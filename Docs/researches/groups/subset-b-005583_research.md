# subset-b-005583 Research

Grouped research for `subset-b-005583`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.h

Purpose: Central VIA framebuffer hardware contract header. It defines output-device bitmasks (`VIA_CRT`, `VIA_DVP0`, `VIA_DVP1`, `VIA_LVDS1`, `VIA_LVDS2`, `VIA_LDVP0`, `VIA_LDVP1`), DPMS-like state constants, sync polarity flags, CRTC/fetch/start-address formulas, per-chip FIFO thresholds, LCD power-sequence timing formulas, LCD scaling formulas, and the register-field layout structures used by the lower-level modeset code.

Important APIs/types/functions: Core types include `struct io_register`, the IGA2 shadow timing structs, `struct fetch_count`, `struct starting_addr`, `_lcd_pwd_seq_timer`, `_lcd_scaling_factor`, FIFO selector structs, `struct pll_limit`, `struct rgbLUT`, `struct IODATA`, `struct pci_device_id_info`, and `struct via_device_mapping`. Exported prototypes cover timing conversion (`var_to_timing`, `viafb_fill_crtc_timing`), register loading (`viafb_load_reg`, `viafb_load_fetch_count_reg`, `viafb_load_FIFO_reg`, `viafb_write_regx`), output routing and power (`via_set_source`, `via_set_state`, `via_set_sync_polarity`), mode setup (`viafb_setmode`, `viafb_init_chip_info`, `viafb_init_dac`), palette programming, DPA programming, and framebuffer memory queries.

Control flow and state: This header has no executable flow. It supplies the constants and data layouts used by `hw.c`, `lcd.c`, `viafbdev.c`, `via_modesetting.c`, `via_clock.c`, and VT1636 helper code when they translate `fb_var_screeninfo`, panel state, and chip identity into indexed VGA sequencer/CRTC register writes. State is mostly external globals declared here (`viafb_SAMM_ON`, `viafb_dual_fb`, `viafb_LCD_ON`, `viafb_LCD2_ON`, `viafb_DVI_ON`, `viafb_hotplug`) and mutable register programming in hardware.

Dependencies and integration points: Includes `viamode.h`, `global.h`, and `via_modesetting.h`, so it bridges legacy VIA register tables with newer basic modesetting helpers. It depends on Linux `seq_file` for procfs output-device formatting. Device IDs for chipset function-3 PCI devices are consumed by `via-core.c` to discover framebuffer memory sizing. Risks are hardware-programming risk: formulas assume valid positive timings and byte depths, per-chip FIFO constants are undocumented magic values, and exported global state makes ordering-sensitive modeset paths hard to reason about. Test signals are compile coverage, boot on each supported chipset family, mode changes on IGA1/IGA2, DPMS blank/unblank, SAMM/dual-fb operation, and register traces around FIFO/fetch/scaling writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c

Purpose: Implements two helper routines behind the legacy VIA fbdev ioctl interface: driver/chip identity reporting and a simple DVI-vs-CRT hotplug policy.

Important APIs/types/functions: `viafb_ioctl_get_viafb_info(u_long arg)` fills `struct viafb_ioctl_info` with `VIAID`, `PCI_VIA_VENDOR_ID`, a chipset-specific device ID derived from `viaparinfo->chip_info->gfx_chip_name`, and the viafb major/minor version before copying it to userspace. `viafb_ioctl_hotplug(int hres, int vres, int bpp)` senses DVI through `viafb_dvi_sense()`, prefers DVI over CRT when a TMDS transmitter exists, mutates `viafb_DVI_ON`, `viafb_CRT_ON`, `viafb_LCD_ON`, `viafb_DeviceStatus`, and calls `viafb_set_iga_path()`.

Control flow and state: The info path is straight-line except for the chipset switch and `copy_to_user` failure handling. The hotplug path first checks for a real TMDS transmitter, then promotes attached DVI if current status is not DVI, otherwise falls back to CRT when no DVI status is active. The `hres`, `vres`, and `bpp` parameters are unused, so hotplug does not validate the current mode against detected output.

Dependencies and integration points: Included via `global.h` and called from `viafb_ioctl()` in `viafbdev.c`. It depends on global `viaparinfo`, TMDS detection helpers, userspace copy helpers, and the IOCTL constants/types in `ioctl.h`. Risks include an unstable ABI warning from the caller, unsynchronized global output-state mutation, unhandled newer chip names in the device-id switch, no LCD hotplug policy, and limited failure reporting from I2C sense paths. Test signals are ioctl userspace probes for `VIAFB_GET_INFO` and `VIAFB_HOTPLUG`, DVI attach/detach exercises, and validating that `viafb_set_iga_path()` reprograms expected output routing after status changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h

Purpose: Public/driver-private definition of the legacy viafb ioctl ABI. It assigns numeric command values, userspace-facing structures, device bit constants, LCD operation constants, and prototypes for the ioctl helper functions.

Important APIs/types/functions: Command constants include `VIAFB_GET_INFO_SIZE`, `VIAFB_GET_INFO`, `VIAFB_HOTPLUG`, output on/off commands, device/support/connect queries, gamma table commands, panel position/size commands, and `VIAFB_GET_CHIP_INFO`. Data structures include `struct device_t`, `struct viafb_ioctl_info`, `struct viafb_ioctl_mode`, `struct viafb_ioctl_samm`, `struct viafb_driver_version`, `struct viafb_ioctl_lcd_attribute`, `struct viafb_ioctl_setting`, `_UTFunctionCaps`, `_POSITIONVALUE`, and `_panel_size_pos_info`. Prototypes expose `viafb_ioctl_get_viafb_info()` and `viafb_ioctl_hotplug()`.

Control flow and state: This header has no executable flow. It defines the binary layout used by `viafb_ioctl()` to copy state between kernel and userspace. The ABI stores active devices, SAMM state, primary device, LCD panel/mode attributes, resolutions, refresh rates, bpp values, and framebuffer split sizes.

Dependencies and integration points: It is included by `viafbdev.h` and is part of the fbdev ioctl surface. It conditionally defines `__user` for non-kernel parsing contexts, suggesting the header may have historically been used by userspace tools. Risks are ABI brittleness: command numbers are raw constants instead of `_IO*` encodings, many structures use fixed-width-but-not-always-explicit fields and bitfields, several commands in `viafbdev.c` are stubs, and the file itself labels the interface unstable. Test signals are 32/64-bit userspace compatibility checks, ioctl fuzzing for each command's copy length, and regression tests around gamma, SAMM, hotplug, and device state serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.c

Purpose: VIA LCD/LVDS management implementation. It identifies internal and external LVDS transmitters, maps panel IDs to native panel geometry, programs LCD scaling and panel timings, configures integrated LVDS power/backlight sequencing, and selects output interfaces for external/integrated LCD paths.

Important APIs/types/functions: Exported functions include `viafb_init_lcd_size()`, `viafb_lvds_trasmitter_identify()`, `viafb_lcd_set_mode()`, `viafb_lcd_disable()`, `viafb_lcd_enable()`, `viafb_init_lvds_output_interface()`, and `viafb_lcd_get_mobile_state()`. Key internal helpers are `fp_id_to_vindex()`, `lvds_identify_integratedlvds()`, `lvds_register_read()`, `load_lcd_scaling()`, `via_pitch_alignment_patch_lcd()`, `lcd_patch_skew*()`, `integrated_lvds_enable()`, `integrated_lvds_disable()`, `lcd_powersequence_on/off()`, `fill_lcd_format()`, and `check_diport_of_integrated_lvds()`.

Control flow and state: Initialization maps `viafb_lcd_panel_id` into `lvds_setting_info` panel width/height, dual-edge, and dithering flags, then mirrors those settings to the second LVDS info. Transmitter identification probes VT1636 over ports `0x31` and `0x2c`, falls back to integrated CX700 LVDS depending on `viafb_display_hardware_layout`, then probes VT1631 by I2C ID. Mode setting chooses the panel mode table, initializes VT1636 when needed, decides whether IGA2 should scale a lower requested mode up to the panel, loads primary or secondary timing, programs fetch/FIFO/vclock, applies LCD format and DPA/skew patches, and fixes pitch alignment for non-32-byte modes. Enable/disable paths are chip-specific: CLE266 uses software power sequencing, CX700 may control two integrated LVDS channels plus VT1636, VT1636 uses I2C VDD writes, and other chips directly toggle backlight/data-path registers.

Dependencies and integration points: Depends on global `viaparinfo`, VIA register access wrappers, `viafb_get_best_mode()`, `viafb_fill_var_timing_info()`, `var_to_timing()`, `via_set_primary_timing()`, `via_set_secondary_timing()`, FIFO/fetch/vclock loaders, VT1636 helpers, and I2C byte reads. It is called from chip init and modesetting paths in `viafbdev.c`/`hw.c`. Risks include many undocumented register magic values, duplicated `viafb_init_lvds_output_interface` declaration in the header, spelling of `trasmitter`, fallback panel-ID behavior that reads hardware for out-of-range IDs, busy `udelay()` sequences, and global-state coupling for two-LCD layouts. Test signals are panel-ID matrix tests, CX700 integrated LVDS layouts, VT1636 probe/enable/disable, IGA1 vs IGA2 LCD mode setting, scaled vs centered panel modes, suspend/resume backlight state, and visual timing validation on real panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h

Purpose: LCD/LVDS interface header for viafb. It defines LVDS/TMDS chip ID constants, panel ID constants, external LCD state globals, and function prototypes implemented by `lcd.c` and `vt1636.c`.

Important APIs/types/functions: Constants include VT1631/VT3271 device-ID registers and named LCD panel IDs from 640x480 through OLPC 1200x900. Prototypes cover VT1636 power/init helpers, `viafb_lcd_enable()`, `viafb_lcd_disable()`, `viafb_init_lcd_size()`, `viafb_lcd_set_mode()`, `viafb_lvds_trasmitter_identify()`, `viafb_init_lvds_output_interface()`, and `viafb_lcd_get_mobile_state()`.

Control flow and state: There is no runtime flow in this header. It provides the compile-time contract for the LCD path that mutates `lvds_setting_information`, `lvds_chip_information`, and global active-output flags.

Dependencies and integration points: Depends on LVDS and framebuffer types supplied through the broader viafb include chain. It is consumed by `global.h` users, `lcd.c`, `vt1636.c`, and modeset code. Risks include duplicate declaration of `viafb_init_lvds_output_interface`, panel ID names that do not directly match the `fp_id_to_vindex()` switch numbering for every entry, and reliance on global `viafb_LCD*_ON`/`viafb_DVI_ON`. Test signals are compile coverage, panel-ID to geometry validation, and ensuring all prototypes match implementation signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h

Purpose: Common VIA register, bit, display-path, color-depth, output-interface, hardware-layout, CRTC index, LCD method, and small shared type definitions. This is the low-level symbolic map for legacy VGA-style sequencer, CRTC, graphics-controller, DAC, and LCD registers.

Important APIs/types/functions: Defines `BIT0` through `BIT7`, standard table lengths (`StdCR`, `StdSR`, `StdGR`, `StdAR`), IGA identifiers, mode-depth flags, large lists of `SR*` and `CR*` register indices, DAC/LUT ports, logical device constants, output-interface constants (`INTERFACE_DVP0`, `INTERFACE_DFP_LOW`, `INTERFACE_LVDS0LVDS1`, etc.), hardware layouts, CRTC timing indexes, LCD display method constants, `struct crt_mode_table`, and `struct io_reg`.

Control flow and state: No executable flow. The values are consumed by table-driven register writes in `viamode.c`, `hw.c`, `lcd.c`, `viafbdev.c` procfs handlers, and utility/gamma code. State and persistence are hardware state in indexed registers and in static mode tables that refer to these constants.

Dependencies and integration points: Includes `via_modesetting.h` so `struct crt_mode_table` can embed `struct via_display_timing`. It is a foundational dependency for almost every file in `drivers/video/fbdev/via`. Risks are namespace pollution from generic names like `BIT0`, typoed/legacy constants (`LCD_EXPANDSION`), and the lack of type separation between register indices, masks, and values. Test signals are compile coverage, register table application checks, and hardware smoke tests after any register constant change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c

Purpose: Static DPA/skew tuning tables for VIA graphics output pads on VT3324, VT3327, and VT3364 chipsets. These values are selected by pixel-clock range when programming VT1636 LVDS paths and graphics DVP/DFP driving strength.

Important APIs/types/functions: Defines `GFX_DPA_SETTING_TBL_VT3324[6]`, `GFX_DPA_SETTING_TBL_VT3327[]`, and `GFX_DPA_SETTING_TBL_VT3364[6]`. Each entry is a `struct GFX_DPA_SETTING` keyed by `DPA_CLK_RANGE_*` and stores DVP0 skew, DVP0 data/clock driving, DVP1 skew/driving, DFP-high, DFP-low, and reserved/extra fields matching `viafb_set_dpa_gfx()` expectations.

Control flow and state: No executable flow. `vt1636.c` computes a clock-range index and passes one selected table row to `viafb_set_dpa_gfx()` through the LCD skew patch path. The tables are persistent read-only data.

Dependencies and integration points: Includes `global.h` for `struct GFX_DPA_SETTING` and register constants. Integrated by `tblDPASetting.h` and `vt1636.c`. Risks are undocumented magic values, comments with apparent typos around 150 MHz ranges, no compile-time assertion that all tables have six entries, and per-chip values that can visibly break signal integrity if edited. Test signals are DVP0/DVP1/DFP display stability at pixel clocks below 30 MHz through above 150 MHz on affected chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h

Purpose: Header for DPA clock range thresholds and extern declarations of graphics DPA setting tables.

Important APIs/types/functions: Defines `DPA_CLK_30M`, `DPA_CLK_50M`, `DPA_CLK_70M`, `DPA_CLK_100M`, `DPA_CLK_150M`, enum `DPA_RANGE`, and externs for `GFX_DPA_SETTING_TBL_VT3324`, `GFX_DPA_SETTING_TBL_VT3327`, and `GFX_DPA_SETTING_TBL_VT3364`.

Control flow and state: No executable flow. It gives `vt1636.c` the symbolic clock-range indices used to select table rows. State is static read-only table data in the `.c` file.

Dependencies and integration points: Includes `global.h` for `struct GFX_DPA_SETTING`. Risks are array declarations not uniformly sized and tight coupling between enum order and table row order. Test signals are compile coverage and VT1636 skew patch tests across all `DPA_RANGE` branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-core.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-core.c

Purpose: PCI and multifunction core for the VIA framebuffer stack. It owns the single global `viafb_dev`, maps MMIO/framebuffer memory, initializes IRQ control, creates GPIO/I2C/camera platform subdevices, registers PM hooks, optionally exposes VX855 DMA services, and binds the fbdev front end to supported VIA PCI IDs.

Important APIs/types/functions: Exported APIs include `viafb_irq_enable()`, `viafb_irq_disable()`, PM hook registration (`viafb_pm_register`, `viafb_pm_unregister`), and optional camera DMA APIs (`viafb_request_dma`, `viafb_release_dma`, `viafb_dma_copy_out_sg`). Key internal routines include `viafb_int_init()`, `viafb_get_fb_size_from_pci()`, `via_pci_setup_mmio()`, `via_pci_teardown_mmio()`, `via_setup_subdevs()`, `via_teardown_subdevs()`, `via_suspend()`, `via_resume()`, `via_pci_probe()`, `via_pci_remove()`, `via_core_init()`, and `via_core_exit()`.

Control flow and state: Module init checks `fb_modesetting_disabled("viafb")`, calls `viafb_init()`, registers the I2C and GPIO platform drivers, then registers the PCI driver. PCI probe removes conflicting apertures, enables the device, initializes `global_dev` including the OLPC-specific port config, maps engine and framebuffer memory, initializes interrupt state, creates subdevices, and calls `via_fb_pci_probe()` to register fbdev. Remove unwinds subdevices, fbdev, MMIO, and PCI enablement. The optional DMA flow allocates a descriptor chain, programs VX855 DMA registers under a mutex/spinlock combination, waits for completion IRQ, and frees descriptors.

Dependencies and integration points: Depends on PCI, aperture, platform-device, PM, interrupt, DMA, `linux/via-core.h`, `linux/via_i2c.h`, `via-gpio.h`, and viafb globals. It integrates with `via_i2c.c`/`via-gpio.c` via platform devices and with `viafbdev.c` via `via_fb_pci_probe/remove`. Risks include the explicitly single-device global design, partial functionality when engine MMIO mapping fails, framebuffer mapping fallback that silently halves mapped size down to 8 MB, IRQ enable callers needing external `reg_lock`, optional DMA timeout handling that logs but still returns success, and order-sensitive teardown around subdevices and fbdev. Test signals are PCI bind/unbind on each listed device ID, mmap/accel behavior with and without engine MMIO, subdevice creation failures, suspend/resume hook ordering, camera DMA on VX855, and OLPC port config behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c

Purpose: Platform GPIO driver exposing selected VIA display GPIO pins through gpiolib. It maps VIA sequencer-register GPIO pairs into a dynamic `gpio_chip`, provides camera GPIO lookup entries, and restores/enables GPIO ports across PM resume.

Important APIs/types/functions: Local data structures include `struct viafb_gpio` describing register/index/mask-shift and `struct viafb_gpio_cfg` holding the `gpio_chip`, active GPIO mapping, names, and `viafb_dev`. GPIO operations are `via_gpio_set()`, `via_gpio_dir_out()`, `via_gpio_dir_input()`, and `via_gpio_get()`. Platform hooks are `viafb_gpio_probe()` and `viafb_gpio_remove()`, with public module helpers `viafb_gpio_init()` and `viafb_gpio_exit()`.

Control flow and state: Probe receives `viafb_dev` from `via-core.c`, scans `vdev->port_cfg` for ports configured as `VIA_MODE_GPIO`, adds both GPIOs for matching register indices, enables each pair under `reg_lock`, registers a dynamic gpiochip labelled `via-gpio`, adds a lookup table for `viafb-camera`, and registers PM hooks. Set/get/direction operations take `reg_lock` and manipulate output-enable, output-value, and input bits in the backing SR registers. Remove unregisters PM, gpiochip, disables active pairs, and clears `ngpio`.

Dependencies and integration points: Depends on gpiolib, `linux/via-core.h`, platform devices created by `via-core.c`, and register helpers `via_read_reg`, `via_write_reg`, `via_write_reg_mask`. Risks include global singleton `viafb_gpio_config`, assumptions that GPIOs come in pairs, a comment noting input direction may be wrong, lookup table installed even when gpiochip add fails, and shared register bits with I2C mode on some ports. Test signals are gpiochip enumeration, direction/value toggles on ports 25/2c/3d, camera lookup resolution, suspend/resume re-enable, and mixed I2C/GPIO port configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h

Purpose: Minimal public header for the VIA GPIO platform driver.

Important APIs/types/functions: Declares `viafb_gpio_init()` and `viafb_gpio_exit()` for registration/unregistration from `via-core.c`.

Control flow and state: No executable flow. Runtime state lives in `via-gpio.c`'s static `viafb_gpio_config` and in hardware GPIO registers.

Dependencies and integration points: Included by `via-core.c` so the core can bring the GPIO platform driver up before registering PCI devices and tear it down on module exit. Risks are limited to keeping prototypes in sync. Test signals are build coverage and module init/exit sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c

Purpose: I2C auxiliary-device bus infrastructure for display devices connected to VIA outputs. It probes EDID and known encoder/transmitter chips on a given `i2c_adapter`, stores discovered lightweight driver descriptors, and lets callers request a preferred display mode.

Important APIs/types/functions: `via_aux_probe()` allocates `struct via_aux_bus`, initializes its driver list, and calls all probe functions in fixed order: EDID, VT1636, VT1632, VT1631, VT1625, VT1622, VT1621, SiI164, and CH7301. `via_aux_free()` calls per-driver cleanup, unlinks list nodes, frees driver data and descriptors, then frees the bus. `via_aux_get_preferred_mode()` walks the driver list and returns the last non-NULL preferred mode reported by any driver implementing `get_preferred_mode`.

Control flow and state: A bus is created per probed I2C adapter from `viafbdev.c` (`i2c_26`, `i2c_31`, optional `i2c_2C`). Each probe may append a `via_aux_drv` to the bus list. EDID can carry allocated `fb_monspecs` state; most chip probes are stateless identity records. Preferred-mode lookup is list-order dependent and overwrites earlier modes with later ones if multiple drivers report a mode.

Dependencies and integration points: Depends on `via_aux.h`, Linux I2C/list/slab, and the concrete `via_aux_*_probe()` functions. It feeds `parse_mode()` in `viafbdev.c` when no explicit mode is supplied. Risks include no locking around the bus list, no reprobe on hotplug except EDID driver's always-present descriptor, and ambiguous preferred-mode precedence. Test signals are I2C adapter absence, EDID monitor preferred mode selection, multiple transmitter detection, and free-path leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h

Purpose: Shared interface for simple I2C auxiliary display-device probes. It defines bus and driver descriptors, common add/read helpers, public bus lifecycle APIs, and declarations for all concrete probe functions.

Important APIs/types/functions: `struct via_aux_bus` stores an `i2c_adapter` and a list of `via_aux_drv`. `struct via_aux_drv` stores list linkage, target bus/address, display name, private data, cleanup callback, and preferred-mode callback. Inline helpers `via_aux_add()` duplicate and append a driver descriptor, and `via_aux_read()` performs a one-byte-register I2C read transaction. Public functions are `via_aux_probe()`, `via_aux_free()`, `via_aux_get_preferred_mode()`, and concrete probe declarations.

Control flow and state: No standalone runtime flow. The inline helpers are used by every auxiliary probe. State is dynamically allocated per bus and per found driver; optional private data belongs to the driver descriptor and is released by `via_aux_free()`.

Dependencies and integration points: Includes Linux list, I2C, and fb headers. It integrates with `via_i2c.c` adapters and mode selection in `viafbdev.c`. Risks include `via_aux_add()` shallow-copying `data` ownership, fixed 7-bit I2C addressing expectations, no synchronization, and no write/helper abstraction for configuration. Test signals are probe/fail allocation paths, I2C read error handling, and cleanup of EDID modedb private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c

Purpose: Auxiliary probe for Chrontel CH7301 DVI transmitters on VIA display I2C buses.

Important APIs/types/functions: `via_aux_ch7301_probe(struct via_aux_bus *bus)` probes addresses `0x75` and `0x76`; the local `probe()` reads register `0x4B` and accepts the device when the value is `0x17`, then logs and calls `via_aux_add()`.

Control flow and state: Probe is read-only and stateless. A successful match creates a `via_aux_drv` descriptor with name `CH7301 DVI Transmitter`; there are no callbacks or private data.

Dependencies and integration points: Uses `via_aux_read()` from `via_aux.h` and is invoked from `via_aux_probe()`. Risks are minimal ID validation from a single register, no configuration or power sequencing support, and no preferred-mode callback. Test signals are I2C scan results at both addresses and ensuring false positives do not occur on unrelated devices returning `0x17` at register `0x4B`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c

Purpose: Generic EDID auxiliary driver. It reads monitor EDID over DDC, converts it into fbdev monitor specs, keeps modedb private data, and exposes the first detailed mode as a preferred mode.

Important APIs/types/functions: `query_edid()` reads 128 bytes from address `0x50`, calls `fb_edid_to_monspecs()`, validates version/revision, replaces any prior modedb, and stores `struct fb_monspecs` in `drv->data`. `get_preferred_mode()` returns the first mode marked both `FB_MODE_IS_FIRST` and `FB_MODE_IS_DETAILED` when `FB_MISC_1ST_DETAIL` is present. `cleanup()` destroys the modedb. `via_aux_edid_probe()` always adds an EDID driver descriptor after an initial query.

Control flow and state: Unlike chip probes, EDID always installs a driver so connected/disconnected displays can be represented by a descriptor even if the first read fails. The only persistent state is the allocated `fb_monspecs` and its mode database. Cleanup intentionally frees the modedb but the descriptor's `data` allocation is released by `via_aux_free()`.

Dependencies and integration points: Depends on `../edid.h`, fb EDID helpers, and `via_aux_read()`. `viafbdev.c` uses `via_aux_get_preferred_mode()` to choose a default mode for CRT/DVP1 when module parameters are absent. Risks include single-shot EDID query with no hotplug refresh in this file, accepting only first detailed mode as preferred, no checksum reporting beyond fb helper behavior, and possible NULL mode if the monitor does not set the expected flags. Test signals are monitors with valid/invalid EDID, no-display DDC reads, preferred-mode fallback, and leak checks around repeated bus free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c

Purpose: Auxiliary probe for Silicon Image SiI 164 PanelLink transmitters.

Important APIs/types/functions: `via_aux_sii164_probe()` scans 7-bit I2C addresses `0x38` through `0x3F`. Local `probe()` reads four bytes at register `0x00` and matches the exact ID sequence `{0x01, 0x00, 0x06, 0x00}` before adding a stateless `via_aux_drv` descriptor.

Control flow and state: Read-only probe loop; successful detection persists only as a bus-list descriptor with the name `SiI 164 PanelLink Transmitter`.

Dependencies and integration points: Invoked by `via_aux_probe()` and depends on `via_aux_read()`. Risks are no programming support after detection, no preferred-mode callback, and scan cost/noise across eight addresses. Test signals are detection on boards with SiI164, non-detection on absent buses, and no collision with VT1631 address `0x38` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c

Purpose: Auxiliary probe for VIA VT1621(M) TV encoders.

Important APIs/types/functions: `via_aux_vt1621_probe()` reads register `0x1B` from address `0x20` and matches value `0x02`. On success it logs and adds a stateless `via_aux_drv` named `VT1621(M) TV Encoder`.

Control flow and state: Single-address, single-register identity check with no private data and no callbacks.

Dependencies and integration points: Called from `via_aux_probe()` after newer LVDS/DVI probes. Risks are weak ID validation, no mode enumeration or TV-standard control, and no configuration path after discovery. Test signals are I2C probe success/failure at `0x20` and absence of false positives with other VT162x devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c

Purpose: Auxiliary probe for VIA VT1622(M) digital TV encoders.

Important APIs/types/functions: `via_aux_vt1622_probe()` probes addresses `0x20` and `0x21`; local `probe()` reads register `0x1B` and matches value `0x03`, then adds a `VT1622(M) Digital TV Encoder` descriptor.

Control flow and state: Stateless read-only detection. No configuration, cleanup, or preferred-mode callback is installed.

Dependencies and integration points: Invoked by `via_aux_probe()` and uses `via_aux_read()`. Risks are single-register identity, overlap with other VT162x addresses, and discovery without usable TV encoder programming in this driver slice. Test signals are I2C detection on boards with either address strap and non-detection on VT1621/VT1625 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c

Purpose: Auxiliary probe for VIA VT1625(M) HDTV encoders.

Important APIs/types/functions: `via_aux_vt1625_probe()` checks addresses `0x20` and `0x21`; local `probe()` reads register `0x1B`, accepts value `0x50`, logs the address, and adds a stateless aux driver descriptor.

Control flow and state: Stateless, read-only I2C identity probe. There is no cleanup or mode callback.

Dependencies and integration points: Called from `via_aux_probe()`. Risks include no HDTV mode programming, no output-state integration, and possible stale detection if a bus device aliases the same ID register. Test signals are probe coverage on both possible addresses and no false positives on VT1621/VT1622 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c

Purpose: Auxiliary probe for VIA VT1631 LVDS transmitters.

Important APIs/types/functions: `via_aux_vt1631_probe()` reads four ID bytes from address `0x38` and matches `{0x06, 0x11, 0x91, 0x31}` before adding a stateless `via_aux_drv` named `VT1631 LVDS Transmitter`.

Control flow and state: Single exact-ID read; successful detection is represented as a bus-list descriptor only.

Dependencies and integration points: Called by `via_aux_probe()`. Separate legacy LVDS detection in `lcd.c` also knows about VT1631 via target address and device ID. Risks include split responsibility between aux detection and active LCD setup, no preferred-mode/config callbacks, and address overlap with other DVI/LVDS transmitters. Test signals are I2C detection on VT1631 panels and ensuring `lcd.c` still configures the active LVDS chip state consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c

Purpose: Auxiliary probe for VIA VT1632 DVI transmitters.

Important APIs/types/functions: `via_aux_vt1632_probe()` scans addresses `0x08` through `0x0F`; local `probe()` matches the four-byte ID `{0x06, 0x11, 0x92, 0x31}` and adds a descriptor named `VT1632 DVI Transmitter`.

Control flow and state: Stateless scan loop, no private data or callbacks beyond detection.

Dependencies and integration points: Called from `via_aux_probe()`. TMDS output support elsewhere checks chip information and DVI sense, so this aux probe is primarily discovery/logging and possible future extension. Risks include scan overhead across eight addresses and no configuration state created from the detected transmitter. Test signals are detection on address-strapped VT1632 boards and lack of disruption to EDID/DDC reads on the same bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c

Purpose: Auxiliary probe for VIA VT1636 LVDS transmitters on an I2C bus.

Important APIs/types/functions: `via_aux_vt1636_probe()` reads four bytes at address `0x40` and matches `{0x06, 0x11, 0x45, 0x33}`. On match it logs and adds a stateless `via_aux_drv` named `VT1636 LVDS Transmitter`.

Control flow and state: Stateless read-only detection. Active VT1636 programming is implemented separately in `vt1636.c`; this file only records presence on the aux bus.

Dependencies and integration points: Invoked from `via_aux_probe()` before VT1632/VT1631/TV encoder probes. Risks are split probe/programming paths with different address conventions (`via_aux` uses 7-bit `0x40`, legacy VT1636 code uses its target address constant), no preferred-mode callback, and no cleanup needs. Test signals are I2C detection and consistency with `viafb_lvds_identify_vt1636()` on ports `0x31`/`0x2C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c

Purpose: Chip-family-specific clock and PLL programming for VIA display engines. It fills a `struct via_clock` function table with operations for primary/secondary display clocks, PLL state, PLL programming, and engine PLL programming.

Important APIs/types/functions: Encoders include `cle266_encode_pll()`, `k800_encode_pll()`, and `vx855_encode_pll()`. Low-level setters program primary, secondary, and engine PLL encoded values through SR registers. State/source helpers include `set_primary_pll_state()`, `set_secondary_pll_state()`, `set_engine_pll_state()`, `set_primary_clock_state()`, `set_secondary_clock_state()`, `set_clock_source_common()`, `set_primary_clock_source()`, and `set_secondary_clock_source()`. `via_clock_init()` selects the correct function table for CLE266/K400, K800-through-VX800, or VX855/VX900, with OLPC overriding display clock state setters to no-ops.

Control flow and state: Runtime callers initialize a `via_clock` object once per chip and then call function pointers during modeset/vclock programming. PLL setters assert reset bits, write encoded multiplier/divisor/rshift bytes, then release reset. Clock/PLL state setters only accept `VIA_STATE_ON` and `VIA_STATE_OFF`; other states are ignored. Undocumented operations log a warning and do not program hardware.

Dependencies and integration points: Depends on `linux/via-core.h`, `via_clock.h`, `global.h`, and `debug.h`. Integrated by chip/modesetting code that needs vclock and engine PLL control. Risks include undocumented dummy handlers for older chips, arithmetic assumptions in PLL encoding, register magic constants, and OLPC-specific no-op behavior to avoid suspend memory corruption. Test signals are pixel-clock accuracy for each chip family, suspend/resume on OLPC XO-1.5, engine acceleration after engine PLL programming, and no warnings on documented paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h

Purpose: Public clock/PLL function-table interface for the VIA framebuffer driver.

Important APIs/types/functions: Defines `enum via_clksrc`, `struct via_pll_config`, `struct via_clock`, inline helpers `get_pll_internal_frequency()` and `get_pll_output_frequency()`, and `via_clock_init()`.

Control flow and state: No standalone flow beyond inline frequency calculations. A `via_clock` instance becomes a chip-specific dispatch table after `via_clock_init()` and is then used by modeset code to program clocks and PLLs.

Dependencies and integration points: Uses Linux fixed-width types and is implemented by `via_clock.c`. Risks include integer division/overflow if reference frequencies or PLL values are invalid, function pointers needing initialization before use, and no explicit error channel for unsupported operations. Test signals are compile coverage, PLL frequency calculations for known configurations, and function-table initialization for each supported `gfx_chip` value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c

Purpose: Platform I2C driver for VIA display I2C/GPIO-backed ports. It creates bit-banged I2C adapters from the port configuration supplied by `via-core.c` and exposes byte read/write helpers for LVDS/TMDS and EDID code.

Important APIs/types/functions: Public helpers are `viafb_i2c_readbyte()`, `viafb_i2c_writebyte()`, `viafb_i2c_readbytes()`, `viafb_find_i2c_adapter()`, `viafb_i2c_init()`, and `viafb_i2c_exit()`. Bit algorithm callbacks are `via_i2c_setscl()`, `via_i2c_getscl()`, `via_i2c_setsda()`, and `via_i2c_getsda()`. Platform hooks are `viafb_i2c_probe()` and `viafb_i2c_remove()`, with `create_i2c_bus()` setting up `i2c_algo_bit_data`.

Control flow and state: Probe stores the singleton `i2c_vdev`, scans up to `VIAFB_NUM_PORTS`, and creates adapters only for configs with a nonzero type and `VIA_MODE_I2C`. Each adapter uses the same static `via_i2c_par[]` entry for algorithm, adapter, and active flag. Read/write helpers check `is_active`, build I2C messages using `target_addr / 2`, and normalize successful transfer counts to zero. Remove deletes active adapters.

Dependencies and integration points: Depends on platform devices from `via-core.c`, `linux/via-core.h`, `linux/via_i2c.h`, I2C bit-bang support, delay, and register helpers protected by `vdev->reg_lock`. Used by `via_aux.c`, `lcd.c`, `vt1636.c`, and DVI/LVDS sensing code. Risks include singleton state, old 8-bit target-address convention (`/ 2`), very short timeout (`2`), shared GPIO/I2C register bits, and no per-adapter locking beyond register access. Test signals are adapter registration, EDID reads, VT1636/VT1631 ID reads, GPIO-backed I2C on port 2C, inactive adapter `-ENODEV`, and removal without stale active flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c

Purpose: Basic CRTC register programming helpers for primary and secondary VIA display engines, plus start address, pitch, and color-depth programming.

Important APIs/types/functions: Implements `via_set_primary_timing()`, `via_set_secondary_timing()`, `via_set_primary_address()`, `via_set_secondary_address()`, `via_set_primary_pitch()`, `via_set_secondary_pitch()`, `via_set_primary_color_depth()`, and `via_set_secondary_color_depth()`.

Control flow and state: Timing setters convert logical `via_display_timing` values into raw register encodings, split high bits across legacy VGA CRTC extension registers, and write them in the order required by each engine. Primary timing unlocks CRTC register `0x11`, writes standard and extended timing bits, relocks it, and toggles timing control reset. Secondary timing writes the secondary CRTC register block directly. Address and pitch helpers encode framebuffer offsets/pitch into register fields; secondary address is quadword aligned. Color-depth helpers map fb depths to hardware bit patterns and warn on unsupported depths.

Dependencies and integration points: Depends on `via_modesetting.h`, `share.h`, `debug.h`, and `via_write_reg*` helpers. Called by LCD, CRT/DVI, pan-display, and mode-setting code in the viafb stack. Risks are off-by-one/shift errors in raw timing packing, no value range validation inside these helpers, unsupported 15-bpp secondary depth, and direct hardware mutation without locking in the helper itself. Test signals are register traces for known modes, fbdev mode switches, panning on both engines, color-depth changes, and secondary engine alignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h

Purpose: Public header for the basic VIA modesetting helper layer.

Important APIs/types/functions: Defines pitch alignment constants `VIA_PITCH_SIZE` and `VIA_PITCH_MAX`, `struct via_display_timing`, and prototypes for timing, address, pitch, and color-depth setters for primary and secondary engines.

Control flow and state: No standalone flow. The struct carries logical timing values that callers convert from `fb_var_screeninfo` or `fb_videomode` before register programming.

Dependencies and integration points: Included by `share.h`, `hw.h`, and callers such as `lcd.c` and `viafbdev.c`. Risks are lack of explicit units/range in `struct via_display_timing` and reliance on callers to validate pitch against `VIA_PITCH_MAX`. Test signals are compile coverage and mode-setting tests that exercise each exported setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c

Purpose: Miscellaneous utility implementation for device support/connection reporting, LCD expansion support reporting, and gamma table access used by viafb ioctls.

Important APIs/types/functions: `viafb_get_device_support_state()` reports CRT plus DVI when VT1632 TMDS is known and LCD when VT1631 LVDS is known. `viafb_get_device_connect_state()` reports CRT, DVI when `viafb_dvi_sense()` succeeds, and LCD when `viafb_lcd_get_mobile_state()` reports a mobile panel. `viafb_lcd_get_support_expand_state()` maps panel IDs to native sizes and checks whether the current mode is smaller. Gamma APIs are `viafb_set_gamma_table()`, `viafb_get_gamma_table()`, and `viafb_get_gamma_support_state()`.

Control flow and state: Gamma set enables the chip-specific gamma bit, saves SR1A, selects IGA1 gamma, writes 256 RGB LUT entries through DAC ports, optionally selects IGA2 and writes the same table when multiple devices are active and the chip supports it, then restores SR1A. Gamma get reads 256 entries from IGA1. Support/connect queries synthesize bitmasks from global chip/output state and hardware sense helpers.

Dependencies and integration points: Called by `viafb_ioctl()` in `viafbdev.c`. Depends on global `viaparinfo`, `viafb_DeviceStatus`, DVI sense, LCD mobile BIOS probe, DAC I/O ports, and register helpers. Risks include direct port I/O with no locking, active-device counting over a global bitmask, no gamma support for some later chips listed elsewhere, 8-bpp no-op behavior, and LCD support tied narrowly to VT1631. Test signals are ioctl gamma set/get round trips, SAMM gamma on both IGAs, DVI sense/connect state, mobile BIOS detection, and panel expansion query for every panel ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h

Purpose: Header for viafb utility/query and gamma helper functions.

Important APIs/types/functions: Declares device support/connect queries, LCD expansion support query, gamma set/get, and gamma support-state reporting.

Control flow and state: No standalone flow. Implementations mutate or read hardware LUT state and global device/chip state.

Dependencies and integration points: Included where ioctl handling needs these helpers. Risks are prototype drift and the absence of explicit locking/error details in the API. Test signals are compile coverage and ioctl paths that call each declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.c

Purpose: Main fbdev front end for VIA UniChrome/Chrome9 graphics. It parses module/boot parameters, validates and applies framebuffer modes, exposes fb_ops, handles legacy ioctls, manages dual-fb/SAMM memory split, registers procfs controls, probes auxiliary I2C buses, registers framebuffer devices, and connects PM hooks to the VIA core.

Important APIs/types/functions: Public entry points used by `via-core.c` are `viafb_init()`, `viafb_exit()`, `via_fb_pci_probe()`, and `via_fb_pci_remove()`. The `fb_ops` table implements open/release, default IOMEM read/write/mmap, `viafb_check_var()`, `viafb_set_par()`, palette, pan, blank, accelerated fill/copy/imageblit, hardware cursor, ioctl, and sync. Major internal helpers include color/fix setup, `parse_active_dev()`, port parsing, procfs output-device update handlers, `parse_mode()`, suspend/resume hooks, I2C auxiliary probe/free, and device-setting serialization.

Control flow and state: Module init optionally parses boot options, validates requested modes/bpp/active devices, and defers hardware registration to PCI probe. PCI probe allocates `fb_info` plus shared/private state, probes I2C aux buses, sets LCD/DVI port parameters, initializes chip info, records framebuffer/MMIO resources from `viafb_dev`, configures acceleration if available, splits memory for secondary framebuffer, resolves default modes from parameters, EDID, OLPC defaults, or 640x480 fallback, validates vars, allocates cmap, registers one or two framebuffers, creates procfs entries, initializes DAC, and registers PM hooks. Runtime `set_par` updates global bpp/refresh/device settings, calls `viafb_setmode()`, and pans to the selected offset. Remove unregisters framebuffers, procfs, aux buses, cmap, and fb_info.

Dependencies and integration points: Depends on fbdev core, procfs/seq_file, module params, `linux/via-core.h`, `linux/via_i2c.h`, aux infrastructure, acceleration, hardware/modesetting/LCD/DVI utilities, and many global variables from `global.h`. Risks include the legacy unstable ioctl ABI, heavy global state (`viafbinfo`, `viaparinfo`, output flags), no broad locking around procfs/ioctl modeset state changes, partial stubs for panel position/size/caps, possible ordering pitfalls in dual-fb registration/unwind, hardware cursor limitations on LCD/IGA2, and direct register control from procfs when enabled. Test signals are boot parameter parsing, single/dual framebuffer registration, SAMM memory size reporting, fbset mode changes, pan/cmap/blank/ioctl behavior, acceleration fallback, hardware cursor paths, procfs output-device changes, suspend/resume, and remove/unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h

Purpose: Main private header for the viafb fbdev front end. It aggregates key headers, declares driver version, shared/private framebuffer state structures, global output flags, LVDS I2C helpers, and PCI-facing fbdev entry points.

Important APIs/types/functions: `struct viafb_shared` holds IGA output masks, procfs entries, `viafb_dev`, probed aux I2C buses, shared TMDS/LVDS/chip info, hardware cursor/VQ offsets, and the acceleration `hw_bitblt` callback. `struct viafb_par` holds per-framebuffer depth, VRAM offset, physical framebuffer accounting, IGA path, pointer to shared state, and deprecated direct pointers into shared chip settings. Prototypes include `viafb_gpio_i2c_read_lvds()`, `viafb_gpio_i2c_write_mask_lvds()`, `via_fb_pci_probe()`, `via_fb_pci_remove()`, `viafb_init()`, and `viafb_exit()`.

Control flow and state: No executable flow in the header. The structures describe persistent per-driver and per-fb state allocated by `via_fb_pci_probe()` and later consumed by fb_ops, LCD/DVI setup, acceleration, procfs, and PM paths.

Dependencies and integration points: Includes Linux fb/proc/spinlock headers and viafb subsystem headers (`via_aux.h`, `ioctl.h`, `share.h`, `chip.h`, `hw.h`). It is the main contract between `via-core.c` and `viafbdev.c`. Risks include global singleton assumptions, duplicated state pointers marked deprecated, and storing physical framebuffer addresses in `unsigned int`. Test signals are structure layout compile coverage, dual-fb state separation, and correct shared pointer use after framebuffer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c

Purpose: Static mode/register table repository for VIA fbdev plus helpers to select the closest refresh-rate mode for a requested resolution.

Important APIs/types/functions: Defines common register initialization arrays such as `CN400_ModeXregs`, `CN700_ModeXregs`, `KM400_ModeXregs`, `CX700_ModeXregs`, `VX855_ModeXregs`, and `CLE266_ModeXregs`, a small patch table for 1024x768, `VPIT`, standard `viafb_modes[]`, reduced-blanking `viafb_rb_modes[]`, exported table length variables, `viafb_get_best_mode()`, and `viafb_get_best_rb_mode()`.

Control flow and state: The data tables are persistent read-only/static initialization sources used during chipset/mode setup. `get_best_mode()` linearly scans a mode array for matching xres/yres and returns the entry whose refresh is closest to the requested refresh. No allocation or hardware writes happen in this file.

Dependencies and integration points: Includes `linux/via-core.h` and `global.h`; exported arrays are consumed by hardware setup code. `viafbdev.c` calls `viafb_get_best_mode()` during mode validation/defaulting, while LCD code uses it for native panel modes. Risks include duplicate/near-duplicate modes, static register magic values, external declaration of `VX800_ModeXregs` in the header without a definition in this file, and no pixel-clock/chip capability filtering in best-mode selection. Test signals are requested resolution/refresh lookup coverage, register table application on each chipset family, and fbdev mode validation for all listed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h

Purpose: Header for legacy VIA mode/register tables and mode lookup helpers.

Important APIs/types/functions: Defines `struct VPITTable` and `struct patch_table`, externs for table lengths and mode register arrays, extern `VPIT`, and prototypes for `viafb_get_best_mode()` and `viafb_get_best_rb_mode()`.

Control flow and state: No runtime flow. It exposes static register/mode table state stored in `viamode.c`.

Dependencies and integration points: Includes `global.h`, which supplies `StdSR`, `StdGR`, `StdAR`, and `struct io_reg` through the include chain. Risks are extern/table drift, especially `VX800_ModeXregs` being declared here while this source group only defines `VX855_ModeXregs`, and global mutable `int` table lengths rather than constants. Test signals are link-time coverage and mode table consumers compiling against all externs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.c

Purpose: Legacy active-programming support for VIA VT1636 LVDS transmitters. It provides I2C masked register access, VT1636 initialization/power control, device identification, and chipset-specific DPA/skew patching used by the LCD path.

Important APIs/types/functions: Public helpers include `viafb_gpio_i2c_read_lvds()`, `viafb_gpio_i2c_write_mask_lvds()`, `viafb_init_lvds_vt1636()`, `viafb_enable_lvds_vt1636()`, `viafb_disable_lvds_vt1636()`, `viafb_lvds_identify_vt1636()`, and skew patch functions for VT3324, VT3327, and VT3364. Static data includes `common_init_data`, single/dual channel enable masks, dithering masks, and VDD on/off masks. Internal helpers include `get_clk_range_index()` and `set_dpa_vt1636()`.

Control flow and state: Identification sets `lvds_chip_target_addr`, reads vendor and chip IDs, and records `VT1636_LVDS` in `viaparinfo->chip_info->lvds_chip_info` on success. Initialization writes common power sequence/control registers, selects single vs dual channel, and enables/disables dithering based on `lvds_setting_information`. Enable/disable only toggles VDD. Skew patching selects a graphics DPA table by `vclk` range, calls `viafb_set_dpa_gfx()`, and for some chips also programs transmitter DPA registers `0x08`/`0x09`.

Dependencies and integration points: Depends on `viafb_i2c_readbyte/writebyte`, `tblDPASetting` tables, `global.h`, and LCD mode setup in `lcd.c`. Risks include masked writes ignoring I2C return codes, global mutation during detection, fixed VT1636 I2C target assumptions, and signal-integrity magic values tied to chipset/panel combinations. Test signals are VT1636 ID read on ports 0x31/0x2c, single/dual channel and dithering register verification, VDD power transitions, and display stability across DPA clock ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.h

Purpose: Header for VT1636 LVDS identification, initialization, power, and skew patch helpers.

Important APIs/types/functions: Declares `viafb_lvds_identify_vt1636()`, `viafb_init_lvds_vt1636()`, `viafb_enable_lvds_vt1636()`, `viafb_disable_lvds_vt1636()`, and skew patch functions for VT3324/VT3327/VT3364.

Control flow and state: No executable flow. The declared routines read/write VT1636 I2C state and graphics DPA registers through global viafb chip/LVDS structures.

Dependencies and integration points: Includes `chip.h` for LVDS types and constants. Used by `lcd.c` to detect and program external LVDS. Risks are prototype drift and close coupling to legacy global `viaparinfo` state despite parameterized signatures. Test signals are compile coverage and all VT1636 branches in LCD mode setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/vt1636.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.c

Purpose: Standalone fbdev driver for VIA/WonderMedia VT8500 LCD controller. It binds as a device-tree platform driver, allocates DMA framebuffer and palette memory, programs LCD timing registers from OF display timings, implements basic fb_ops, and supports wait-for-vsync through an interrupt waitqueue.

Important APIs/types/functions: Main fb operations are `vt8500lcd_set_par()`, `vt8500lcd_setcolreg()`, `vt8500lcd_ioctl()`, `vt8500lcd_pan_display()`, and `vt8500lcd_blank()`, collected in `vt8500lcd_ops` with WMT GE accelerated fill/copy and sync hooks. Platform lifecycle is `vt8500lcd_probe()` and `vt8500lcd_remove()`. IRQ handling is `vt8500lcd_handle_irq()`. `chan_to_field()` converts 16-bit color channel values into fb bitfields.

Control flow and state: Probe allocates `struct vt8500lcd_info` plus pseudo palette, requests and maps MMIO, reads OF display timings and `bits-per-pixel`, allocates a double-height coherent framebuffer and coherent palette buffer, requests IRQ, allocates cmap, converts the native OF mode into `fb_var_screeninfo`, calls `set_par()`, programs framebuffer and palette base registers, registers the framebuffer, and enables the controller. `set_par()` derives visual/line length/color fields, chooses a hardware bpp code from `bpp_values`, disables the controller, waits for idle, writes horizontal/vertical timing registers, sets base control, and reenables. IOCTL unmasks EOF interrupt for `FBIO_WAITFORVSYNC`, waits up to `HZ/10`, then masks interrupts again. Pan-display writes the framebuffer offset register.

Dependencies and integration points: Depends on platform/of display timing APIs, DMA coherent allocation, fbdev core, IRQ/waitqueue primitives, I/O memory mapping, and `wmt_ge_rops` acceleration. Device-tree match is `via,vt8500-fb`. Risks include manual `request_mem_region`/`ioremap` instead of devm for MMIO resource cleanup, framebuffer free missing in remove path for `fb.screen_buffer`, fixed double-buffer allocation, busy wait for controller idle in `set_par`, blanking only affecting pseudocolor modes, no `.fb_mmap`, and limited bpp validation. Test signals are OF probe with valid/invalid timing and bpp, fbcon registration, pan between the two virtual pages, `FBIO_WAITFORVSYNC` timeout/interrupt wake, palette writes in pseudocolor modes, remove/unbind leak checks, and WMT GE accelerated fill/copy smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h

Purpose: Private header for the VT8500 LCD fbdev driver, defining the driver state container and supported bits-per-pixel hardware code mapping.

Important APIs/types/functions: `struct vt8500lcd_info` embeds `struct fb_info`, MMIO `regbase`, coherent palette CPU/physical address and size, and a waitqueue used for vsync waits. `bpp_values[]` maps hardware bpp selector indices to supported bpp values: 1, 2, 4, 8, 12, 16, 18, and 24.

Control flow and state: No standalone flow. `vt8500lcdfb.c` uses `container_of()` to recover this structure from `fb_info` and stores all persistent per-device runtime state here.

Dependencies and integration points: Relies on fbdev, I/O memory, DMA address, and waitqueue types included by the `.c` before this header. Risks include defining a non-const `static int bpp_values[]` in a header, no include guard, and header dependence on prior includes. Test signals are compile coverage, bpp selector mapping in `vt8500lcd_set_par()`, and static-analysis warnings for header-defined mutable data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h -->
