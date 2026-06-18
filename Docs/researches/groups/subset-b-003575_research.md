# Research: subset-b-003575

Grouped source research for subset B work item `subset-b-003575`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_gmbus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_gmbus.c

## Purpose
This file implements the GMA500 Intel GMBUS/DDC I2C adapters and a GPIO bit-banged fallback for display probing and control. It creates one Linux `i2c_adapter` per GMBUS pin group, maps those adapters onto either VDC or AUX register space depending on platform, and exposes helpers for speed selection, forced bit-banging, reset, and teardown.

## Important APIs, Types, and Functions
The exported entry points are `gma_intel_i2c_reset()`, `gma_intel_setup_gmbus()`, `gma_intel_gmbus_set_speed()`, `gma_intel_gmbus_force_bit()`, and `gma_intel_teardown_gmbus()`. The local `struct intel_gpio` wraps a bit-banged adapter, GPIO register offset, and `drm_psb_private`. `gmbus_xfer()` is the hardware transfer engine, while `intel_i2c_quirk_xfer()` drives transfers through the GPIO fallback. `intel_gpio_create()` maps GMBUS pins to GPIOA-F registers and registers an `i2c-algo-bit` bus.

## Control Flow
Setup allocates `dev_priv->gmbus`, chooses `dev_priv->gmbus_reg`, registers adapters named by port, programs `reg0` with the port number plus 100 kHz rate, and currently creates a forced bit-bang adapter for each port. Hardware transfer writes `GMBUS0`, emits `GMBUS1` cycles, shuttles data through `GMBUS3`, waits on `GMBUS2` ready/wait/error bits, and clears errors through `GMBUS_SW_CLR_INT`. On timeout it logs the failure, disables GMBUS, creates a GPIO fallback if needed, and retries through bit-banging.

## State and Persistence Behavior
Persistent driver state is in `dev_priv->gmbus`, each `intel_gmbus.reg0`, optional `force_bit` fallback adapters, and `dev_priv->gmbus_reg`. Transfers are synchronous and do not store message data after return. GPIO helpers preserve pull-up-disable bits across line toggles. Teardown unregisters both hardware and fallback adapters and leaves MMIO unmapping to driver unload.

## Dependencies and Integration Points
The code depends on Linux I2C core, `i2c-algo-bit`, DRM device private state, GMBUS/GPIO register definitions from `psb_intel_reg.h`, and register bases established in `psb_drv.c` and chip setup. LVDS, HDMI, SDVO, EDID probing, and BIOS/VBT display setup consume the adapters.

## Risks
The hardware path has short polling timeouts and falls back silently to GPIO, which can mask GMBUS regressions. `gmbus_func()` calls the fallback functionality callback without using its return value. The forced bit-bang default means hardware GMBUS is largely bypassed despite the code path existing. Adapter cleanup must match allocation; forced adapters are allocated separately from the main `dev_priv->gmbus` array.

## Test Signals
Useful signals are successful adapter registration for all GMBUS ports, EDID reads on LVDS/SDVO/HDMI DDC, timeout fallback logs only on unsupported pins, no I2C adapter leaks after unload, and successful suspend/resume display probing with `dev_priv->gmbus_reg` selecting AUX on MRST/Oaktrail and VDC on Poulsbo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_gmbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_i2c.c

## Purpose
This is the older generic GPIO bit-banged I2C implementation used by GMA500 display code. It creates a single `gma_i2c_chan` from a GPIO register, exposes it as a Linux `i2c_adapter`, and provides low-level SCL/SDA callbacks for EDID and panel-control buses.

## Important APIs, Types, and Functions
The exported APIs are `gma_i2c_create()` and `gma_i2c_destroy()`. The callbacks `get_clock()`, `get_data()`, `set_clock()`, and `set_data()` implement `struct i2c_algo_bit_data` over the GPIO register in `chan->reg`. `struct gma_i2c_chan`, declared in `psb_intel_drv.h`, stores the adapter, algorithm data, target address, owning DRM device, and GPIO register.

## Control Flow
Creation allocates the channel, initializes the adapter name/owner/parent, wires `i2c-algo-bit` callbacks, registers the bus with `i2c_bit_add_bus()`, then idles SDA and SCL high. Set callbacks preserve pull-up-disable bits, choose input direction for logical high and output low for logical low, write the GPIO register, and delay for line settling.

## State and Persistence Behavior
The only persistent state is the allocated `gma_i2c_chan` and its registered adapter. The GPIO register is the live hardware state; no transfer data is cached. Destroy unregisters the adapter and frees the channel. Runtime access depends on the caller ensuring display register access is powered when required.

## Dependencies and Integration Points
The file integrates with LVDS DDC and backlight paths in `psb_intel_lvds.c`, with SDVO or other output probing via the shared `gma_i2c_chan` type, and with GPIO definitions and `REG_READ`/`REG_WRITE` macros from `psb_drv.h`/`psb_intel_reg.h`.

## Risks
There is no explicit `gma_power_begin()` around GPIO access here, so callers must avoid using it while MMIO is inaccessible. The function jumps to `out_free` even for allocation failure, which is harmless but makes the error flow less clear. Incorrect GPIO register selection can toggle unrelated pins, and a missing destroy path leaks an adapter.

## Test Signals
Signals include successful `i2c_bit_add_bus()` registration, EDID reads through LVDS DDC, I2C backlight writes on panels with I2C brightness control, stable SCL/SDA idle-high behavior, and clean adapter removal during connector or driver teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.c

## Purpose
This file discovers Moorestown/Oaktrail platform configuration that is not supplied by normal desktop VBT paths. It reads fuse values, SKU/core-clock data, panel type, panel timing, MIPI/LVDS descriptors, and PCI revision data into `drm_psb_private` before display output setup.

## Important APIs, Types, and Functions
The public entry point is `mid_chip_setup()`. `mid_get_fuse_settings()` reads host bridge configuration windows for display type and SKU frequency. `mid_get_pci_revID()` records the graphics root revision. `read_vbt_r0()` and `read_vbt_r10()` map the platform GCT header. `mid_get_vbt_data_r0()`, `_r1()`, and `_r10()` parse different GCT layouts into `dev_priv->gct_data`; `mid_get_vbt_data()` chooses the parser by `$GCT` revision.

## Control Flow
`mid_chip_setup()` runs fuse discovery, GCT/VBT discovery, and revision discovery. Fuse discovery obtains PCI bus 0 device 0, writes magic addresses to config offset `0xD0`, reads through `0xD4`, sets `iLVDS_enable`, `is_lvds_on`, `is_mipi_on`, `video_device_fuse`, `fuse_reg_value`, and `core_freq`. GCT discovery reads config offset `0xFC` from graphics root, maps the header, validates signature, then maps the revision-specific panel table and copies the selected boot panel timing into common `oaktrail_gct_data`.

## State and Persistence Behavior
The file persists platform facts in `drm_psb_private`: selected internal display type, initial LVDS/MIPI power flags, core frequency, fuse values, platform revision, `has_gct`, and `gct_data`. The mapped GCT memory is temporary and unmapped after copies. No firmware data is written except the PCI config address-window setup used for fuse reads.

## Dependencies and Integration Points
It depends on PCI config-space access, `ioremap()` of firmware-provided physical addresses, Oaktrail GCT structures from `oaktrail.h`, and display setup in `oaktrail_device.c` and `oaktrail_lvds.c`. If no GCT is found, Oaktrail setup falls back to OpRegion and normal Intel BIOS parsing.

## Risks
The code trusts several firmware-provided sizes and panel indexes with limited bounds checking, especially GCT revision 0/1 boot panel indexes and revision 1.0 `panel_count`. The comments note missing ioremap-failure checks in older paths. Bad fuse reads can select wrong LVDS/MIPI behavior or core clock, which affects PLL and backlight calculations.

## Test Signals
Boot logs should identify internal LVDS/MIPI selection, SKU/core clock, and GCT revision. Oaktrail LVDS should get a fixed mode from `gct_data` when EDID is absent. Invalid or missing GCT should trigger BIOS fallback without crashing. Core clock values should be 100, 166, or 200 MHz for known SKUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.h

## Purpose
This header exposes the MID platform setup hook used by Oaktrail/Moorestown-specific chip setup. It is intentionally small and keeps MID BIOS/GCT parsing private to `mid_bios.c`.

## Important APIs, Types, and Functions
The only declaration is `int mid_chip_setup(struct drm_device *dev);`, with a forward declaration for `struct drm_device`.

## Control Flow
There is no executable flow. Consumers include this header and call `mid_chip_setup()` during chip initialization before output probing, so display code can rely on fuse, core clock, and GCT state in `drm_psb_private`.

## State and Persistence Behavior
The header owns no state. The called implementation writes state into `drm_psb_private`, notably `core_freq`, display selection flags, `has_gct`, and `gct_data`.

## Dependencies and Integration Points
It integrates `oaktrail_device.c` with `mid_bios.c` while avoiding exposure of the private GCT parser helpers.

## Risks
Because the contract is a single broad setup call, callers cannot distinguish partial success unless the implementation returns errors; the current implementation generally returns `0` after logging problems.

## Test Signals
Build coverage should ensure Oaktrail chip setup resolves `mid_chip_setup()`. Runtime signals are the MID discovery logs and populated platform fields before LVDS/HDMI initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.c

## Purpose
This file implements the PowerVR SGX-side MMU page-directory and page-table manager used by the GMA500 driver. It allocates GPU page directories, maps physical page sequences or page arrays into GPU virtual addresses, invalidates mappings, manages hardware directory contexts, and performs cache/TLB flushes.

## Important APIs, Types, and Functions
The exported APIs are `psb_mmu_driver_init()`, `psb_mmu_driver_takedown()`, `psb_mmu_alloc_pd()`, `psb_mmu_free_pagedir()`, `psb_mmu_get_default_pd()`, `psb_mmu_set_pd_context()`, `psb_mmu_flush()`, `psb_mmu_insert_pfn_sequence()`, `psb_mmu_insert_pages()`, `psb_mmu_remove_pfn_sequence()`, and `psb_mmu_remove_pages()`. Internal helpers compute page-directory/table indexes, construct PTEs, allocate page tables, map/unmap them under lock, and flush PTE cache lines.

## Control Flow
Driver init allocates a default page directory, records BIF control state, clears faults, detects `clflush`, and initializes locking. A page directory allocates a PD page, dummy PT, dummy page, and a 1024-entry software PT pointer table. Insert paths walk the GPU VA range by PDE window, allocate PTs as needed, write PTEs, bump `pt->count`, flush modified PTEs when the PD is bound to hardware, and trigger an MMU flush. Remove paths invalidate PTEs, decrement counts, drop empty PTs, flush modified cache lines, then flush the hardware MMU.

## State and Persistence Behavior
Persistent state lives in `struct psb_mmu_driver` and each `struct psb_mmu_pd`: hardware context number, PD/PT pages, invalid PTE/PDE encodings, default PD, flush flags, saved BIF control, and optional MSVDX invalidation flag. Hardware-visible PD/PT pages are DMA32 pages. The code preserves ordering with a driver rwsem taken before the PT spinlock.

## Dependencies and Integration Points
The MMU is initialized from `psb_drv.c`, populated with stolen memory, and used by GEM/GTT paths. It writes SGX registers `PSB_CR_BIF_CTRL` and `PSB_CR_BIF_DIR_LIST_BASE*` through `PSB_RSGX32`/`PSB_WSGX32`. PTE bit definitions come from `psb_drv.h`; SGX register definitions come from `psb_reg.h`.

## Risks
Reference counts can underflow if remove calls do not match inserted mappings. The code assumes 1024 PDEs and 4 KiB pages. There are subtle cache-flush calculations using CPUID-derived line size and `kmap_atomic`; locking order must remain rwsem before spinlock. Tiled insertion/removal requires `num_pages` to divide by desired stride when `hw_tile_stride` is nonzero.

## Test Signals
Signals include successful driver load with stolen-memory mapping, no SGX MMU faults during modeset/GEM operation, correct cleanup of empty PTs, stable suspend/resume after MMU context rebinding, and no warnings from invalid stride inputs or allocation failures. Hardware TLB/cache flush registers should be touched after bound PD updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.h

## Purpose
This header defines the SGX MMU software state structures and public MMU management API for the GMA500 driver.

## Important APIs, Types, and Functions
Key types are `struct psb_mmu_driver`, `struct psb_mmu_pd`, and `struct psb_mmu_pt`. The driver stores the rwsem/spinlock, flush flags, default PD, saved BIF control, clflush details, and DRM device pointer. A PD stores the hardware context, software PT table, directory page, dummy PT/page, PTE masks, and driver pointer. A PT stores parent PD, index, present-entry count, backing page, and temporary mapped virtual address. Function declarations mirror the implementation’s init/takedown, allocation/free, context binding, insert/remove, and flush APIs.

## Control Flow
There is no executable flow. The declarations define the sequence used by driver load: initialize driver, allocate optional pagefault PD, bind contexts, insert mappings, flush, then free on unload.

## State and Persistence Behavior
The structs are long-lived kernel driver state and contain both software-only pointers and hardware-visible page backing. Comments document the required lock ordering: take `psb_mmu_driver.sem` before the page-table spinlock.

## Dependencies and Integration Points
The header is included by `psb_drv.h`, `mmu.c`, and other GMA500 memory-management code. It depends on DRM device, page, semaphore, spinlock, and atomic types being available through included kernel headers.

## Risks
External code can directly inspect or misuse MMU internals because the structs are fully exposed. Violating the documented lock order or editing PT `count` outside the provided APIs can corrupt mappings or deadlock.

## Test Signals
Build-time consumers should resolve all MMU APIs, and lockdep/runtime testing should show no inversion between `sem` and `lock`. Mapping tests should observe state transitions through the exported functions rather than direct struct mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail.h

## Purpose
This header collects Oaktrail/Moorestown-specific panel data structures and HDMI function declarations. It defines the GCT panel timing/descriptors consumed by MID BIOS parsing and the HDMI device state saved across modeset and suspend/resume.

## Important APIs, Types, and Functions
Important data types include `struct oaktrail_timing_info`, `struct gct_r10_timing_info`, `struct oaktrail_panel_descriptor_v1`, `struct oaktrail_panel_descriptor_v2`, `union oaktrail_panel_rx`, `struct gct_r0`, `struct gct_r1`, `struct gct_r10`, `struct oaktrail_gct_data`, and `struct oaktrail_hdmi_dev`. It also declares Oaktrail HDMI setup/teardown/save/restore/init, HDMI I2C init/exit, and CRTC HDMI mode-set/DPMS helpers.

## Control Flow
There is no executable flow. The structs shape how `mid_bios.c` copies firmware GCT data and how `oaktrail_device.c`, `oaktrail_lvds.c`, `oaktrail_hdmi.c`, and `oaktrail_hdmi_i2c.c` share Oaktrail-specific state.

## State and Persistence Behavior
`oaktrail_gct_data` is embedded in `drm_psb_private` and persists selected panel timing/descriptor data after firmware tables are unmapped. `oaktrail_hdmi_dev` is allocated when the HDMI PCI function is found and stores MMIO mapping, DPMS mode, HDMI I2C state, and register snapshots.

## Dependencies and Integration Points
The header integrates MID firmware parsing, LVDS fixed-mode generation, Oaktrail chip operations, and separate HDMI PCI controller handling. It depends on DRM mode types, PCI device types, and register definitions indirectly through implementation files.

## Risks
The packed bitfield layouts are firmware ABI contracts; compiler layout and endian assumptions must match the platform. GCT revision variants use similar but not identical timing layouts, so copying fields incorrectly can produce bad panel modes. HDMI state is shared between display and I2C files through an opaque `hdmi_i2c_dev` pointer.

## Test Signals
Signals include correct compile-time struct packing, GCT-derived LVDS modes matching panel native resolution, HDMI setup resolving all declarations, and suspend/resume preserving the register fields listed in `oaktrail_hdmi_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_crtc.c

## Purpose
This file supplies Oaktrail/Moorestown CRTC helper operations for non-HDMI and HDMI-routed pipes. It computes Oaktrail PLL settings, programs pipe timings and planes, handles DPMS power sequencing, panel fitter decisions, FIFO watermark programming, and framebuffer base updates.

## Important APIs, Types, and Functions
The exported object is `oaktrail_helper_funcs`. Main functions are `oaktrail_crtc_dpms()`, `oaktrail_crtc_mode_set()`, and `oaktrail_pipe_set_base()`. PLL helpers include `mrst_limit()`, `mrst_lvds_clock()`, `mrst_sdvo_find_best_pll()`, and `mrst_lvds_find_best_pll()`. Limit tables encode different LVDS SKU frequencies and SDVO constraints.

## Control Flow
DPMS routes HDMI CRTCs to `oaktrail_crtc_hdmi_dpms()`. For LVDS/SDVO it powers the display, enables or disables DPLL, pipe, and plane registers, waits for vblank/stabilization, and writes fixed FIFO watermark values. Mode set discovers attached encoder type, disables VGA and panel fitter, writes timing registers, handles no-scale centering by adjusting blank/sync windows, calls `mode_set_base()`, computes PLL values from core or SDVO ref clock, writes FP/DPLL/pipe/plane registers across primary and AUX register windows when needed, then releases power.

## State and Persistence Behavior
The file updates CRTC saved modes, hardware timing/PLL/plane registers, and framebuffer base/surface registers. It uses `gma_power_begin()`/`gma_power_end()` for MMIO access. It does not allocate long-lived state, relying on `gma_crtc`, `drm_psb_private.regmap`, and framebuffer GEM offsets.

## Dependencies and Integration Points
It integrates with DRM CRTC helper callbacks, `gma_display` helpers, GEM framebuffer objects, Oaktrail HDMI CRTC helpers, LVDS/SDVO encoder type discovery, and register maps from `oaktrail_device.c`. PLL decisions depend on `dev_priv->core_freq` populated by MID fuse setup.

## Risks
PLL programming depends on SKU-derived core frequency and hardcoded conversion tables; a bad `core_freq` causes wrong clocks. `need_aux` mirrors writes to AUX for SDVO and must align with platform register mapping. DPMS and mode set perform direct register polling with fixed delays. Framebuffer offset programming assumes `to_psb_gem_object(fb->obj[0])->offset` is valid and already bound.

## Test Signals
Test by setting LVDS and SDVO modes at multiple clocks, checking no-scale/aspect/fullscreen behavior, verifying pipe/plane disable/enable sequencing on DPMS, observing stable FIFO watermarks, and confirming framebuffer panning/base updates without corruption or power-management failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_device.c

## Purpose
This file defines the Oaktrail chipset personality for the shared GMA500 driver. It wires output initialization, backlight control, display save/restore, display-island power gating, register maps, chip setup/teardown, and the `psb_ops` table selected by Oaktrail PCI IDs.

## Important APIs, Types, and Functions
The externally consumed object is `oaktrail_chip_ops`. Important functions include `oaktrail_output_init()`, `oaktrail_backlight_init()`, `oaktrail_set_brightness()`, `oaktrail_save_display_registers()`, `oaktrail_restore_display_registers()`, `oaktrail_power_down()`, `oaktrail_power_up()`, `oaktrail_chip_setup()`, and `oaktrail_teardown()`. `oaktrail_regmap` maps pipe A/B abstract offsets to hardware registers.

## Control Flow
Chip setup enables MSI, installs the Oaktrail register map, runs MID chip setup, falls back to OpRegion/VBT when no GCT exists, initializes GMBUS, and probes HDMI hardware. Output init creates LVDS if fuses say LVDS, logs unsupported DSI otherwise, creates HDMI if present, and initializes SDVO. Suspend save captures watermarks, pipe A, cursor, palette, HDMI state, LVDS/panel/backlight, overlay, and DPST registers, then shuts down LVDS hardware. Restore writes the saved registers back in hardware-safe order.

## State and Persistence Behavior
The file persists saved hardware state in `dev_priv->regs`, HDMI state in `dev_priv->hdmi_priv`, backlight adjustment percentages, and `dev_priv->regmap`. Power gating uses OSPM I/O ports derived by `gma_power_init()`. Backlight state is written to `BLC_PWM_CTL*` and adjusted by `blc_adj1`/`blc_adj2`.

## Dependencies and Integration Points
It depends on MID BIOS discovery, Intel BIOS/OpRegion parsing, GMBUS, HDMI, LVDS, SDVO, power management, and register definitions. `psb_drv.c` selects `oaktrail_chip_ops` for the 0x4100 family and calls these hooks during load, suspend/resume, modeset, and unload.

## Risks
Power-up/down loops poll forever without timeout. Backlight PWM calculations depend on `core_freq`; a missing/zero core clock can break setup. Save/restore order is hardware-sensitive and mixes VDC and HDMI controller state. DSI is explicitly unsupported, so systems fused for MIPI will log an error and have no internal panel.

## Test Signals
Signals include Oaktrail probe selecting this ops table, successful GCT or BIOS fallback, registered LVDS/HDMI/SDVO connectors as expected, backlight init and brightness changes, suspend/resume preserving panel state, and display-island power transitions completing without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi.c

## Purpose
This file implements Oaktrail HDMI support for the separate HDMI PCI controller. It handles HDMI device discovery/MMIO mapping, TMDS connector/encoder registration, HDMI PLL and pipe-B mode programming, audio enable/disable, hotplug detection, EDID mode reporting, DPMS, and HDMI register save/restore.

## Important APIs, Types, and Functions
Exported functions are `oaktrail_hdmi_setup()`, `oaktrail_hdmi_teardown()`, `oaktrail_hdmi_init()`, `oaktrail_crtc_hdmi_mode_set()`, `oaktrail_crtc_hdmi_dpms()`, `oaktrail_hdmi_save()`, and `oaktrail_hdmi_restore()`. Internal helpers include `oaktrail_hdmi_find_dpll()`, `oaktrail_hdmi_reset()`, `scu_busy_loop()`, `oaktrail_hdmi_detect()`, `oaktrail_hdmi_get_modes()`, and audio toggles.

## Control Flow
Setup locates PCI device 8086:080d, enables it, maps BAR0, initializes the HDMI I2C controller, stores `dev_priv->hdmi_priv`, and disables audio. Connector init creates a DVID connector and TMDS encoder. HDMI CRTC mode set powers the device, disables VGA/DPLL, resets the controller through SCU IPC MMIO, computes DPLL divisors from a 25 MHz ref clock, programs both core and PCH-style pipe-B timings, calls base programming, enables pipe/plane, and waits for vblank. DPMS toggles DPLL, pipe B, PCH pipe B, and plane B.

## State and Persistence Behavior
Persistent state is `struct oaktrail_hdmi_dev`: PCI device, MMIO mapping, I2C device, and saved DPLL/pipe/plane/PCH registers. `oaktrail_hdmi_dpms()` also keeps a static last DPMS mode. Save/restore copies pipe B timing, plane, cursor, palette, and HDMI DPLL/PCH state into driver-private structures.

## Dependencies and Integration Points
The file integrates with Oaktrail chip setup, Oaktrail CRTC helpers, HDMI I2C init/exit, DRM connector helpers, DRM EDID helpers, and GMA500 power/register macros. It uses hardcoded SCU IPC and HDMI MMIO offsets specific to this platform.

## Risks
EDID support is incomplete and currently uses a hardcoded raw EDID even if adapter 3 exists. SCU reset uses fixed physical addresses and magic values. HDMI mode set forces pipe B and contains many hardware constants. `oaktrail_hdmi_destroy()` is empty, so connector cleanup relies on broader DRM teardown. DPMS register access lacks an explicit power wrapper in the CRTC DPMS helper.

## Test Signals
Signals include detecting the HDMI PCI function, successful BAR mapping and I2C IRQ registration, hotplug status changing with `HDMI_HSR`, valid modes from the fallback EDID, stable HDMI output at 20-165 MHz pixel clocks, audio enable during mode set, and correct HDMI register restoration after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi_i2c.c

## Purpose
This file provides the Oaktrail HDMI controller’s hardware I2C/DDC adapter. It configures GPIO muxing for HDMI I2C, registers fixed-number adapter 3, drives EDID read transactions through HDMI registers, and services controller interrupts for read-buffer-full and transaction-done events.

## Important APIs, Types, and Functions
The exported APIs are `oaktrail_hdmi_i2c_init()` and `oaktrail_hdmi_i2c_exit()`. `struct hdmi_i2c_dev` stores the adapter pointer, mutex, completion, status, active message, and buffer offset. Transfer logic is in `oaktrail_hdmi_i2c_access()`, `xfer_read()`, `xfer_write()`, `hdmi_i2c_read()`, `hdmi_i2c_transaction_done()`, and `oaktrail_hdmi_i2c_handler()`.

## Control Flow
Init allocates `hdmi_i2c_dev`, binds a static `i2c_adapter` to the HDMI device, configures GPIO pins 52/53 to alternate function 2, requests the HDMI IRQ, and registers adapter number 3. Transfers take a mutex, enable the I2C unit and IRQs, run each message as read or no-op write, then disable IRQs. Reads program `HDMI_HI2CHCR`; the interrupt handler copies 64-byte chunks from read buffer registers and clears/continues transactions until done.

## State and Persistence Behavior
State persists in `hdmi_dev->i2c_dev` and the static numbered adapter. Each transfer stores the current `i2c_msg`, buffer offset, and status until completion. The driver uses completions for IRQ wakeup but does not keep EDID data after the caller’s buffer is filled. Exit deletes the adapter, frees state, and releases the shared IRQ.

## Dependencies and Integration Points
This integrates with `oaktrail_hdmi_setup()` and the HDMI connector’s EDID path. It depends on PCI driver data pointing to `oaktrail_hdmi_dev`, Linux I2C core, IRQ handling, HDMI MMIO registers, and hardcoded GPIO controller MMIO for pin muxing.

## Risks
`xfer_read()` waits in a loop without checking the timeout return or signal interruption, so a failed interrupt can spin in repeated timed waits. `hdmi_i2c_read()` always copies 64 bytes per full interrupt and can overrun a short message buffer if hardware delivers more than requested. Writes are stubbed out. The static adapter with fixed `.nr = 3` can conflict if another adapter already owns that number.

## Test Signals
Signals include successful GPIO mux write, IRQ request, numbered adapter registration, EDID reads without buffer corruption, interrupt status clearing for FULL/DONE/HPD, clean adapter/IRQ removal, and no hangs when a display is disconnected or the HDMI controller fails to signal completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds.c

## Purpose
This file implements the Oaktrail LVDS connector/encoder path. It powers the panel, programs LVDS and panel-fitter registers, discovers a fixed panel mode from EDID/GCT/VBT, attaches scaling and backlight properties, and wires Oaktrail-specific encoder helpers.

## Important APIs, Types, and Functions
The exported API is `oaktrail_lvds_init()`. Important helpers are `oaktrail_lvds_set_power()`, `oaktrail_lvds_dpms()`, `oaktrail_lvds_mode_set()`, `oaktrail_lvds_prepare()`, `oaktrail_lvds_commit()`, `oaktrail_lvds_get_max_backlight()`, and `oaktrail_lvds_get_configuration_mode()`. It reuses connector funcs from `psb_intel_lvds.c` and mode fixup from `psb_intel_lvds_mode_fixup()`.

## Control Flow
Initialization allocates encoder and connector objects, initializes a LVDS connector and encoder, attaches scaling/backlight properties, derives dither preference from GCT or driver flags, then probes EDID. It first tries the chip ops I2C bus, then an LPC GPIO bit-banged bus if available, assigns `connector->ddc`, and stores a preferred mode from EDID. If EDID is unavailable, it builds a mode from GCT timing, then VBT fallback modes. Prepare saves backlight PWM and powers the panel down; commit restores power and brightness.

## State and Persistence Behavior
Persistent state is in `mode_dev->panel_fixed_mode`, `mode_dev->panel_wants_dither`, `mode_dev->backlight_duty_cycle`, connector DDC pointer, and `dev_priv->is_lvds_on`. Panel power changes update `PP_CONTROL`, wait on `PP_STATUS`, and optionally call a chip-specific LVDS backlight power hook.

## Dependencies and Integration Points
It depends on MID GCT data from `mid_bios.c`, generic LVDS connector funcs in `psb_intel_lvds.c`, LPC I2C from `oaktrail_lvds_i2c.c`, GMA power helpers, DRM EDID helpers, and mode properties from DRM core.

## Risks
If EDID is unavailable and GCT/VBT data is bad, the panel mode will be wrong. The code sets `connector->ddc` manually after probing because the adapter may be discovered late. Error paths must release the optional LPC DDC bus or I2C adapter correctly. Power loops wait indefinitely on panel status bits.

## Test Signals
Signals include LVDS connector registration only when fused for LVDS, preferred mode from EDID or GCT, correct scaling property behavior, dither bit programming when requested, backlight/panel power toggles on DPMS, and no leaks in failed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds_i2c.c

## Purpose
This file implements an LPC GPIO bit-banged I2C bus for LVDS DDC on Atom E6xx/Oaktrail systems. It is used when normal GMBUS/DDC probing is unavailable but an LPC GPIO base was discovered.

## Important APIs, Types, and Functions
The exported function is `oaktrail_lvds_i2c_init()`. Local callbacks `get_clock()`, `get_data()`, `set_clock()`, and `set_data()` implement `i2c-algo-bit` using LPC GPIO registers. Register offsets include `RGIO` and `RGLVL`; line masks are `GPIO_CLOCK` and `GPIO_DATA`.

## Control Flow
Initialization allocates a `gma_i2c_chan`, points `chan->reg` at `dev_priv->lpc_gpio_base`, sets adapter metadata and bit-bang callbacks, idles SDA/SCL high, delays, and registers the bus. Get callbacks set the corresponding GPIO to input in `RGIO` and read `RGLVL`. Set callbacks choose input/high or output/low by modifying `RGIO` and `RGLVL`.

## State and Persistence Behavior
The created `gma_i2c_chan` and Linux adapter persist until the caller destroys them with `gma_i2c_destroy()`. The file does not keep global state. Hardware state is the LPC GPIO direction and level registers.

## Dependencies and Integration Points
It is called from `oaktrail_lvds_init()` as a fallback DDC bus. It depends on `dev_priv->lpc_gpio_base` being discovered in `psb_driver_load()` from PCI device 31:0 and on Linux I2C bit-banging.

## Risks
The bus directly performs `inl`/`outl` on LPC I/O ports; a wrong base can touch unrelated hardware. The adapter has a slower 100 usec bit delay, which may affect probing time. Cleanup responsibility sits with the LVDS caller, so early returns must destroy the bus.

## Test Signals
Signals include EDID reads succeeding on systems with LPC GPIO DDC, correct SCL/SDA idle-high behavior, no I/O port faults, and bus cleanup when LVDS probe fails or the connector is destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.c

## Purpose
This file implements Intel graphics OpRegion support for GMA500. It maps the ACPI OpRegion, exposes ACPI/ASLE mailboxes, acknowledges ACPI video notifications, and handles ASLE backlight requests from firmware.

## Important APIs, Types, and Functions
Public functions are `psb_intel_opregion_setup()`, `psb_intel_opregion_init()`, `psb_intel_opregion_fini()`, `psb_intel_opregion_enable_asle()`, and `psb_intel_opregion_asle_intr()`. Local ABI structs model the OpRegion header, ACPI mailbox, SWSCI placeholder, and ASLE mailbox. `asle_set_backlight()` translates ASLE brightness to `gma_backlight_set()`, and `psb_intel_opregion_asle_work()` services ASLE requests.

## Control Flow
Setup reads PCI config `ASLS`, maps 8 KiB with `acpi_os_ioremap()`, validates the `"IntelGraphicsMem"` signature, records header/VBT/lid pointers, and attaches ACPI/ASLE mailbox pointers based on header mailbox bits. Init sets ACPI driver-ready flags and registers an ACPI notifier. ASLE interrupts schedule work, which checks command bits and handles supported backlight updates. Fini clears readiness, unregisters the notifier, cancels work, and unmaps the OpRegion.

## State and Persistence Behavior
Mapped OpRegion pointers live in `dev_priv->opregion`; `system_opregion` is a global pointer used by the ACPI notifier. ASLE work is deferred through `opregion.asle_work`. The code writes firmware-visible readiness/status/brightness fields such as `drdy`, `csts`, `ardy`, `tche`, `aslc`, and `cblv`.

## Dependencies and Integration Points
It integrates with ACPI, PCI config space, DRM debug logging, GMA interrupt handling (`psb_intel_opregion_asle_intr()`), pipe status enabling, and backlight control. BIOS parsing can also consume `opregion.vbt`.

## Risks
Only ASLE backlight is implemented; ALS, panel fitting, and PWM frequency requests are advertised but not serviced. `system_opregion` assumes one relevant device. Duplicate macro definitions make maintenance noisy. Mapping and mailbox offsets must match firmware exactly. ASLE enable is skipped on non-PC-like Medfield behavior only by comments and the `system_opregion` condition.

## Test Signals
Signals include valid OpRegion signature detection, ACPI mailbox readiness flags set/cleared on init/fini, ACPI video notifier acknowledgments, ASLE backlight requests changing brightness and updating `cblv`, and clean unmap/cancel-work during unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.h

## Purpose
This header provides the OpRegion function declarations and no-op fallbacks when ACPI support is disabled.

## Important APIs, Types, and Functions
When `CONFIG_ACPI` is enabled it declares `psb_intel_opregion_asle_intr()`, `psb_intel_opregion_init()`, `psb_intel_opregion_fini()`, `psb_intel_opregion_setup()`, and `psb_intel_opregion_enable_asle()`. Without ACPI it supplies inline stubs; setup returns `0` and all other functions do nothing.

## Control Flow
There is no runtime flow in the enabled-declaration case. In non-ACPI builds, callers execute local stubs so driver load/unload paths can remain unconditional.

## State and Persistence Behavior
The header has no state. In ACPI builds the implementation stores mapped OpRegion pointers in `drm_psb_private`; in non-ACPI builds no OpRegion state is created.

## Dependencies and Integration Points
The header lets `psb_drv.c`, `psb_device.c`, and `oaktrail_device.c` call OpRegion setup/init/fini/ASLE helpers without preprocessor branches.

## Risks
The non-ACPI `psb_intel_opregion_setup()` returning success can hide absence of OpRegion functionality from callers. The inline stubs are declared `extern inline`, which can be sensitive to compiler inline semantics.

## Test Signals
Build both ACPI and non-ACPI configurations. ACPI builds should link to `opregion.c`; non-ACPI builds should load without unresolved symbols and simply skip OpRegion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.c

## Purpose
This file centralizes GMA500 display power management. It initializes runtime PM, saves/restores display and PCI state during suspend/resume, rebuilds GTT/GEM mappings after resume, installs/uninstalls IRQs around suspend, and provides `gma_power_begin()`/`gma_power_end()` wrappers for hardware register access.

## Important APIs, Types, and Functions
Public APIs are `gma_power_init()`, `gma_power_uninit()`, `gma_power_suspend()`, `gma_power_resume()`, `gma_power_begin()`, and `gma_power_end()`. Internal helpers are `gma_suspend_display()`, `gma_resume_display()`, `gma_suspend_pci()`, and `gma_resume_pci()`.

## Control Flow
Init computes APM/OSPM I/O bases, calls optional chip PM init, takes a runtime PM reference to keep the device awake, and marks PM initialized. System suspend uninstalls IRQs, calls chip save/power-down hooks, saves PCI state plus BSM/VBT config values, disables the PCI device, and enters D3hot. Resume restores PCI power/config, powers up the display island, restores page table/GTT control, rebuilds GTT/GEM memory manager state, calls chip restore hooks, and reinstalls IRQs.

## State and Persistence Behavior
Saved PCI config values are stored in `dev_priv->regs.saveBSM` and `saveVBT`; display state is delegated to chip-specific save hooks. Runtime PM references are held/released by init/uninit and begin/end. `pm_initialized` gates uninit.

## Dependencies and Integration Points
It depends on chip ops (`init_pm`, `save_regs`, `restore_regs`, `power_down`, `power_up`), PCI PM, runtime PM, IRQ helpers, GTT/GEM resume, and register definitions for page table and GMCH control. All display register users should wrap access with `gma_power_begin()`.

## Risks
The comment states runtime PM support is broken and keeps the device permanently referenced, so power saving is limited. `gma_power_begin(false)` fails if the device is suspended; callers must handle cache-only paths. `gma_resume_pci()` return is ignored by `gma_power_resume()`. Suspend/resume order is hardware-sensitive.

## Test Signals
Signals include successful system suspend/resume with restored modes, IRQs reinstalled, GTT/GEM mappings rebuilt, no register access while power is off, balanced runtime PM references, and stable behavior for callers using forced and opportunistic `gma_power_begin()` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.h

## Purpose
This header declares the GMA500 power-management interface used by driver load/unload, PCI PM callbacks, and register-access wrappers.

## Important APIs, Types, and Functions
It declares `gma_power_init()`, `gma_power_uninit()`, `gma_power_suspend()`, `gma_power_resume()`, `gma_power_begin()`, and `gma_power_end()`, with forward declarations for `struct device` and `struct drm_device`.

## Control Flow
There is no executable flow. The declared API supports a lifecycle of init, repeated begin/end guarded MMIO access, suspend/resume callbacks, and uninit.

## State and Persistence Behavior
The header owns no state. Implementations mutate runtime PM references, saved PCI/display state, and `drm_psb_private.pm_initialized`.

## Dependencies and Integration Points
It is included by display, LVDS, backlight, CRTC, and driver-core files that need power-safe hardware access. The suspend/resume declarations are used in the PCI driver PM ops.

## Risks
Callers must balance `gma_power_begin()` with `gma_power_end()` only when begin succeeds. Misuse can leak runtime PM references or access powered-down hardware.

## Test Signals
Build should verify all users see the declarations. Runtime test signals are balanced PM refs and absence of MMIO faults in callers using the wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.c

## Purpose
This file defines the Poulsbo/GMA500 chipset personality. It wires output initialization, PWM backlight setup, SGX clock-gating initialization, generic display save/restore hooks, register maps, and the `psb_chip_ops` table selected for Poulsbo PCI IDs.

## Important APIs, Types, and Functions
The exported object is `psb_chip_ops`. Important functions are `psb_output_init()`, `psb_backlight_setup()`, `psb_init_pm()`, `psb_save_display_registers()`, `psb_restore_display_registers()`, `psb_power_down()`, `psb_power_up()`, `psb_chip_setup()`, and `psb_chip_teardown()`. `psb_regmap` maps abstract pipe offsets to Poulsbo registers.

## Control Flow
Chip setup selects the register map, discovers core frequency, initializes GMBUS, initializes OpRegion, and parses Intel BIOS data. Output init creates LVDS and SDVO outputs. Backlight setup derives the PWM register period from VBT backlight frequency and core clock, validates bounds, writes `BLC_PWM_CTL`, and sets full brightness. Save/restore locks modeset state, saves shared watermark registers, then delegates CRTC and connector save/restore callbacks.

## State and Persistence Behavior
Persistent state includes `dev_priv->regmap`, VBT-derived `lvds_bl`, saved watermark registers, connector/CRTC save areas, and `BLC_PWM_CTL`. Poulsbo power-up/down hooks are no-ops, unlike Oaktrail display-island gating.

## Dependencies and Integration Points
It integrates with `psb_drv.c` through `psb_ops`, with `psb_intel_display.c` for CRTC helpers, with `psb_intel_lvds.c` for LVDS/backlight, with SDVO output init, GMBUS, OpRegion, and Intel BIOS parsing.

## Risks
Backlight setup depends on valid VBT backlight data; missing or out-of-range values abort setup. Display save/restore assumes connector save callbacks are correctly installed. `psb_chip_teardown()` only tears down GMBUS, while BIOS/OpRegion cleanup is handled elsewhere, so lifecycle ownership is split.

## Test Signals
Signals include Poulsbo PCI IDs selecting `psb_chip_ops`, LVDS/SDVO connectors appearing, PWM backlight initialized from VBT, modes surviving suspend/resume through connector/CRTC save callbacks, and no regressions in SGX clock gating initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.h

## Purpose
This header exposes Poulsbo-specific clock functions to the shared GMA500 driver.

## Important APIs, Types, and Functions
It declares `extern const struct gma_clock_funcs psb_clock_funcs;`, implemented in `psb_intel_display.c`.

## Control Flow
There is no executable flow. Poulsbo chip ops reference this clock-function table so CRTC mode setting can compute PLL values.

## State and Persistence Behavior
The header has no state. The referenced object is static runtime dispatch metadata.

## Dependencies and Integration Points
It connects `psb_device.c` to `psb_intel_display.c` without pulling in broader implementation details.

## Risks
If `psb_clock_funcs` is changed or removed, Poulsbo mode setting will fail to link or lack PLL helpers.

## Test Signals
Build coverage for Poulsbo ops and successful mode setting using `psb_clock_funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.c

## Purpose
This is the main PCI/DRM driver entry point for GMA500/GMA600/GMA3600/GMA3650. It matches PCI IDs to chip ops, removes conflicting firmware framebuffers, allocates the DRM device/private state, maps MMIO resources, initializes chip/memory/display/IRQ subsystems, registers with DRM, and tears everything down on remove.

## Important APIs, Types, and Functions
Important functions are `psb_pci_probe()`, `psb_driver_load()`, `psb_driver_unload()`, `psb_device_release()`, `psb_do_init()`, `psb_spank()`, `gma_remove_conflicting_framebuffers()`, `psb_pci_remove()`, `psb_init()`, and `psb_exit()`. Key objects are `pciidlist`, `psb_gem_fops`, the `drm_driver`, and the `pci_driver`.

## Control Flow
Probe removes firmware devices, enables PCI, allocates `drm_psb_private`, stores drvdata, calls `psb_driver_load()`, registers DRM, and starts DRM clients. Load maps VDC/SGX/AUX/LPC resources, sets up OpRegion and chip ops, initializes power, scratch page, GTT, GEM MM, SGX MMU/page directories, soft-resets SGX, maps stolen memory into the SGX MMU, binds PD contexts, registers ACPI video, initializes vblank/IRQs/modeset/polling, then enables backlight and ASLE if an internal panel exists.

## State and Persistence Behavior
Driver-private state spans PCI resource mappings, chip ops, GTT/GEM/MMU state, stolen memory, scratch page cache attributes, IRQ masks, register save areas, OpRegion, backlight, modeset objects, and platform-specific aux/LPC devices. Unload reverses backlight, modeset, IRQ, chip, OpRegion, MMU, GEM, GTT, page/cache, MMIO, PCI references, BIOS, and power initialization.

## Dependencies and Integration Points
This file integrates nearly every local subsystem: GTT, GEM, MMU, chip ops for PSB/Oaktrail/CDV, power, IRQ, framebuffer helpers, Intel BIOS, OpRegion, ACPI video, DRM core, PCI, and aperture conflict removal.

## Risks
Load error paths are broad and rely on `psb_driver_unload()` tolerating partially initialized state. Some failures after setup return directly instead of going through `out_err`. The driver keeps runtime PM awake by design. AUX fallback can point `aux_reg` at `vdc_reg`; unload must avoid double-unmap semantics. Hardware init uses magic SGX reset and base registers.

## Test Signals
Signals include PCI ID matching for all families, no firmware framebuffer conflict, successful DRM registration, initialized vblank/IRQ/modeset/backlight, SGX MMU stolen-memory mapping, clean remove/unload after partial and full probes, and suspend/resume callbacks through `psb_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.h

## Purpose
This is the central private header for the GMA500 driver. It defines driver identity, platform detection macros, MMIO/resource constants, SGX MMU bit definitions, IRQ/register constants, key private structures, chip operation dispatch, subsystem prototypes, and register access helpers.

## Important APIs, Types, and Functions
Core types include `struct psb_intel_opregion`, `struct sdvo_device_mapping`, `struct intel_gmbus`, `struct psb_offset`, `struct psb_pipe`, `struct psb_state`, `struct cdv_state`, `struct psb_save_area`, `struct drm_psb_private`, and `struct psb_ops`. It declares modeset, backlight, GEM, chip ops, CRTC/helper, LVDS, and utility APIs. Inline helpers/macros include `to_drm_psb_private()`, `REG_READ/WRITE`, AUX variants, SGX/VDC read/write macros, and platform tests `IS_PSB`, `IS_MRST`, `IS_CDV`.

## Control Flow
There is no executable driver flow, but the header defines dispatch tables that shape runtime flow. `psb_drv.c` chooses a `psb_ops` implementation, then calls its setup/output/backlight/save/restore/power callbacks while display files use the shared register map and private state.

## State and Persistence Behavior
`drm_psb_private` is the persistent driver state container. It owns PCI resource references, GTT/GEM/MMU state, mapped register bases, IRQ masks, modeset mappings, GMBUS, LVDS/VBT/GCT data, HDMI state, saved registers, OpRegion, power/backlight state, and platform flags. `psb_save_area` stores suspend/resume register snapshots.

## Dependencies and Integration Points
The header includes GTT, BIOS, MMU, Oaktrail, OpRegion, power, Intel display, and register headers. It is shared across almost every GMA500 implementation file and therefore forms the integration contract between PCI core, memory management, display, output, power, and ACPI paths.

## Risks
Because it exposes many internals and macros, changes can have wide blast radius. Register macros assume a local `dev` or `dev_priv` variable name. `PSB_WMSVDX32` references `msvdx_reg`, which is not visible in the shown private struct and may be legacy/dead for this tree. Platform detection depends on PCI device ID bit masks.

## Test Signals
Signals include all GMA500 source files compiling with this header, correct chip-op selection by platform macros, valid register access through VDC/AUX/SGX mappings, and no struct-layout regressions affecting suspend/resume or output setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_display.c

## Purpose
This file provides Poulsbo-style CRTC mode setting, PLL helpers, mode readback, CRTC initialization, cursor setup, and connector-clone helpers for the shared GMA500 modeset stack.

## Important APIs, Types, and Functions
Exported objects/functions are `psb_intel_helper_funcs`, `psb_clock_funcs`, `psb_intel_crtc_mode_get()`, `psb_intel_crtc_init()`, `psb_intel_get_crtc_from_pipe()`, and `gma_connector_clones()`. Local helpers include `psb_intel_limit()`, `psb_intel_clock()`, `psb_intel_panel_fitter_pipe()`, `psb_intel_crtc_mode_set()`, `psb_intel_crtc_clock_get()`, and `psb_intel_cursor_init()`.

## Control Flow
CRTC mode set validates a framebuffer, discovers attached encoder type, selects a PLL limit, computes PLL divisors, programs LVDS pins before DPLL when needed, writes timing/source/plane registers, calls base programming, and waits for vblank. Mode readback pulls timing and PLL registers from live hardware or saved state when powered down. CRTC init allocates `gma_crtc` plus connector storage, initializes DRM CRTC and gamma, attaches chip helper functions, records pipe/plane mappings, and initializes cursor registers and optional stolen-memory cursor backing.

## State and Persistence Behavior
The file persists per-CRTC state in `gma_crtc`, `psb_intel_crtc_state`, `dev_priv->plane_to_crtc_mapping`, `pipe_to_crtc_mapping`, cursor GEM object/address, LUT adjustment, and saved modes. It writes live hardware timing/PLL/plane/cursor registers through `dev_priv->regmap`.

## Dependencies and Integration Points
It depends on DRM CRTC helpers, GEM framebuffer objects, generic GMA display helpers, Poulsbo register maps from `psb_device.c`, LVDS/SDVO encoder types, and clock helper callbacks. Chip ops point to `psb_intel_helper_funcs` and `psb_clock_funcs`.

## Risks
PLL selection returns without applying a mode if it cannot find settings but only logs. LVDS pipe restrictions are enforced in LVDS mode fixup, not here. Cursor allocation for platforms requiring physical cursor memory can fail, leaving cursor disabled. Mode readback mixes live and saved register paths depending on runtime power.

## Test Signals
Signals include successful CRTC creation for all configured pipes, correct PLL programming for LVDS/SDVO modes, mode readback matching active modes, cursor registers initialized to zero, framebuffer base updates via `gma_pipe_set_base()`, and clone masks matching connector types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_drv.h

## Purpose
This header defines the shared Intel-style display abstractions used by GMA500 output, CRTC, connector, and I2C code. It bridges DRM core objects to GMA500-specific encoder/connector/CRTC/private mode state.

## Important APIs, Types, and Functions
Important definitions include output type constants, clone bits, `INTELFB_CONN_LIMIT`, `struct psb_intel_mode_device`, `struct gma_i2c_chan`, `struct gma_encoder`, `struct gma_connector`, `struct psb_intel_crtc_state`, and `struct gma_crtc`. It provides container macros and declarations for I2C creation, DDC modes, CRTC init/readback, SDVO/LVDS/Oaktrail LVDS, best encoder, connector attachment, LVDS property/mode helpers, GMBUS helpers, and CDV DP/audio/color property helpers.

## Control Flow
There is no executable flow. Runtime display flow uses these structs to attach encoders to connectors, map outputs to CRTCs, preserve panel fixed modes, and dispatch helper callbacks.

## State and Persistence Behavior
The declared structs persist display state: panel fixed modes and backlight duty in `psb_intel_mode_device`, GPIO I2C bus data in `gma_i2c_chan`, output type/private pointers in `gma_encoder`, save/restore callbacks in `gma_connector`, and pipe/cursor/LUT/modes/page-flip state in `gma_crtc`.

## Dependencies and Integration Points
It depends on Linux I2C, DRM CRTC/encoder/probe/vblank headers, and `gma_display.h`. It is included by display, LVDS, SDVO, HDMI, I2C, and core driver code.

## Risks
The header exposes output internals broadly, so ownership of fields such as `connector->ddc`, `gma_encoder->dev_priv`, and `lvds_i2c_bus` must be consistent across output implementations. Some comments note legacy or FIXME areas, including shared SDVO/LVDS I2C ownership and display-private placement.

## Test Signals
Build coverage across all output implementations, correct connector-to-encoder attachment, valid container macro usage, mode device fixed-mode propagation, and successful GMBUS/I2C/LVDS/SDVO/HDMI integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_lvds.c

## Purpose
This file implements the generic Poulsbo LVDS connector and encoder path. It handles LVDS panel/backlight power, I2C or PWM brightness, panel save/restore, mode validation/fixup, panel fitter setup, mode discovery through DDC/VBT/current hardware, connector properties, and LVDS object creation/destruction.

## Important APIs, Types, and Functions
Exported functions/objects are `psb_intel_lvds_set_brightness()`, `psb_intel_lvds_mode_valid()`, `psb_intel_lvds_mode_fixup()`, `psb_intel_lvds_destroy()`, `psb_intel_lvds_set_property()`, `psb_intel_lvds_connector_helper_funcs`, `psb_intel_lvds_connector_funcs`, and `psb_intel_lvds_init()`. Local `struct psb_intel_lvds_priv` stores saved LVDS/panel/backlight registers and an I2C bus.

## Control Flow
Initialization allocates encoder/connector/private state, creates DDC and backlight I2C GPIO buses, initializes connector/encoder, attaches scaling/backlight properties, reads EDID preferred mode, falls back to VBT fixed mode, then falls back to the current hardware-programmed LVDS mode. Mode fixup enforces pipe restrictions, rejects sharing a pipe with another encoder, and replaces adjusted timings with the fixed panel mode. Prepare powers the panel off after saving brightness; commit restores power and brightness. Property changes may trigger a full mode set or backlight update.

## State and Persistence Behavior
Persistent state includes panel fixed mode, backlight duty cycle, LVDS I2C bus, connector save/restore callbacks, saved LVDS registers, and VBT backlight data. Power sequencing writes `PP_CONTROL`, waits on `PP_STATUS`, and caches backlight register state when hardware is off.

## Dependencies and Integration Points
It depends on `gma_i2c_create()`, DDC helper `psb_intel_ddc_get_modes()`, DRM connector helpers, backlight infrastructure via `gma_backlight_set()`, panel/VBT data from BIOS parsing, and CRTC mode readback from `psb_intel_display.c`.

## Risks
`psb_intel_lvds_get_max_backlight()` logs `REG_READ()` even in the powered-off path, which can be unsafe if the register is inaccessible. PWM brightness uses `BUG_ON(max_pwm_blc == 0)`. I2C brightness requires valid VBT `lvds_bl` and target address assumptions. Mode/property setters return `-1` rather than standard errno values. Error paths must free two I2C buses plus DRM objects.

## Test Signals
Signals include LVDS connector creation, EDID/VBT/current-mode fallback selection, pipe restriction enforcement, scaling/backlight properties working through KMS, correct PWM and I2C brightness behavior, panel power sequencing on DPMS, and clean teardown without I2C adapter leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_modes.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_modes.c

## Purpose
This file contains the shared DDC mode probing helper for GMA500 connectors. It reads EDID from an I2C adapter, updates the connector EDID property, and adds EDID modes to the connector.

## Important APIs, Types, and Functions
The single exported function is `psb_intel_ddc_get_modes(struct drm_connector *connector, struct i2c_adapter *adapter)`. It calls `drm_get_edid()`, `drm_connector_update_edid_property()`, `drm_add_edid_modes()`, and frees the returned EDID block.

## Control Flow
The helper initializes `ret` to zero, attempts to read EDID over the provided adapter, and if successful updates connector metadata, adds modes, frees EDID, and returns the number of modes added. If EDID read fails, it returns zero.

## State and Persistence Behavior
No persistent local state is kept. The function mutates DRM connector state by updating its EDID property and probed modes list.

## Dependencies and Integration Points
It is used by LVDS and other display probing paths that have a DDC adapter. It depends on Linux I2C and DRM EDID helpers.

## Risks
The function assumes the adapter pointer is valid; callers must guard missing DDC buses. A zero return conflates absent EDID, invalid EDID, and zero modes, so callers need fallback paths such as VBT or pre-programmed modes.

## Test Signals
Signals include successful EDID reads adding expected modes, connector EDID property updates, proper fallback when `drm_get_edid()` returns NULL, and no EDID memory leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_modes.c -->
