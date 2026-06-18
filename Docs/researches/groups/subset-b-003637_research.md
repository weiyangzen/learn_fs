# subset-b-003637 research

Grouped research for Ingenic IPU, Intel Keem Bay display, and Lima Mali GPU DRM driver files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/`. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c

## Purpose
Implements the Ingenic JZ47xx Image Processing Unit as an atomic DRM overlay plane. The driver accepts RGB and YUV framebuffers, programs IPU DMA addresses, optional color-space conversion, resize coefficient LUTs, and vblank-driven address updates so the IPU output can feed the Ingenic LCD controller.

## Important APIs, types, and functions
Key types are `struct soc_info`, `struct ingenic_ipu_private_state`, and `struct ingenic_ipu`. The atomic plane hooks are `ingenic_ipu_plane_atomic_check()`, `ingenic_ipu_plane_atomic_update()`, and `ingenic_ipu_plane_atomic_disable()`. Scaling helpers include `reduce_fraction()`, `jz4725b_set_coefs()`, `jz4760_set_coefs()`, `ingenic_ipu_set_coefs()`, and the bicubic fixed-point `cubic_conv()`. Component lifecycle is handled by `ingenic_ipu_bind()`, `ingenic_ipu_unbind()`, `ingenic_ipu_probe()`, and `ingenic_ipu_remove()`. `ingenic_ipu_irq_handler()` commits cached buffer addresses and forwards vblank.

## Control flow
Atomic check validates visibility, minimum dimensions, even input/output widths, fixed hardware scaling-table limits, and noncoherent damage tracking. It marks the CRTC mode changed when the IPU is enabled, disabled, resized, repositioned, or has sharpness changed. Atomic update enables the clock, optionally resets and enables the IPU on modeset, syncs noncoherent framebuffer memory, caches plane DMA addresses, and only reprograms full registers on modeset. Full programming writes input strides, input size, format mapping, output RGB888 geometry, YUV-to-RGB CSC coefficients, scaling mode bits, LUT index, horizontal/vertical coefficients, clears status, and starts the frame interrupt. The IRQ acknowledges completion, writes cached Y/U/V addresses for the next frame, restarts older hardware when needed, and calls `drm_crtc_handle_vblank()`.

## State and persistence
Runtime state is mostly in `struct ingenic_ipu`: regmap, clock, SoC data, cached plane DMA addresses, clock-enabled flag, and the mutable `sharpness` property. Atomic scaling numerator/denominator state is held in a DRM private object so LUT programming is tied to the atomic transaction. Hardware state persists in IPU control, DMA, CSC, and resize registers until reset, disable, or next modeset.

## Dependencies and integration points
Depends on the Ingenic DRM master helpers for plane routing, noncoherent mapping, and disable/config operations. It uses DRM atomic plane helpers, GEM DMA framebuffer address helpers, regmap MMIO, platform component binding, one IRQ, and the IPU clock. Compatible strings select JZ4725B or JZ4760 format tables and coefficient algorithms.

## Risks
Scaling is hardware-constrained to 31 LUT entries, and `reduce_fraction()` can reject otherwise valid user modes. The check path permits up to 102 percent internal scaling distortion to find a legal coefficient ratio. Packed YUV422 is disabled on JZ4725B because some resize ratios crash hardware. Clock enable failure during update leaves the plane silently unprogrammed. Address updates are split between atomic update and IRQ, so missed frame interrupts can delay buffer flips.

## Test signals
Useful coverage includes atomic modeset and plane-update tests with RGB, planar YUV, packed YUV on JZ4760, sharpness values 0/1/bicubic, downscale/upscale/integer-upscale ratios, noncoherent framebuffer damage clips, enable/disable transitions, suspend/resume, and vblank delivery. Kernel logs expose scaling ratios, clock errors, and unsupported-format warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h

## Purpose
Defines the private Ingenic IPU register map and bit fields used by `ingenic-ipu.c` to program control, status, DMA addresses, image geometry, strides, resize LUTs, and color-space conversion.

## Important APIs, types, and functions
This header exports macros only. Important groups are `JZ_REG_IPU_*` register offsets, `JZ_IPU_CTRL_*` control bits, input/output geometry shifts, stride shifts, input/output format encodings, RGB component order encodings, JZ4725B resize LUT fields, JZ4760 bicubic coefficient fields, and CSC offset shifts.

## Control flow
There is no executable flow. The implementation combines these constants into regmap writes during atomic modeset and IRQ handling.

## State and persistence
No C state is stored here. The macros describe persistent MMIO state in the IPU block: run/stop/reset/chip-enable state, DMA addresses, format configuration, resize coefficients, and CSC coefficients.

## Dependencies and integration points
Includes `linux/bitops.h` for `BIT()`. It is private to the Ingenic DRM IPU implementation and avoids exposing IPU registers through a public DRM ABI.

## Risks
Register-field aliases are hardware-specific: for example RGB and YUV input format encodings share bit positions, and incorrect output order bits produce swapped colors. Any shift or mask drift directly corrupts IPU programming.

## Test signals
Build coverage catches missing macros. Runtime signals are correct color ordering, correct YUV conversion, successful scaling, and stable frame IRQ behavior across JZ4725B and JZ4760 compatible devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig

## Purpose
Adds the `DRM_KMB_DISPLAY` Kconfig option for the Intel Keem Bay display controller DRM driver.

## Important APIs, types, and functions
The symbol is tristate, depends on DRM and either `ARCH_KEEMBAY` or `COMPILE_TEST`, and selects DRM client, KMS helper, display helper, bridge connector, GEM DMA helper, and MIPI DSI support.

## Control flow
No runtime control flow exists. Build selection controls whether the `kmb-drm` module or built-in object is compiled.

## State and persistence
No runtime state is defined. The selected config persists in the kernel build and determines availability of the display driver.

## Dependencies and integration points
Ties the KMB display implementation to the DRM/KMS stack, GEM DMA framebuffer memory, bridge connectors, and MIPI DSI infrastructure.

## Risks
Missing selected helpers would break compilation or probe. The option is narrow to Keem Bay hardware but allows compile-test coverage on other architectures.

## Test signals
Build `CONFIG_DRM_KMB_DISPLAY=y/m` with Keem Bay and COMPILE_TEST configurations. Runtime validation belongs to the module probe and mode-setting files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile

## Purpose
Defines the object composition for the Intel Keem Bay DRM display driver.

## Important APIs, types, and functions
`kmb-drm-y` links `kmb_crtc.o`, `kmb_drv.o`, `kmb_plane.o`, and `kmb_dsi.o`; `obj-$(CONFIG_DRM_KMB_DISPLAY)` emits the module or built-in object.

## Control flow
There is no runtime flow. Build-time object ordering pulls together CRTC, platform driver, plane, and DSI/bridge code into one DRM driver.

## State and persistence
No state is stored here.

## Dependencies and integration points
The Makefile matches the Kconfig module name `kmb-drm` and must stay synchronized with source-file splits.

## Risks
Omitting one object can compile-link fail or remove runtime functionality such as DSI bridge setup or plane programming.

## Test signals
Kernel build and module link tests are sufficient for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c

## Purpose
Implements the Keem Bay LCD controller CRTC side of the DRM pipeline: vblank enable/disable, mode programming, atomic enable/disable/begin/flush, mode validation, and primary plane based CRTC creation.

## Important APIs, types, and functions
`struct kmb_crtc_timing` carries porch and sync widths used for programming. CRTC callbacks include `kmb_crtc_enable_vblank()`, `kmb_crtc_disable_vblank()`, `kmb_crtc_set_mode()`, `kmb_crtc_atomic_enable()`, `kmb_crtc_atomic_disable()`, `kmb_crtc_atomic_begin()`, `kmb_crtc_atomic_flush()`, and `kmb_crtc_mode_valid()`. `kmb_setup_crtc()` creates planes through `kmb_plane_init()` and initializes the DRM CRTC.

## Control flow
Atomic enable prepares the LCD clock, programs DSI via `kmb_dsi_mode_set()`, disables and clears interrupts, writes LCD timing registers, triggers the timing generator, enables the LCD controller, restores interrupt enables, and turns vblank on. Atomic begin masks vertical compare interrupts while a commit is prepared. Atomic flush re-enables vertical compare and arms or immediately sends pending vblank events under the DRM event lock. Atomic disable first disables planes for hardware safety, turns vblank off, and disables the LCD clock. Mode validation only accepts 1920x1080-class modes at 59 to 60 Hz with enough vertical front porch.

## State and persistence
CRTC state lives in the DRM CRTC and `struct kmb_drm_private`. Hardware timing, background color, interrupt compare, and LCD enable bits persist in LCD MMIO until changed or reset. Pending vblank events are consumed in `atomic_flush()`.

## Dependencies and integration points
Uses `kmb_drv.h` register accessors, `kmb_regs.h` register definitions, `kmb_dsi_mode_set()` for downstream MIPI configuration, and `kmb_plane_init()` for the primary/overlay layer set. Integrates with DRM atomic helpers and vblank core.

## Risks
Several timing values are hardcoded rather than derived from the DRM mode, even though logs print the mode porches. Mode validation uses `< KMB_CRTC_MAX_*` tests, effectively rejecting smaller-than-1080p modes despite max naming. Event delivery depends on vblank get succeeding. Disabling planes when the CRTC turns off is required by hardware.

## Test signals
Exercise 1080p60 modesets, invalid resolution/refresh/VFP rejection, vblank interrupt enable/disable, page-flip event delivery, suspend/resume, and CRTC disable with active planes. LCD timing registers and DRM vblank counters are direct diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c

## Purpose
Implements the Keem Bay platform DRM driver. It creates the DRM device, initializes clocks, MMIO, DSI host/bridge, mode config, CRTC/planes, LCD IRQ handling, runtime/system PM, framebuffer client setup, and teardown.

## Important APIs, types, and functions
Clock and hardware setup is split across `kmb_initialize_clocks()`, `kmb_display_clk_enable()`, `kmb_map_mmio()`, and `kmb_hw_init()`. DRM setup uses `kmb_setup_mode_config()` and `kmb_driver`. IRQ handling uses `handle_lcd_irq()`, `kmb_isr()`, `kmb_irq_reset()`, `kmb_irq_install()`, and `kmb_irq_uninstall()`. Platform lifecycle is `kmb_probe()` and `kmb_remove()`, with `kmb_pm_suspend()` and `kmb_pm_resume()` for PM.

## Control flow
Probe first locates the DSI endpoint and remote DSI platform device, registers a DSI host early through `kmb_dsi_host_bridge_init()`, and defers until the external bridge is available. It then allocates a managed DRM private, initializes DSI, maps LCD/MIPI MMIO, enables LCD/MIPI clocks and MSSCAM reset/clock bits, sets up mode config, installs the LCD IRQ, initializes polling, registers the DRM device, and starts the client setup. The LCD IRQ handler clears EOF, line compare, vertical compare, layer, and DMA error conditions. EOF applies deferred plane disables. Underflow recovery flushes FIFOs, disables DMA, and re-enables at a later vertical compare.

## State and persistence
`struct kmb_drm_private` stores LCD MMIO, clocks, CRTC, DSI pointer, IRQ lock, init display configuration, plane disable flags, underflow state, flush state, and the affected layer. Hardware state includes LCD interrupts, FIFO flush, DMA enables, MSSCAM clock/reset bits, and MIPI/LCD routing.

## Dependencies and integration points
Depends on OF graph wiring, reserved memory, syscon `intel,keembay-msscam`, DRM GEM DMA helpers, bridge connector support, the DSI helper file, and CRTC/plane files. The platform compatible is `intel,keembay-display`.

## Risks
Some setup calls ignore or squash errors, such as `kmb_initialize_clocks()` return in `kmb_hw_init()` and `kmb_dsi_encoder_init()` return assignment before CRTC port setup. Probe has global DSI host dependencies and defer-sensitive ordering. IRQ recovery is tightly coupled to plane update behavior and can drop plane updates while underflow recovery is active. Clock enable/disable is split between driver and CRTC paths and needs balanced sequencing.

## Test signals
Probe/defer with ADV7535 bridge, IRQ install/uninstall, fbdev client bring-up, reserved-memory configurations, DMA underflow injection, vblank counters, page flips during EOF, system suspend/resume, and driver remove should all be tested. Logs include clock rates, bridge attach, underflow notices, and IRQ errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h

## Purpose
Defines Keem Bay DRM private data, platform limits, clock containers, LCD register access helpers, and CRTC setup prototypes shared by the KMB driver files.

## Important APIs, types, and functions
Important types are `struct kmb_clock` and `struct kmb_drm_private`. Helper functions/macros include `to_kmb()`, `crtc_to_kmb_priv()`, `kmb_write_lcd()`, `kmb_read_lcd()`, `kmb_set_bitmask_lcd()`, and `kmb_clr_bitmask_lcd()`. Constants define 1920x1080 display limits, refresh constraints, default LCD clock, and driver version.

## Control flow
Only inline MMIO accessors execute. They read or write LCD controller registers and implement read-modify-write bit set/clear sequences.

## State and persistence
The private structure is the central runtime state for LCD MMIO, clock handles, DRM CRTC, saved atomic suspend state, IRQ fields, per-plane init state, and underflow recovery flags.

## Dependencies and integration points
Includes DRM device definitions, KMB plane types, and register constants. Used by `kmb_drv.c`, `kmb_crtc.c`, and `kmb_plane.c`.

## Risks
Read-modify-write helpers are not internally locked, so callers must hold appropriate serialization when racing IRQ and atomic paths. The min/max naming around 1920x1080 constants is confusing and can cause incorrect mode-validation changes.

## Test signals
Build coverage catches structure and prototype drift. Runtime signals are correct MMIO programming through users of these helpers and stable underflow state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c

## Purpose
Programs the Keem Bay MIPI DSI transmitter and D-PHY, creates a minimal MIPI DSI host for the external ADV7535 bridge path, attaches the bridge to the DRM encoder, and connects the LCD controller output to MIPI.

## Important APIs, types, and functions
Public entry points are `kmb_dsi_host_bridge_init()`, `kmb_dsi_init()`, `kmb_dsi_encoder_init()`, `kmb_dsi_map_mmio()`, `kmb_dsi_clk_init()`, `kmb_dsi_mode_set()`, and `kmb_dsi_host_unregister()`. Major internal groups are datatype/word-count helpers, frame-generator programming (`mipi_tx_fg_section_cfg()`, `mipi_tx_fg_cfg()`), controller programming (`mipi_tx_init_cntrl()`), D-PHY test-mode writes (`test_mode_send()`), PLL selection (`mipi_tx_pll_setup()`), slew-rate setup, D-PHY init/wait helpers, and `connect_lcd_to_mipi()`.

## Control flow
The early host bridge init allocates global `mipi_dsi_host` and `mipi_dsi_device` objects, registers the host, follows DT graph output endpoint 1 to the bridge, and returns `-EPROBE_DEFER` until the bridge driver is ready. A modeset copies the DRM adjusted mode into global frame config, computes lane data rate from total pixels, refresh, bpp, and active lanes, drops to two lanes for low rates, initializes frame section/header/timing/FIFO/controller registers, initializes the D-PHY or paired D-PHYs, enables the bridge chain, and sets MSSCAM routing from LCD to MIPI. Encoder init creates a simple DSI encoder, attaches the bridge without an internal connector, creates a bridge connector, and attaches it.

## State and persistence
File-scope globals store the DSI host, DSI device, bridge, default frame section, frame timing, DSI config, and controller config. `struct kmb_dsi` stores MMIO, clocks, device pointers, encoder base, and system clock MHz. Hardware state includes MIPI HS controller registers, frame generator registers, FIFO allocation, D-PHY PLL/test configuration, lane enables, and syscon routing.

## Dependencies and integration points
Depends on OF graph, DRM bridge and bridge-connector helpers, DRM MIPI DSI host infrastructure, platform resources named `mipi`, clocks `clk_mipi`, `clk_mipi_ecfg`, `clk_mipi_cfg`, `intel,keembay-msscam` syscon, and register macros from `kmb_regs.h`. It is called from KMB probe, mode config, and CRTC mode-set paths.

## Risks
The host transfer/attach/detach callbacks are stubs, so this only supports bridges configured out-of-band, as documented for ADV7535. Many configuration objects are global, so multi-instance support is unsafe. Several D-PHY wait loops only log timeout but return success. PLL best-value search does not explicitly fail if no good `m/n` pair is found. Hardcoded controller number `MIPI_CTRL6`, default four-lane assumptions, and low-rate two-lane fallback are hardware-board specific.

## Test signals
Validate probe deferral until the bridge appears, encoder/connector creation, 1080p timing programming, two-lane fallback for low pixel rates, D-PHY PLL lock and FSM logs, bridge-chain enable, syscon routing, and MIPI clock-rate programming. Oscilloscope or bridge link status is the strongest hardware signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h

## Purpose
Declares Keem Bay DSI data structures, MIPI/DSI/D-PHY constants, register helper inlines, configuration structs, and the DSI entry points used by the platform and CRTC code.

## Important APIs, types, and functions
Important types include `struct kmb_dsi`, `struct mipi_ctrl_cfg`, `struct mipi_tx_ctrl_cfg`, `struct mipi_tx_frame_cfg`, `struct mipi_tx_frame_section_cfg`, datatype parameter structs, and D-PHY/DSI enums. Inline helpers are `kmb_write_mipi()`, `kmb_read_mipi()`, `kmb_write_bits_mipi()`, `kmb_set_bit_mipi()`, and `kmb_clr_bit_mipi()`. Prototypes cover host bridge init, mode set, MMIO mapping, clock init, encoder init, and unregister.

## Control flow
The header has no complex flow beyond MMIO access helpers. `kmb_write_bits_mipi()` performs read-modify-write masking for arbitrary bit fields; set/clear helpers manipulate single bit offsets.

## State and persistence
The `kmb_dsi` structure persists per DSI instance and owns encoder base, platform device, host/device pointers, bridge pointer, MIPI MMIO, clocks, and system clock value.

## Dependencies and integration points
Includes DRM encoder and MIPI DSI definitions. The constants must match `kmb_dsi.c` and `kmb_regs.h`; the public prototypes are consumed by `kmb_drv.c` and `kmb_crtc.c`.

## Risks
`kmb_write_bits_mipi()` uses `(1 << num_bits) - 1`, which is unsafe for 32-bit widths but current callers use smaller fields. The large enum surface is hardware-contract sensitive. Header-level constants hardcode default 24 MHz clocks, 24 bpp, and default lane rate.

## Test signals
Build coverage catches signature drift. Runtime validation is provided by DSI clock init, mode set, bridge attach, and D-PHY programming tests in the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c

## Purpose
Implements Keem Bay DRM plane support for LCD video layers. It validates framebuffer formats and sizes, programs DMA addresses and layer format registers, configures alpha/blending and CSC, defers disables to EOF, and creates the primary and overlay planes.

## Important APIs, types, and functions
Plane callbacks are `kmb_plane_atomic_check()`, `kmb_plane_atomic_update()`, `kmb_plane_atomic_disable()`, and `kmb_plane_destroy()`. Helpers include `check_pixel_format()`, `get_pixel_format()`, `get_bits_per_pixel()`, `config_csc()`, and `kmb_plane_set_alpha()`. `kmb_plane_init()` creates up to `KMB_MAX_PLANES` planes and records the primary.

## Control flow
Atomic check rejects unsupported formats, changes in format after first use, changes in framebuffer width/height after first configuration, out-of-range plane dimensions, and scaling. Atomic update exits during underflow recovery, then programs DMA length, stride, line width, Y/Cb/Cr addresses, source rectangle, destination position, pixel format, planar CSC, alpha register and flags, LCD control layer enable/blend bits, pipeline DMA, output RGB888/MIPI mode, DMA configuration, initial display config cache, and EOF/DMA-error interrupts. Atomic disable records a per-plane disable flag and control bit; the IRQ EOF path performs the actual hardware disable.

## State and persistence
Persistent software state is held in `kmb->init_disp_cfg[plane_id]` and `kmb->plane_status[plane_id]`. Hardware state includes layer DMA addresses, widths, strides, format config, CSC coefficients, alpha, LCD control enables, output format, and interrupt enables.

## Dependencies and integration points
Depends on DRM atomic plane helpers, GEM DMA framebuffer address helpers, blend properties, `kmb_drv.h` MMIO helpers, and `kmb_regs.h` register constants. The IRQ logic in `kmb_drv.c` consumes plane disable and underflow state.

## Risks
`KMB_MAX_PLANES` is defined as 2 even though enum and register constants describe four layers, so only two video layers are created. Static DMA address storage is shared across updates. Format and size immutability after first configuration is a hardware limitation that userspace must handle. Underflow recovery can cause updates to be skipped. Planar stride calculations use width and `cpp[0]`, which needs careful validation for subsampled formats.

## Test signals
Test primary and overlay updates, all advertised packed and planar formats, alpha blend modes, immutable format/size rejection, no-scaling enforcement, EOF-delayed disable, DMA underflow recovery, and vblank/page-flip behavior. LCD layer register dumps and underflow logs are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h

## Purpose
Declares Keem Bay plane constants, layer IDs, sub-plane IDs, plane/private status structures, and plane creation/destruction APIs.

## Important APIs, types, and functions
Defines interrupt masks for VL0, VL1, GL0, GL1, combined DMA errors, `POSSIBLE_CRTCS`, `KMB_MAX_PLANES`, `enum layer_id`, `enum sub_plane_id`, `struct kmb_plane`, `struct layer_status`, `struct disp_cfg`, `kmb_plane_init()`, and `kmb_plane_destroy()`.

## Control flow
There is no executable control flow. The declarations shape the plane loops and IRQ handling in the C files.

## State and persistence
`struct layer_status` persists deferred disable state and related LCD control bits. `struct disp_cfg` persists first-use width, height, and format constraints for each plane.

## Dependencies and integration points
Includes DRM fourcc and plane definitions and relies on layer interrupt bits from `kmb_regs.h` through inclusion order in users.

## Risks
`POSSIBLE_CRTCS` is defined twice and `KMB_MAX_PLANES` is 2 despite four enumerated layer IDs. Any change here affects plane creation loops, IRQ array indexing, and underflow recovery behavior.

## Test signals
Build coverage and runtime creation of the expected number of planes are the main signals. Plane disable and DMA error recovery validate the status structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h

## Purpose
Provides register offsets, bit fields, and convenience macros for the Keem Bay LCD controller, layer DMA/CSC/format registers, MIPI DSI transmitter, D-PHY, IRQ blocks, MSSCAM syscon routing, and QoS-related registers.

## Important APIs, types, and functions
Important groups include LCD control and interrupt bits, layer configuration and DMA address macros `LCD_LAYERn_*`, output timing and format registers, MIPI HS controller register macros `MIPI_TXm_*`, FIFO allocation helpers `SET_MC_FIFO_*`, MIPI IRQ masks, D-PHY test/control/status macros, PLL lock and stop-state helpers, and MSSCAM route/clock/reset constants.

## Control flow
The file is declarative, but some macros expand to MMIO helper calls. Address macros compute per-layer and per-MIPI-controller offsets used in plane, CRTC, IRQ, and DSI programming.

## State and persistence
No C state is stored. The definitions describe hardware state programmed by the KMB driver: LCD enable/interrupt/layer/DMA/timing, output format, MIPI controller configuration, D-PHY lane and PLL state, and syscon route/reset bits.

## Dependencies and integration points
Consumed by all KMB C files. Macro call helpers assume `kmb_write_bits_mipi()`, `kmb_read_mipi()`, and related functions are in scope.

## Risks
Register arithmetic and bit positions are central to hardware correctness. There is a duplicate `DPHY_INIT_CTRL2` definition, and macros with side effects can obscure call sites. Wrong layer stride offsets or FIFO masks can corrupt display DMA. D-PHY macros use DPHY numbering assumptions around 6 and 7.

## Test signals
Compile-time use catches some symbol drift. Runtime validation is successful modeset, correct scanout colors, stable DMA, MIPI link bring-up, D-PHY lock, and expected interrupt status/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig

## Purpose
Adds `DRM_LIMA`, the DRM render driver option for ARM Mali 400/450 Utgard GPUs.

## Important APIs, types, and functions
The symbol is tristate, depends on DRM, ARM/ARM64/COMPILE_TEST, MMU, COMMON_CLK, and OF, and selects DRM scheduler, GEM shmem helper, PM devfreq, and the simple_ondemand devfreq governor.

## Control flow
No runtime flow. The selected symbol controls compilation of the `lima` module or built-in driver.

## State and persistence
No runtime state exists. Build configuration determines availability of the driver and its scheduler/devfreq dependencies.

## Dependencies and integration points
Links the driver to the DRM render-node stack, MMU-backed VM, device tree probing, clock framework, DRM scheduler, shmem GEM, and devfreq.

## Risks
The driver relies on selected subsystems for core behavior; missing scheduler or shmem support would be fatal. COMPILE_TEST broadens build coverage but cannot validate hardware-specific paths.

## Test signals
Build with module and built-in configurations on ARM/ARM64 and COMPILE_TEST. Runtime signals are probe and render-node IOCTL tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile

## Purpose
Defines the object list for the Lima DRM driver.

## Important APIs, types, and functions
`lima-y` links driver, device, PMU, L2 cache, MMU, GP, PP, GEM, VM, scheduler, context, DLBU, broadcast, trace, and devfreq objects. `obj-$(CONFIG_DRM_LIMA)` emits `lima.o`.

## Control flow
No runtime control flow. Build composition mirrors the driver's runtime split between platform/IOCTL, memory management, scheduling, hardware IP blocks, and power management.

## State and persistence
No state is stored here.

## Dependencies and integration points
Must stay synchronized with the inter-file dependencies in `lima_device.c`, scheduler code, GP/PP pipe setup, GEM/VM, and devfreq.

## Risks
Missing any object can cause link failures or runtime NULL callback paths.

## Test signals
Kernel build and module load tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c

## Purpose
Controls the Mali450 broadcast unit used to send register writes and interrupts across multiple pixel processors.

## Important APIs, types, and functions
Exports `lima_bcast_enable()`, `lima_bcast_init()`, `lima_bcast_fini()`, `lima_bcast_resume()`, `lima_bcast_suspend()`, `lima_bcast_mask_irq()`, and `lima_bcast_reset()`. Internal `lima_bcast_hw_init()` writes broadcast and interrupt masks.

## Control flow
Init builds a mask from present PP cores and programs broadcast and interrupt mask registers. Task execution in `lima_pp.c` calls `lima_bcast_enable()` with the active PP count to route broadcast work only to participating processors. Error and mask paths clear broadcast and interrupt masks, and reset restores them.

## State and persistence
The present-PP mask is stored in `ip->data.mask`. Hardware broadcast and interrupt mask registers persist until disabled, reset, or reinitialized on resume.

## Dependencies and integration points
Uses `lima_device`, `lima_sched_pipe`, PP IP IDs, and register constants. Integrated only when the Mali450 broadcast IP is present and the PP pipe sets `bcast_processor`.

## Risks
Mask construction depends on IP discovery order and PP IDs. Incorrect masks can send work to absent PP cores or miss active cores, leading to hangs or incomplete rendering.

## Test signals
Validate Mali450 multi-PP rendering with broadcast enabled, interrupt masking on error paths, reset recovery, and resume reprogramming. Register dumps of broadcast masks show expected PP participation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h

## Purpose
Declares the Lima broadcast unit interface used by device initialization and the PP scheduler path.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exposes lifecycle calls plus `lima_bcast_enable()`, `lima_bcast_mask_irq()`, and `lima_bcast_reset()`.

## Control flow
No runtime flow exists here. Callers use the declarations to initialize, suspend/resume, enable, mask, and reset broadcast programming.

## State and persistence
No state is declared beyond using `struct lima_ip` and `struct lima_device` from including contexts.

## Dependencies and integration points
Used by `lima_device.c` for IP lifecycle and `lima_pp.c` for multi-PP task dispatch and recovery.

## Risks
The header references `struct lima_device` without its own forward declaration, relying on include order in current users.

## Test signals
Build coverage catches signature drift; runtime coverage comes from Mali450 broadcast rendering paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c

## Purpose
Manages per-file Lima GPU contexts. A context owns one DRM scheduler entity per hardware pipe and carries process debug identity.

## Important APIs, types, and functions
Exports `lima_ctx_create()`, `lima_ctx_free()`, `lima_ctx_get()`, `lima_ctx_put()`, `lima_ctx_mgr_init()`, and `lima_ctx_mgr_fini()`. `lima_ctx_do_release()` tears down scheduler contexts when the reference count reaches zero.

## Control flow
Create allocates a context, initializes scheduler contexts for GP and PP pipes, inserts the context into an xarray handle table, and records current PID and process name. Free erases the handle under the manager mutex and drops the reference. Get loads and refcounts a context under the same mutex. Manager fini walks any remaining handles and releases them.

## State and persistence
State is held in `struct lima_ctx`: kref, device pointer, scheduler contexts, process name, and PID. The manager owns a locked xarray of user-visible context IDs. State persists until explicit free or DRM file close.

## Dependencies and integration points
Depends on `lima_sched_context_init/fini()` and the per-file private data in `lima_drv.c`. IOCTL submit paths lookup contexts before scheduling work.

## Risks
Partial create unwinding must match the number of initialized pipes. Context handles are per DRM file; use-after-free is prevented by krefs but scheduler jobs must hold their references correctly.

## Test signals
Create/free IOCTL tests, submit after free rejection, file-close cleanup, multi-pipe context initialization failure injection, and process name/PID in error dumps validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h

## Purpose
Defines Lima context and context-manager structures and declares the context API.

## Important APIs, types, and functions
`struct lima_ctx` contains a kref, device pointer, scheduler contexts for all pipes, and debug process identity. `struct lima_ctx_mgr` contains a mutex and xarray. Prototypes cover create/free/get/put/init/fini.

## Control flow
No executable flow. The declarations support IOCTL and scheduler code.

## State and persistence
Context state persists per user-created context; the manager persists per open DRM file.

## Dependencies and integration points
Includes xarray, scheduler task name size, and `lima_device.h` for pipe counts and scheduler context type.

## Risks
The header pulls in broad device definitions, so include cycles must be managed carefully. Changing `context[lima_pipe_num]` impacts scheduler ABI assumptions inside the driver.

## Test signals
Build coverage and context IOCTL tests are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c

## Purpose
Implements optional devfreq and thermal cooling support for Lima GPU clock scaling using OPP tables and busy/idle accounting.

## Important APIs, types, and functions
Public functions are `lima_devfreq_init()`, `lima_devfreq_fini()`, `lima_devfreq_record_busy()`, `lima_devfreq_record_idle()`, `lima_devfreq_resume()`, and `lima_devfreq_suspend()`. Internal helpers are `lima_devfreq_update_utilization()`, `lima_devfreq_target()`, `lima_devfreq_reset()`, and `lima_devfreq_get_dev_status()`.

## Control flow
Init exits quietly when no `operating-points-v2` property exists. Otherwise it sets the `core` clock name, optional `mali` regulator, loads OPPs, chooses an initial frequency, configures simple_ondemand thresholds, registers devfreq, and optionally registers cooling. Busy/idle calls update utilization under a spinlock and maintain a busy counter. Devfreq polling reads current GPU rate, rolls elapsed time into busy or idle buckets, returns status, and resets counters. Suspend/resume wrap the devfreq device and reset accounting on resume.

## State and persistence
`struct lima_devfreq` stores devfreq and cooling handles, governor data, busy/idle ktime counters, last update time, busy count, and spinlock. State persists for the device lifetime after init.

## Dependencies and integration points
Uses the clk, devfreq, OPP, thermal cooling, property, and regulator frameworks. Scheduler power-management paths record busy/idle transitions while tasks run.

## Risks
Busy count underflow is only `WARN_ON`, so mismatched record calls can corrupt utilization. Debug percentage divides by `total_time / 100`, which can be zero for tiny intervals. Optional regulator handling must align with OPP voltage requirements.

## Test signals
Validate devices with and without OPP tables, frequency transitions under render load, cooling device registration, suspend/resume accounting reset, and balanced busy/idle calls during GP/PP jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h

## Purpose
Declares Lima devfreq state and APIs for initialization, teardown, utilization accounting, and PM transitions.

## Important APIs, types, and functions
`struct lima_devfreq` contains devfreq/cooling handles, simple_ondemand governor data, busy/idle times, last update time, busy count, and spinlock. Prototypes cover init/fini, busy/idle recording, resume, and suspend.

## Control flow
No executable flow exists in the header.

## State and persistence
The structure persists inside `struct lima_device` and is active only when an OPP table was found and devfreq registration succeeded.

## Dependencies and integration points
Includes devfreq, spinlock, and ktime headers. Used by device lifecycle and scheduler runtime accounting.

## Risks
All mutable fields require lock discipline because GP and PP completion paths can update accounting concurrently.

## Test signals
Build coverage plus devfreq load/suspend/resume tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c

## Purpose
Initializes and tears down the Lima hardware device: clocks, reset, regulator, VM address space, MMIO, IP block discovery, GP/PP scheduler pipes, error-dump state, and runtime suspend/resume.

## Important APIs, types, and functions
`struct lima_ip_desc` describes each IP block's name, IRQ, required status, offset, and lifecycle callbacks. Public entry points are `lima_device_init()`, `lima_device_fini()`, `lima_device_resume()`, `lima_device_suspend()`, and `lima_ip_name()`. Helpers cover clock/regulator init, IP init/fini/resume/suspend, and GP/PP pipe init/fini.

## Control flow
Device init sets DMA constraints, enables bus/core clocks and optional reset, enables optional regulator, creates an empty VM, reserves VA/DLBU memory depending on Mali400 versus Mali450, maps MMIO, probes every IP descriptor, initializes the GP scheduler pipe, initializes the PP pipe by pairing present PP, PP MMU, and L2 cache blocks, initializes error-dump bookkeeping, and logs rates. Fini reverses scheduler pipes, IPs, DLBU memory, VM, regulator, and clocks. Resume enables clocks/regulator, resumes all present IPs, then resumes devfreq. Suspend refuses if scheduler credits indicate running tasks, suspends devfreq, suspends IPs in reverse order, disables regulator, and disables clocks.

## State and persistence
`struct lima_device` stores GPU id, versions, PP count, MMIO, clocks, reset, regulator, IP array, scheduler pipes, empty VM, VA range, DLBU page, devfreq state, and error-task list. IP descriptors are static. Hardware state is rebuilt on resume by each IP callback.

## Dependencies and integration points
Depends on platform resource 0, clock names `bus` and `core`, optional reset array, optional `mali` regulator, DMA mapping, VM code, GP/PP/MMU/PMU/L2/DLBU/BCAST modules, and DRM scheduler pipe setup. Called by `lima_drv.c` probe/remove and PM ops.

## Risks
IP discovery order matters: optional IPs can depend on earlier PP presence, and L2 cache selection differs between Mali400 and Mali450. Suspend can fail with `-EBUSY` if jobs are running. Error unwinding must match the partial init state. Mali450 reserves a VA region for DLBU; wrong VA bounds would collide with user BO mappings.

## Test signals
Probe/remove on Mali400 and Mali450, optional regulator/reset absence, missing optional PP cores, multiple L2 layouts, runtime suspend while idle and busy, resume after suspend, and failure injection during IP init validate this file. Logs expose IP versions and clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h

## Purpose
Defines the central Lima device model, GPU/IP/pipe IDs, IP block representation, device-wide state, polling helper, and device lifecycle prototypes.

## Important APIs, types, and functions
Enums define Mali400/Mali450 IDs, all IP blocks, and GP/PP pipe IDs. `struct lima_ip` wraps an IP block's device, id, presence, MMIO, IRQ, and per-IP union state. `struct lima_device` stores platform, DRM, clocks, reset, regulator, IPs, scheduler pipes, VM bounds, DLBU page, devfreq, and error-dump state. `to_lima_dev()` and `lima_poll_timeout()` are important helpers.

## Control flow
`lima_poll_timeout()` repeatedly calls a supplied poll function until success or timeout, sleeping between attempts when requested. Other content is declarative.

## State and persistence
The structures describe the full runtime state for one Lima GPU and its IP blocks. This state persists for the platform device lifetime.

## Dependencies and integration points
Includes DRM device, Linux list/mutex/delay, scheduler, dump, and devfreq headers. Used by nearly every Lima source file.

## Risks
The central header couples many modules; structure changes are high blast radius. The polling helper returns success immediately on a truthy callback and assumes callers provide safe timeout values.

## Test signals
Build coverage across all Lima files and runtime probe/suspend/job tests validate these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c

## Purpose
Controls the Mali450 Dynamic Load Balancing Unit used to distribute PP tile-list work across pixel processors.

## Important APIs, types, and functions
Exports `lima_dlbu_enable()`, `lima_dlbu_disable()`, `lima_dlbu_set_reg()`, `lima_dlbu_init()`, `lima_dlbu_fini()`, `lima_dlbu_resume()`, and `lima_dlbu_suspend()`. `lima_dlbu_hw_init()` programs the master tile-list physical and virtual base addresses.

## Control flow
Init/resume writes the write-combined DLBU page DMA address and reserved GPU VA. PP task execution enables a PP mask for the selected processors, optionally writes task-provided DLBU registers, and uses the reserved DLBU VA as the PP frame base. Non-DLBU paths disable the PP enable mask.

## State and persistence
DLBU shared page state lives in `lima_device` as CPU and DMA addresses. Hardware registers persist the PP mask, tile-list base addresses, frame dimensions, config, and start tile position.

## Dependencies and integration points
Depends on Lima device, VM reserved VA constants, and register definitions. Integrated by Mali450 PP task dispatch in `lima_pp.c`.

## Risks
The reserved VA and DMA page must remain valid for the device lifetime. Bad PP masks or task-supplied DLBU registers can distribute work incorrectly and hang rendering.

## Test signals
Mali450 PP submissions with `use_dlbu`, multi-PP workloads, DLBU disable fallback, resume reprogramming, and register dumps of PP enable masks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h

## Purpose
Declares the Lima DLBU lifecycle, enable/disable, and register-programming API.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports `lima_dlbu_enable()`, `lima_dlbu_disable()`, `lima_dlbu_set_reg()`, and init/fini/resume/suspend functions.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here; callers pass `struct lima_device` or `struct lima_ip`.

## Dependencies and integration points
Used by `lima_device.c` for IP lifecycle and `lima_pp.c` for Mali450 task setup.

## Risks
Prototype drift would break PP task dispatch or device init.

## Test signals
Build coverage plus Mali450 DLBU render tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c

## Purpose
Implements the Lima DRM render driver: module parameters, IOCTL dispatch, per-file open/close state, platform probe/remove, runtime PM registration, error-state sysfs dump access, and DRM driver registration.

## Important APIs, types, and functions
IOCTL handlers include `lima_ioctl_get_param()`, `lima_ioctl_gem_create()`, `lima_ioctl_gem_info()`, `lima_ioctl_gem_submit()`, `lima_ioctl_gem_wait()`, `lima_ioctl_ctx_create()`, and `lima_ioctl_ctx_free()`. File callbacks are `lima_drm_driver_open()` and `lima_drm_driver_postclose()`. Error dump helpers are `lima_error_state_read()` and `lima_error_state_write()`. Platform lifecycle is `lima_pdev_probe()` and `lima_pdev_remove()`.

## Control flow
Probe initializes scheduler slabs, allocates `struct lima_device`, reads compatible data, allocates a DRM device, initializes hardware, initializes devfreq, enables runtime PM/autosuspend, registers DRM, and creates a binary sysfs error file. Open creates a per-file VM and context manager. Submit validates pipe, flags, frame size, BO list, user frame copy, task frame validation, context handle, and delegates scheduling to GEM. Remove unregisters sysfs/DRM, disables runtime PM, tears down devfreq/device, drops DRM, and finalizes scheduler slabs.

## State and persistence
Module parameters persist globally: scheduler timeout, heap initial pages, max saved error tasks, and hang limit. Per-file state is `struct lima_drm_priv` with VM and context manager. Device state is in `struct lima_device`. Error-state data persists in `ldev->dump` and `error_task_list` until read or cleared by writing sysfs.

## Dependencies and integration points
Depends on DRM IOCTL/render node infrastructure, sync objects, GEM shmem, Lima GEM/VM/context/device code, platform OF compatible strings `arm,mali-400` and `arm,mali-450`, runtime PM, and sysfs bin attributes.

## Risks
User-copy size validation is safety critical for BO arrays and task frames. IOCTL ABI checks must reject padding/invalid flags. Probe failure unwinding must free scheduler slabs exactly once. Error dump read concatenates variable-size task blobs and requires mutex protection. Runtime PM state must be active before DRM exposes render nodes.

## Test signals
Use render-node IOCTL tests for get-param, GEM create/info/wait, context create/free, valid and invalid submits, explicit fence syncobjs, file close cleanup, sysfs error read/write, probe deferral/failure injection, and runtime autosuspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h

## Purpose
Declares Lima driver-wide module parameters, per-file DRM private state, submit aggregation state, compatible data, and helper accessors.

## Important APIs, types, and functions
Exports extern module parameters, `struct lima_drm_priv`, `struct lima_submit`, `struct lima_compatible`, and `to_lima_drm_priv()`. `struct lima_submit` carries context, pipe id, flags, BO arrays, syncobj handles, and scheduler task pointer.

## Control flow
No executable flow except the inline file-private accessor.

## State and persistence
Per-file state persists while a DRM file is open. `lima_submit` is transient per IOCTL submission and bridges IOCTL parsing to GEM/scheduler code.

## Dependencies and integration points
Includes DRM file, Lima context, and Lima device definitions. Used by GEM, driver, and VM submit paths.

## Risks
The submit structure sits on a trust boundary after user data is copied and before jobs are queued; field semantics must stay aligned with IOCTL ABI and scheduler expectations.

## Test signals
Build coverage and IOCTL submit tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h

## Purpose
Defines the binary error-dump file format used by Lima to expose saved failed GPU tasks through sysfs.

## Important APIs, types, and functions
Constants include version numbers, magic `LIMA_DUMP_MAGIC`, task IDs for GP/PP, and chunk IDs for frame, buffer, process name, and process ID. Structures include `lima_dump_head`, `lima_dump_task`, `lima_dump_chunk`, `lima_dump_chunk_buffer`, and `lima_dump_chunk_pid`.

## Control flow
No executable flow. Scheduler error code serializes data using this layout; `lima_drv.c` reads and clears it through the binary sysfs attribute.

## State and persistence
Dump headers and task/chunk records persist in `lima_device` error-task storage until cleared or driver removal.

## Dependencies and integration points
Uses fixed-width Linux types to define a stable binary layout consumed by debugging tools.

## Risks
Changing structure layout or IDs breaks userspace dump decoders. Size fields must be validated by producers and readers to avoid truncated or malformed dumps.

## Test signals
Trigger GPU task errors, read `/sys/.../error`, validate magic/version/chunk layout, and clear by writing the sysfs file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c

## Purpose
Implements Lima GEM buffer creation, heap-buffer growth, VM attachment, mmap/vmap/pin restrictions, submission dependency handling, scheduler queuing, reservation fences, and GEM wait.

## Important APIs, types, and functions
Public APIs are `lima_heap_alloc()`, `lima_gem_create_handle()`, `lima_gem_create_object()`, `lima_gem_get_info()`, `lima_gem_submit()`, and `lima_gem_wait()`. GEM object hooks include free/open/close/pin/vmap/mmap. Dependency helpers are `lima_gem_sync_bo()` and `lima_gem_add_deps()`.

## Control flow
Create allocates a shmem GEM object, forces DMA32 pages, optionally initializes a growable heap BO, otherwise pins/maps pages through shmem, creates a handle, and drops the allocation reference. Object open adds the BO to the file VM, close removes it. Heap allocation doubles committed size up to BO size, faults shmem pages, maps SG tables for DMA, maps newly added pages into the VM, and updates `heap_size`. Submit resolves optional output syncobj, looks up each BO, pins VM mappings by incrementing BO-VA references, locks reservations, initializes a scheduler task, adds explicit or implicit dependencies, queues the task, attaches the returned fence to BO reservations with read/write usage, unlocks, drops refs, and updates output syncobj.

## State and persistence
`struct lima_bo` stores shmem object, lock, VA list, and heap size. BO-to-VM mappings persist while open handles or executing tasks hold references. DMA reservation fences persist for synchronization. Heap BO committed size can grow across recoverable GP out-of-memory interrupts.

## Dependencies and integration points
Depends on DRM GEM shmem, DMA mapping, syncobj, DRM scheduler, Lima VM, scheduler task API, IOCTL submit parsing, and module parameter `lima_heap_init_nr_pages`.

## Risks
Heap BOs cannot be pinned, vmapped, or mmaped; callers must respect that. Error unwind must drop BO VM refs and object refs exactly once. Explicit sync bypasses implicit dependencies, so userspace must supply correct fences. SG table replacement during heap growth must keep DMA mappings and VM mappings consistent.

## Test signals
Test GEM create/info/mmap, heap BO growth during GP recovery, submit with read/write BO flags, explicit and implicit fences, output syncobj replacement, invalid handles, reservation-lock failure injection, and GEM wait timeout conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h

## Purpose
Defines Lima GEM BO state and declares the GEM, heap, submit, and wait APIs.

## Important APIs, types, and functions
`struct lima_bo` embeds `drm_gem_shmem_object`, a mutex, VA mapping list, and heap size. Inline helpers convert GEM objects to Lima BOs, return BO size, and return the DMA reservation object. Prototypes cover heap allocation, object creation, handle creation, info query, submit, wait, and VMA flag setup.

## Control flow
Only simple inline accessors execute.

## State and persistence
The BO structure persists for the GEM object lifetime. The VA list tracks per-VM mappings and heap size tracks committed heap pages.

## Dependencies and integration points
Includes DRM GEM shmem helper and is used by IOCTL, VM, GP recovery, and scheduler submission code.

## Risks
The embedded shmem object layout is assumed by `to_lima_bo()`. Incorrect heap-size semantics can break mmap/pin restrictions and GP heap recovery.

## Test signals
Build coverage plus GEM create/submit/heap tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c

## Purpose
Implements the Mali GP (geometry processor) IP block, including IRQ handling, reset, task validation/run/recovery, version detection, and scheduler-pipe callback setup.

## Important APIs, types, and functions
Lifecycle functions are `lima_gp_init()`, `lima_gp_fini()`, `lima_gp_resume()`, and `lima_gp_suspend()`. Pipe setup is `lima_gp_pipe_init()` and `lima_gp_pipe_fini()`. Internal callbacks include `lima_gp_task_validate()`, `lima_gp_task_run()`, `lima_gp_task_fini()`, `lima_gp_task_error()`, `lima_gp_task_mmu_error()`, `lima_gp_task_recover()`, and reset helpers.

## Control flow
IRQ handling distinguishes shared IRQ false positives, recoverable PLBU out-of-memory, other errors, and normal VS/PLBU completion. Task validation checks command-list and heap address ranges. Task run identifies heap BOs by matching VA to PLBU allocation start, updates heap end, marks recoverability, waits for any prior async reset, writes GP frame registers, updates PLBU allocation, and starts VS and/or PLBU. Recoverable PLBU OOM grows the heap if the fail size reached current heap size, then updates allocation registers and resumes. Error handling masks interrupts and hard-resets after bus stop.

## State and persistence
`ip->data.async_reset` tracks deferred soft resets. `pipe->current_task`, `pipe->error`, task heap pointers, and recoverable flags coordinate with the scheduler. Hardware GP registers persist frame addresses, command bits, interrupt masks, and performance-counter reset probes.

## Dependencies and integration points
Depends on Lima scheduler, VM, GEM heap allocation, DRM UAPI GP frame layout, MMU error callbacks, and register constants. Device init installs this as the GP pipe processor.

## Risks
Heap recovery depends on exact PLBU allocation VA matching. Interrupt completion considers active bits and command-list end bits; wrong interpretation can complete early or hang. Reset polling has short timeouts. Task slab lifetime is global refcounted and must be balanced.

## Test signals
Run GP-only and GP+PP submissions, invalid frame ranges, PLBU heap OOM recovery, nonrecoverable GP errors, MMU fault completion, IRQ sharing, reset timeout injection, and version logging on Mali400/450.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h

## Purpose
Declares the Lima GP IP lifecycle and scheduler pipe setup APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports GP init/fini/resume/suspend plus `lima_gp_pipe_init()` and `lima_gp_pipe_fini()`.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored; implementations operate on IP and device objects.

## Dependencies and integration points
Used by `lima_device.c` to initialize the GP IP and GP scheduler pipe.

## Risks
Signature drift breaks device initialization and scheduler callback installation.

## Test signals
Build coverage and GP task execution validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c

## Purpose
Initializes and flushes Mali L2 cache IP blocks used by GP and PP pipes.

## Important APIs, types, and functions
Exports `lima_l2_cache_init()`, `lima_l2_cache_fini()`, `lima_l2_cache_resume()`, `lima_l2_cache_suspend()`, and `lima_l2_cache_flush()`. Internal helpers are `lima_l2_cache_wait_idle()` and `lima_l2_cache_hw_init()`.

## Control flow
Init filters out `l2_cache2` unless PP4-PP7 are present, initializes the spinlock, reads and logs cache geometry, flushes the cache, enables access and read allocation, and sets max reads. Flush serializes with the IP lock, issues clear-all, waits until command busy clears, and returns timeout errors. Resume redoes hardware init.

## State and persistence
Per-cache lock lives in `ip->data.lock`. Hardware enable, max-read, and cache contents persist until reset, flush, or power loss.

## Dependencies and integration points
Depends on register constants and device IP discovery. Scheduler pipes reference L2 cache IPs and flush them around task execution through scheduler code.

## Risks
Flush timeout indicates stuck hardware and can compromise memory coherency. Cache2 presence detection must match Mali450 PP topology. Locking only serializes driver-issued cache commands.

## Test signals
Probe logs of cache size, L2 flush success, multi-cache Mali450 rendering, suspend/resume reinit, and timeout fault injection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h

## Purpose
Declares the Lima L2 cache lifecycle and flush API.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exports init/fini/resume/suspend plus `lima_l2_cache_flush()`.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here.

## Dependencies and integration points
Used by device IP descriptors and scheduler/cache maintenance paths.

## Risks
Prototype changes affect device init and task cache-management code.

## Test signals
Build coverage and runtime L2 flush tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c

## Purpose
Controls Mali MMU IP blocks for GP and PP pipes: initialization, IRQ fault handling, TLB flush, VM switching, and page-fault recovery.

## Important APIs, types, and functions
Exports `lima_mmu_init()`, `lima_mmu_fini()`, `lima_mmu_resume()`, `lima_mmu_suspend()`, `lima_mmu_flush_tlb()`, `lima_mmu_switch_vm()`, and `lima_mmu_page_fault_resume()`. The `lima_mmu_send_command()` macro writes commands and polls completion/status conditions. IRQ handler is `lima_mmu_irq_handler()`.

## Control flow
Init skips the PP MMU broadcast pseudo-IP, write-tests DTE address masking, registers a shared IRQ, hard-resets the MMU, masks page-fault and bus-error interrupts, installs the empty VM page directory, and enables paging. IRQ logs page faults or bus errors, masks all MMU interrupts, clears status, and notifies the GP or PP scheduler pipe. VM switching stalls the MMU, writes the new page directory, zaps TLB, and disables stall. Page-fault resume hard-resets a fault-active MMU and reinstalls the empty VM.

## State and persistence
MMU state is mostly hardware: DTE page directory address, paging enabled, stall active, interrupt mask/status, and TLB contents. The empty VM belongs to `lima_device`; active VM is selected by scheduler task execution.

## Dependencies and integration points
Depends on Lima VM page-directory DMA, scheduler MMU error callbacks, shared platform IRQs, and MMU register definitions. Device init creates per-processor MMU IPs and optional broadcast MMU pseudo-IP.

## Risks
Fault handling masks interrupts until recovery, so recovery paths must run. VM switch command timeouts can leave the MMU stalled or using the wrong page table. Shared IRQ handling must return `IRQ_NONE` for unrelated interrupts. DTE write test assumes hardware masks low bits to page alignment.

## Test signals
Valid job VM switches, synthetic page faults, read bus errors, TLB flushes, MMU IRQ sharing, page-fault resume, and suspend/resume validate this file. Logs include fault address, bus ID, access type, and command timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h

## Purpose
Declares the Lima MMU lifecycle, TLB, VM switch, and page-fault resume APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_vm`; exposes init/fini/resume/suspend, `lima_mmu_flush_tlb()`, `lima_mmu_switch_vm()`, and `lima_mmu_page_fault_resume()`.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored in the header.

## Dependencies and integration points
Used by device IP descriptors, scheduler pipe task execution, and MMU fault recovery.

## Risks
Signature changes affect GP/PP scheduling and device lifecycle.

## Test signals
Build coverage plus VM switch and fault tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c

## Purpose
Controls the Mali PMU power domains used by Lima, powering GPU IP blocks up during init/resume and down during fini/suspend.

## Important APIs, types, and functions
Exports `lima_pmu_init()`, `lima_pmu_fini()`, `lima_pmu_resume()`, and `lima_pmu_suspend()`. Helpers are `lima_pmu_wait_cmd()`, `lima_pmu_get_ip_mask()`, `lima_pmu_hw_init()`, and `lima_pmu_hw_fini()`.

## Control flow
Hardware init masks PMU interrupts, writes a conservative software delay, reads power status, and powers up any off domains while waiting for command completion. Fini computes a domain mask from GPU type and present PP cores, powers down currently-on domains in that mask, and handles the Mali400 quirk where all-domain powerdown may not generate an interrupt.

## State and persistence
`ip->data.mask` caches the PMU domain mask. Hardware state persists as PMU power status, interrupt clear/mask, software delay, and command state.

## Dependencies and integration points
Depends on Lima device GPU ID, IP presence, and PMU register constants. Called by device IP lifecycle and PM suspend/resume ordering.

## Risks
Wrong masks can power down active or required domains. PMU command timeout prevents reliable power sequencing. The Mali400 interrupt quirk must remain preserved.

## Test signals
Probe/resume power-up, suspend/remove power-down, Mali400 and Mali450 PP topology masks, PMU timeout injection, and clock-frequency stress validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h

## Purpose
Declares Lima PMU lifecycle APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exposes init/fini/resume/suspend.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored here; PMU state is held in `struct lima_ip` and hardware registers.

## Dependencies and integration points
Used by the IP descriptor table in `lima_device.c`.

## Risks
Prototype drift breaks PMU lifecycle setup.

## Test signals
Build coverage and runtime suspend/resume power sequencing validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c

## Purpose
Implements Mali PP (pixel processor) IP blocks, including IRQ handling, reset, task dispatch for Mali400 and Mali450 broadcast/DLBU modes, error handling, version detection, and PP scheduler-pipe callback setup.

## Important APIs, types, and functions
Lifecycle APIs are `lima_pp_init()`, `lima_pp_fini()`, `lima_pp_resume()`, `lima_pp_suspend()`, plus broadcast pseudo-IP functions `lima_pp_bcast_*()`. Pipe APIs are `lima_pp_pipe_init()` and `lima_pp_pipe_fini()`. Internal callbacks include `lima_pp_task_validate()`, `lima_pp_task_run()`, `lima_pp_task_fini()`, `lima_pp_task_error()`, `lima_pp_task_mmu_error()`, and `lima_pp_task_mask_irq()`.

## Control flow
Per-PP IRQs handle error bits, clear interrupts, decrement the outstanding PP task count, and complete the scheduler task when all processors finish. Broadcast IRQ handling loops over participating PP cores, reads status before interrupt state to avoid races, records done bits, and completes when the atomic task count reaches zero. Task validation checks requested PP count and Mali450 padding. Mali450 task run optionally enables DLBU, programs DLBU registers, enables broadcast, waits for reset, writes shared frame/writeback registers, writes per-PP stack/frame data, and starts rendering through broadcast. Mali400 task run programs each PP individually. Error handling hard-resets every PP and resets broadcast masks.

## State and persistence
`ip->data.async_reset` tracks deferred soft resets. `pipe->task` counts active PP cores, `pipe->done` tracks broadcast completions, and `pipe->error` records error state. Hardware PP registers persist frame, writeback, stack, control, interrupt mask/status, and reset probes.

## Dependencies and integration points
Depends on DRM UAPI PP frame layouts, Lima scheduler, DLBU and broadcast modules, VM constants, and register definitions. Device init wires present PP/MMU/L2 triplets into the PP pipe.

## Risks
Broadcast completion races are subtle; status/state ordering is intentional. PP count must not exceed discovered processors. DLBU and broadcast programming are Mali450-specific. Reset timeouts or missed interrupts can hang the scheduler. Task slab lifetime is global refcounted.

## Test signals
Mali400 single/multi-PP rendering, Mali450 broadcast rendering, DLBU and non-DLBU tasks, invalid PP count/padding, PP error IRQs, MMU errors, reset recovery, shared IRQs, and version logging validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h

## Purpose
Declares Lima PP IP lifecycle, broadcast pseudo-IP lifecycle, and PP scheduler pipe APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports `lima_pp_*()`, `lima_pp_bcast_*()`, `lima_pp_pipe_init()`, and `lima_pp_pipe_fini()`.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here.

## Dependencies and integration points
Used by `lima_device.c` IP descriptors and pipe initialization.

## Risks
Prototype drift affects PP device lifecycle and scheduler setup.

## Test signals
Build coverage and PP render submissions validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h -->
