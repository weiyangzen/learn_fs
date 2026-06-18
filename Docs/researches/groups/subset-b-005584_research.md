# Research Group subset-b-005584

This grouped report covers the requested source files in manifest order. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8623fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8623fb.c

Purpose: PCI fbdev driver for the VIA VT8623/CLE266 integrated graphics core. It exposes a legacy framebuffer over PCI BAR memory, programs SVGA/VGA timing registers directly, supports text, 4/8-bit pseudocolor, 16-bit RGB565, and 32-bit truecolor modes, and preserves VGA state while the framebuffer is open.

Important APIs, types, and functions: `struct vt8623fb_info` stores MMIO, saved `vgastate`, open reference count, mutex, and pseudo-palette. Format/timing descriptions are in `vt8623fb_formats`, `vt8623_pll`, and `vt8623_*_regs`. Fbdev operations are implemented by `vt8623fb_open`, `vt8623fb_release`, `vt8623fb_check_var`, `vt8623fb_set_par`, `vt8623fb_setcolreg`, `vt8623fb_blank`, `vt8623fb_pan_display`, `vt8623fb_fillrect`, and `vt8623fb_imageblit`. PCI lifecycle is `vt8623_pci_probe`, `vt8623_pci_remove`, PM suspend/resume hooks, and module init/exit.

Control flow: module init checks `fb_modesetting_disabled("vt8623fb")`, reads boot/module mode options, and registers a PCI driver for VIA device ID `0x3122`. Probe rejects secondary VGA devices, removes conflicting aperture users, allocates `fb_info`, enables and reserves PCI regions, maps framebuffer with write-combining and MMIO normally, computes VGA I/O base, detects VRAM size, selects the startup mode with `fb_find_mode`, allocates a cmap, registers the framebuffer, and optionally enables write combining through `arch_phys_wc_add`. Mode setting validates format, virtual resolution, memory size, timings, and non-interlace constraints before programming VGA/SVGA sequencer, CRT, graphics, PLL, timing, fetch, offset, and display enable registers. Open saves VGA mode/fonts/cmap on the first opener; release restores on the last close. Resume reprograms current fb state only if there was an active opener.

State and persistence: persistent driver state is in `fb_info->par`, PCI drvdata, hardware registers, the pseudo-palette, and the saved VGA snapshot. `ref_count` under `open_lock` gates save/restore and suspend behavior. The framebuffer memory contents are cleared during `set_par`; no disk persistence exists. Module parameters `mode_option`/`mode` and `mtrr` affect startup mode and write-combining.

Dependencies and integration points: depends on fbdev core, PCI, aperture conflict removal, SVGA helper APIs, `vgastate`, VGA I/O helpers, console locking for PM, and architecture write-combining hooks. It integrates with fbcon through fbdev ops and tile ops for text mode, and with global modeset disabling through `fb_modesetting_disabled`.

Risks: register programming is highly hardware-specific and lacks VGA arbitration, so secondary devices are ignored. The custom 4-bpp blitters assume 8-pixel alignment and fall back for other cases. Incorrect VRAM detection falls back to 16 MiB. `save_vga`/`restore_vga` failures are not deeply surfaced. Suspend/resume only handles active users and does not restore if no framebuffer opener exists. Legacy MMIO/I/O paths and no PCI disable calls are compatibility-sensitive.

Test signals: build with `CONFIG_FB_VT8623`; boot with and without `vt8623fb.mode=` and `nomodeset`; probe on primary CLE266 hardware; exercise fbcon text, 4/8/16/32-bpp modes, panning, colormap updates, blank/DPMS states, open/close VGA restoration, suspend/resume, and aperture conflict handling. Validate no register write regressions with mode switches and console takeover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8623fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb.c

Purpose: platform framebuffer driver for WonderMedia WM8505 display hardware. It creates a DMA-backed virtual framebuffer from devicetree display timings, programs GOVR display/timing registers, exposes a contrast sysfs attribute, and uses the WonderMedia GE ROP helpers for accelerated fill/copy when available.

Important APIs, types, and functions: `struct wm8505fb_info` embeds `struct fb_info` and stores `regbase` plus contrast. Main helpers are `wm8505fb_init_hw`, `wm8505fb_set_timing`, `wm8505fb_set_par`, `wm8505fb_setcolreg`, `wm8505fb_pan_display`, `wm8505fb_blank`, `contrast_show`, and `contrast_store`. `wm8505fb_ops` wires DMA-memory default read/write, GE `fillrect`/`copyarea`, `sys_imageblit`, `wmt_ge_sync`, pan, blank, and IOMEM mmap. Probe/remove are handled by `wm8505fb_probe` and `wm8505fb_remove`.

Control flow: platform probe allocates `wm8505fb_info` plus a 16-entry pseudo-palette, maps register resource 0, parses `display-timings`, reads native fb videomode and `bits-per-pixel`, allocates two screens worth of coherent DMA memory, fills `fb_info`, sets default contrast, calls `wm8505fb_set_par`, allocates a 256-entry cmap, initializes hardware registers, stores drvdata, and registers the framebuffer. `set_par` accepts 16-bpp RGB565 or 32-bpp RGB888 layouts, updates `fix.line_length` and visual state, programs timings, and writes packed contrast to the hardware. Blank disables vertical sync except for unblank, which re-enables timings. Pan writes x/y offsets to GOVR registers.

State and persistence: state lives in devm-managed driver memory, coherent framebuffer memory, the pseudo-palette, sysfs contrast value, and hardware registers. Framebuffer memory is volatile and allocated at probe; no persistent storage exists. Contrast changes are immediate and survive until driver remove or hardware reset only.

Dependencies and integration points: depends on platform bus, OF display timing parsing, fbdev core, DMA coherent allocation, `wm8505fb_regs.h` register offsets, and `wmt_ge_rops` acceleration. The compatible string is `wm,wm8505-fb`; `dev_groups` publishes the sysfs contrast attribute.

Risks: `display_timings` returned by `of_get_display_timings` is not released in this file, which can matter if the helper expects caller ownership. The driver assumes `bits-per-pixel` is 16 or 32; other values fall through with partially configured format. It clears a broad 0x200-byte register window, including unknown registers by design. Hardware programming contains acknowledged "black magic" constants. GE helpers use global engine state and must be present/initialized for true acceleration.

Test signals: build with WM8505 fb and OF display timing support; probe with a DT node containing `display-timings` and `bits-per-pixel`; verify 16/32-bpp color, panning, blank/unblank, sysfs contrast read/write bounds, mmap/read/write, and accelerated rect/copy behavior with and without `CONFIG_FB_WMT_GE_ROPS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb_regs.h

Purpose: register offset header for WM8505 GOVR framebuffer hardware. It centralizes offsets used by `wm8505fb.c` for framebuffer base addresses, color space selection, contrast, panning, virtual resolution, timing generator, and DVO/output setup.

Important APIs, types, and functions: no functions or types are defined. Public macros include `WMT_GOVR_COLORSPACE`, `WMT_GOVR_COLORSPACE1`, `WMT_GOVR_CONTRAST`, `WMT_GOVR_BRGHTNESS`, `WMT_GOVR_FBADDR`, `WMT_GOVR_FBADDR1`, `WMT_GOVR_XPAN`, `WMT_GOVR_YPAN`, `WMT_GOVR_XRES`, `WMT_GOVR_XRES_VIRTUAL`, `WMT_GOVR_MIF_ENABLE`, `WMT_GOVR_FHI`, `WMT_GOVR_REG_UPDATE`, `WMT_GOVR_DVO_SET`, `WMT_GOVR_TG`, and timing offsets.

Control flow: not applicable; this file is included by the framebuffer driver and supplies constants for direct `readl`/`writel` register access.

State and persistence: no state. Hardware state is created by consumers writing the defined offsets.

Dependencies and integration points: integrated directly with `wm8505fb.c`; the comments encode partial reverse-engineered meaning of some bits, especially color space and DVO setup.

Risks: offsets and bit meanings are hardware-specific and partially documented. The spelling typo in the framebuffer comment is harmless, but incomplete semantic coverage increases the risk of accidental misuse by future code.

Test signals: compile coverage through `wm8505fb.c`; runtime validation is register behavior during WM8505 probe, mode set, contrast, pan, and blank operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.c

Purpose: WonderMedia Graphics Engine raster-operation acceleration provider. It exports fbdev-compatible fillrect, copyarea, and sync helpers that program a global GE MMIO block for solid fills and screen-to-screen copies.

Important APIs, types, and functions: exported symbols are `wmt_ge_fillrect`, `wmt_ge_copyarea`, and `wmt_ge_sync`. Internal helpers include `pixel_to_pat`, `wmt_ge_rops_probe`, and `wmt_ge_rops_remove`. Register offsets define command, depth, rop, source/destination geometry, pattern color, enable, interrupt, and status registers.

Control flow: a platform driver matching `wm,prizm-ge-rops` maps one MMIO resource into the file-global `regbase`, enables the engine, and refuses a second engine. Fill operations resolve true/direct-color values through the pseudo-palette, expand them to a hardware pattern, synchronize previous work, program destination geometry and rop code (`0xf0` copy or `0x5a` XOR), then fire the command. Copy operations synchronize, program source and destination rectangles, set rop `0xcc`, and fire. Sync busy-waits for the status busy bit to clear with a fixed loop limit.

State and persistence: the only driver state is global `regbase`, plus the GE hardware registers. There is no per-client state, no command queue, and no persistence beyond MMIO state. The accelerated operations depend on caller-provided `fb_info`.

Dependencies and integration points: depends on platform bus, OF, fbdev structures, eventless MMIO polling, and consumers such as `wm8505fb.c`. The header provides software fallbacks when disabled.

Risks: single global engine support means multiple devices are not handled. There is no explicit locking around GE register programming; concurrent fb operations could interleave unless higher layers serialize them. `wmt_ge_sync` is a CPU busy wait and returns `-EBUSY` without recovery. Unsupported pixel depths silently pattern as zero after a warn-once. Remove just clears `regbase`, relying on devm for unmap and not disabling the engine.

Test signals: build with `CONFIG_FB_WMT_GE_ROPS`; probe a `wm,prizm-ge-rops` DT node before framebuffer use; run fbcon scroll/fill/copy workloads, XOR rect tests, unsupported depth checks, concurrent drawing stress, and `fb_sync` timeout injection if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.h

Purpose: configuration wrapper for WonderMedia GE ROP helpers. It lets fbdev drivers call `wmt_ge_*` functions unconditionally while providing system-memory fallbacks when GE acceleration is not built.

Important APIs, types, and functions: declares or inlines `wmt_ge_fillrect`, `wmt_ge_copyarea`, and `wmt_ge_sync`. With `CONFIG_FB_WMT_GE_ROPS`, these are externs from `wmt_ge_rops.c`; otherwise `wmt_ge_fillrect` maps to `sys_fillrect`, `wmt_ge_copyarea` maps to `sys_copyarea`, and sync returns success.

Control flow: compile-time only through preprocessor conditionals.

State and persistence: no state; fallback behavior is stateless aside from normal fbdev memory writes.

Dependencies and integration points: included by `wm8505fb.c`; depends on fbdev declarations being visible to callers.

Risks: software fallback uses `sys_*` helpers while the accelerated path uses I/O request programming. That can hide acceleration-specific bugs unless both configurations are tested. The header itself does not include fb headers, so include ordering matters.

Test signals: compile both enabled and disabled configurations; verify `wm8505fb_ops` resolves symbols and that software fallback draws correctly without the GE platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/xen-fbfront.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/xen-fbfront.c

Purpose: Xen paravirtual framebuffer frontend. It exposes a sysmem fbdev framebuffer to Linux guests and communicates memory pages, display updates, and optional resize requests to a Xen backend through xenbus, shared pages, event channels, and the Xen framebuffer ring protocol.

Important APIs, types, and functions: `struct xenfb_info` tracks vmalloc framebuffer memory, `fb_info`, dirty rectangle, resize request, shared page, GFNs, event IRQ, feature flags, and xenbus device. Core functions include `xenfb_send_event`, `xenfb_refresh`, `xenfb_deferred_io`, `xenfb_setcolreg`, `xenfb_check_var`, `xenfb_set_par`, `xenfb_event_handler`, `xenfb_probe`, `xenfb_remove`, `xenfb_resume`, `xenfb_init_shared_page`, `xenfb_connect_backend`, `xenfb_disconnect_backend`, and `xenfb_backend_changed`.

Control flow: module init only registers the frontend when running as a non-dom0 Xen PV-capable guest. Probe reads backend video limits from xenstore, allocates vmalloc framebuffer memory and GFNs, allocates a shared `xenfb_page`, creates `fb_info`, sets 32-bpp truecolor defaults, initializes deferred I/O, fills the shared page with GFN directory and mode metadata, binds an event channel IRQ, writes `page-ref`, `event-channel`, protocol, and update feature to xenstore, registers the framebuffer, and makes tty0 preferred if no console was selected. Deferred I/O and damage callbacks coalesce dirty rectangles and send `XENFB_TYPE_UPDATE` when requested. Resize changes are staged in `xenfb_set_par` and emitted before updates if backend resize is supported.

State and persistence: all state is per xenbus frontend and volatile. The guest framebuffer is vmalloc memory; the shared page and GFN directory persist while the device is connected. Dirty and resize state are protected by spinlocks. Xenstore values and ring producer/consumer indexes are integration state with the backend.

Dependencies and integration points: depends on Xen hypervisor detection, xenbus, event channels, Xen page/GFN helpers, fbdev deferred I/O, vmalloc, console registration, and protocol definitions in `xen/interface/io/fbif.h`.

Risks: framebuffer sharing uses GFNs rather than grant tables, as noted in the TODO. Ring-full conditions defer dirty rectangles and rely on later IRQ/update flushes. Resize is limited to initial memory bounds and backend feature support. The module parameter array is global, so multiple vfb devices would share sizing state. Damage-range handling refreshes the whole current mode. Backend input events are ignored.

Test signals: boot a Xen PV guest with vfb; vary `video=` memory/width/height and xenstore limits; verify fbcon, mmap/write damage, deferred I/O updates, backend `request-update`, resize with and without `feature-resize`, resume reconnect, ring-full dirty coalescing, and frontend close state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/xen-fbfront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/xilinxfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/xilinxfb.c

Purpose: framebuffer driver for Xilinx TFT LCD controller variants. It handles a simple fixed-format truecolor controller with framebuffer base and control registers, supporting OF-provided dimensions, BUS or PPC DCR register access, optional screen rotation, and either supplied or DMA-allocated framebuffer memory.

Important APIs, types, and functions: `struct xilinxfb_platform_data` defines resolution, virtual resolution, physical size, rotation, and optional fb physical address. `struct xilinxfb_drvdata` embeds `fb_info`, register access state, framebuffer allocation state, flags, default control value, and pseudo-palette. Key functions are `xilinx_fb_out32`, `xilinx_fb_in32`, `xilinx_fb_setcolreg`, `xilinx_fb_blank`, `xilinxfb_assign`, `xilinxfb_release`, `xilinxfb_of_probe`, and `xilinxfb_of_remove`.

Control flow: OF probe starts from default 640x480 visible, 1024x480 virtual geometry, allocates drvdata, determines BUS versus DCR access from `xlnx,dcr-splb-slave-if`, maps registers or DCR host, parses optional `phys-size`, `resolution`, `virtual-resolution`, and `rotate-display`, then delegates to `xilinxfb_assign`. Assignment maps/allocates framebuffer memory, clears it, writes framebuffer base, detects little-endian register access if the readback differs, enables display and rotation, fills `fb_info`, allocates cmap, and registers the framebuffer. Blank writes control enable or zero.

State and persistence: runtime state is drvdata, hardware control registers, pseudo-palette, and framebuffer memory. DMA-allocated memory is freed on release; caller-provided physical memory is ioremapped and unmapped only. No persistent storage exists.

Dependencies and integration points: depends on platform/OF, fbdev default IOMEM ops, DMA coherent allocation, optional PPC DCR APIs, and Xilinx compatible strings for XPS/PLB TFT/DVI controllers.

Risks: hardware format is effectively fixed at 32 bpp with 24 useful color bits; mode validation/set_par are absent, so users cannot safely change modes. If register endianness readback fails for reasons other than byte order, the driver switches access mode. Supplied `fb_phys` is trusted. DCR path only exists under `CONFIG_PPC_DCR`. Error paths must disable the display and free the right memory kind.

Test signals: build BUS and PPC DCR configurations; boot with each supported compatible; validate OF geometry parsing, big/little-endian MMIO access, blank/unblank, pseudo-palette color rendering, rotation bit, DMA allocation and external framebuffer paths, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/xilinxfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/video/hdmi.c

Purpose: generic HDMI infoframe helper library. It initializes, validates, packs, unpacks, checksums, and logs standard HDMI infoframes: AVI, SPD, Audio, HDMI Vendor, DRM, and a DisplayPort SDP representation of HDMI audio infoframes.

Important APIs, types, and functions: exported init/check/pack APIs include `hdmi_avi_infoframe_init/check/pack/pack_only`, `hdmi_spd_infoframe_init/check/pack/pack_only`, `hdmi_audio_infoframe_init/check/pack/pack_only/pack_for_dp`, `hdmi_vendor_infoframe_init/check/pack/pack_only`, `hdmi_drm_infoframe_init/check/pack/pack_only/unpack_only`, `hdmi_infoframe_pack`, `hdmi_infoframe_pack_only`, `hdmi_infoframe_unpack`, and `hdmi_infoframe_log`. Internal helpers compute checksums, derive vendor frame length, validate "any vendor" frames, unpack individual types, and map enum values to log strings.

Control flow: each frame type has an init function that zeroes and assigns type/version/length defaults, a check function that validates type/version/length and type-specific constraints, a pack-only function that validates the existing frame, writes header and payload bytes, zeroes the destination buffer, and stores checksum byte 3, and a pack function that first normalizes derived fields where needed. Generic pack/unpack switch on infoframe type. Unpack functions validate size, header, length, checksum, then fill typed structs. Logging dispatches by type and prints decoded enum names and fields.

State and persistence: stateless library code. It mutates caller-provided frame structs only in `check` paths that update derived length, and mutates caller-provided buffers during packing. No global state exists.

Dependencies and integration points: depends on `linux/hdmi.h` structure definitions and enums, `drm/display/drm_dp.h` for `struct dp_sdp`, device logging, exported symbols for DRM/HDMI bridge/display drivers, and kernel bit/errno/string helpers.

Risks: packing assumes callers provide semantically valid enum values beyond the explicit checks; many fields are masked rather than rejected. `pack_only` variants require pre-normalized fields, especially vendor length. Vendor handling only supports HDMI IEEE OUI. SPD string initialization copies fixed field sizes and may not NUL-terminate, which is acceptable for packed fields but relevant for logging. Checksum failures cause unpack rejection. A typo in the DRM init comment is harmless.

Test signals: unit/KUnit-style round-trip tests for every infoframe type; checksum validation; too-small buffer `-ENOSPC`; invalid type/version/length `-EINVAL`; vendor VIC versus 3D mutual exclusion; DRM unpack-only CTA bytes; DP audio SDP header fields; logging smoke tests with boundary enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/logo/Kconfig

Purpose: Kconfig menu for boot logo generation and selection. It controls whether framebuffer/console boot logos are built, which color-depth variants are available, and which source PNM files are converted into generated C logo data.

Important APIs, types, and functions: config symbols include `LOGO`, `FB_LOGO_EXTRA`, `LOGO_LINUX_MONO`, `LOGO_LINUX_MONO_FILE`, `LOGO_LINUX_VGA16`, `LOGO_LINUX_VGA16_FILE`, `LOGO_LINUX_CLUT224`, and `LOGO_LINUX_CLUT224_FILE`.

Control flow: selecting `LOGO` opens nested logo options. Per-logo file symbols default to architecture-specific logo assets for some architectures and to generic Linux logo assets otherwise. The 224-color logo defaults to enabled.

State and persistence: Kconfig state persists in the kernel build configuration and drives generated object inclusion; no runtime state is created here.

Dependencies and integration points: `LOGO` depends on `FB_CORE` or `SGI_NEWPORT_CONSOLE`. File symbols are consumed by `drivers/video/logo/Makefile`, which invokes `pnmtologo`. Logo objects are consumed by `logo.c` and framebuffer console/display code.

Risks: invalid custom PNM paths or wrong palette/color count fail at build time. `LOGO_LINUX_CLUT224` defaulting to yes increases generated asset inclusion whenever `LOGO` is enabled.

Test signals: menuconfig visibility under fbdev and SGI Newport configs; build with default and custom logo file paths; verify mono, VGA16, and CLUT224 conversion commands run and generated objects link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/logo/Makefile

Purpose: build rules for Linux boot logo objects and the host-side `pnmtologo` converter. It maps Kconfig logo choices to generated C files and object files.

Important APIs, types, and functions: Make variables include `obj-$(CONFIG_LOGO*)`, `hostprogs := pnmtologo`, `quiet_cmd_logo`, `cmd_logo`, per-logo generated C targets, pattern rule for `%_clut224.c`, and `targets` for generated files.

Control flow: when a logo config is enabled, the relevant object is included. Generated C files depend on configured PNM files and the host `pnmtologo`; the kernel build invokes `pnmtologo -t <type> -n <logo-name> -o <output> <input>` through `if_changed`.

State and persistence: build-system state only. Generated C files are build artifacts, tracked in `targets`, not source runtime state.

Dependencies and integration points: depends on Kbuild hostprogs, config file path variables from Kconfig, and the `pnmtologo.c` converter. `logo.o` provides runtime selection through `fb_find_logo`.

Risks: custom logo file paths are direct dependencies and can break incremental builds if missing. The CLUT224 pattern rule assumes source file naming convention. Converter failures surface as build failures.

Test signals: run kernel build for each logo type; check generated `logo_linux_*.c` content, object inclusion, and incremental rebuild when PNM input changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/logo.c -->
# sources/distributed-fs/ceph-client/drivers/video/logo/logo.c

Purpose: runtime selector for compiled-in Linux boot logos. It chooses the best enabled logo for a requested color depth unless logos have been disabled or already freed after init.

Important APIs, types, and functions: module parameter `nologo`, static `logos_freed`, `fb_logo_late_init`, and exported `fb_find_logo(int depth)`.

Control flow: `fb_logo_late_init` runs as a synchronous late initcall and marks initdata logo assets as freed. `fb_find_logo` returns `NULL` if `nologo` or `logos_freed` is true; otherwise it conditionally selects mono for depth >=1, VGA16 for depth >=4, and CLUT224 for depth >=8, with later checks overriding earlier ones.

State and persistence: `nologo` is a module parameter; `logos_freed` is runtime state protecting against use-after-initdata-free. Logo assets themselves are generated `__initconst` data and intentionally unavailable after late init.

Dependencies and integration points: depends on generated `linux_logo` objects declared by `linux/linux_logo.h`; exported to fbdev/console users. On M68K it includes setup headers.

Risks: callers after late init receive no logo. Selection is depth-based only, not display-specific. Module parameter permissions are zero, so runtime toggling through sysfs is not available.

Test signals: boot with and without `nologo`; build different logo configs; call `fb_find_logo` before and after late init; verify depth selection and no access after init data free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/logo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/pnmtologo.c -->
# sources/distributed-fs/ceph-client/drivers/video/logo/pnmtologo.c

Purpose: host build utility that converts ASCII PNM logo images into C source containing `struct linux_logo` data arrays suitable for kernel inclusion.

Important APIs, types, and functions: global options are `-t` type, `-n` logo name, `-o` output, and input filename. Main helpers are `get_number`, `get_number255`, `read_image`, validation helpers, `write_header`, `write_footer`, `write_hex`, `write_logo_mono`, `write_logo_vga16`, `write_logo_clut224`, `write_logo_gray256`, `die`, `usage`, and `main`.

Control flow: `main` parses options, reads an ASCII PBM/PGM/PPM image, and dispatches to the selected output writer. `read_image` rejects binary PNM, parses width/height/maxval, allocates `logo_data`, and normalizes channels to 0..255. Output writers validate constraints: mono must be black/white, VGA16 must match the fixed VGA palette, CLUT224 builds a palette up to 224 colors and encodes indexes offset by 32, and gray256 requires equal RGB channels. The generated file includes logo data, optional CLUT, and a `const struct linux_logo`.

State and persistence: process-local heap state for image rows and palette, output file or stdout, and generated C source on disk. No runtime kernel state.

Dependencies and integration points: built as a Kbuild host program from `logo/Makefile`; output consumed by logo object builds and `logo.c`.

Risks: binary PNM files are unsupported and require pre-conversion. Parsing uses simple heap allocations and exits on fatal errors; no cleanup is needed for a short-lived host tool but malformed huge dimensions can demand large memory. PBM parsing includes a workaround for some non-spaced exports. CLUT order follows first occurrence, so image changes alter generated data layout.

Test signals: run converter on valid mono, VGA16, CLUT224, and gray256 ASCII images; test invalid binary PNM, too many colors, out-of-palette VGA16, non-gray gray256, comments/whitespace parsing, custom symbol name, stdout and `-o` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/logo/pnmtologo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/nomodeset.c -->
# sources/distributed-fs/ceph-client/drivers/video/nomodeset.c

Purpose: global kernel modeset-disabling helper for the `nomodeset` boot parameter. It lets graphics drivers query whether only firmware/system framebuffer drivers should be used.

Important APIs, types, and functions: static `video_nomodeset`, exported `video_firmware_drivers_only`, and `disable_modeset` registered with `__setup("nomodeset", ...)`.

Control flow: early boot parameter parsing calls `disable_modeset`, sets the static boolean, emits a warning, and returns handled. Drivers call `video_firmware_drivers_only()` to check this state.

State and persistence: one boot-lifetime boolean. No runtime toggling or persistence across boots.

Dependencies and integration points: used through `<video/nomodeset.h>` by DRM/fbdev code that wants to avoid native modesetting when the user requested firmware-only graphics.

Risks: global effect is coarse-grained. Drivers that do not check this helper may still bind. The warning text is the only user-facing signal here.

Test signals: boot with `nomodeset`; verify exported helper returns true and native drivers that honor it skip modesetting while system framebuffer remains available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/nomodeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/of_display_timing.c -->
# sources/distributed-fs/ceph-client/drivers/video/of_display_timing.c

Purpose: Open Firmware/devicetree parser for `display-timings` nodes. It translates timing subnodes into `struct display_timing` and aggregate `struct display_timings` objects.

Important APIs, types, and functions: exported `of_get_display_timing` and `of_get_display_timings`; internal `parse_timing_property` and `of_parse_display_timing`. It fills `struct timing_entry`, `struct display_timing`, and `struct display_timings`.

Control flow: individual timing properties may contain one cell (typical only) or three cells (min/typ/max). `of_parse_display_timing` reads required horizontal, vertical, and clock properties, optional polarity/edge booleans, and mode flags. `of_get_display_timing` parses a named child. `of_get_display_timings` locates the `display-timings` child, resolves `native-mode` or first child, allocates an array, parses every child, records the native index, and releases nodes on success/error.

State and persistence: allocates `display_timings` and per-timing objects for the caller to release with `display_timings_release`. No global state.

Dependencies and integration points: depends on OF property APIs, `display_timing` structures, and slab allocation. Used by framebuffer/display drivers such as `wm8505fb.c` and by `of_videomode.c`.

Risks: required property parsing ORs errors together and reports a generic timing-property error. Any invalid child makes the whole timing set fail to avoid accepting wrong devicetrees. Ownership must be honored by callers to avoid leaks. Timing node order defines fallback native mode.

Test signals: DT parsing tests for one-cell and three-cell properties, missing required values, invalid cell counts, native-mode phandle, first-child fallback, polarity and interlace/doublescan/doubleclk flags, and error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/of_display_timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/of_videomode.c -->
# sources/distributed-fs/ceph-client/drivers/video/of_videomode.c

Purpose: convenience OF helper that retrieves one videomode from a node's display timings and converts it into `struct videomode`.

Important APIs, types, and functions: exported `of_get_videomode(struct device_node *np, struct videomode *vm, int index)`.

Control flow: calls `of_get_display_timings`, maps `OF_USE_NATIVE_MODE` to the timing set's native index, converts the selected timing with `videomode_from_timings`, releases the display timing set, and returns the conversion status.

State and persistence: no persistent state; allocates through `of_get_display_timings` and releases before returning.

Dependencies and integration points: bridges `of_display_timing.c` and `videomode.c`; used by display drivers that only need one mode rather than the full timing table.

Risks: callers cannot inspect alternate modes through this API. Missing timings are reported as `-EINVAL`. Index bounds are delegated to `videomode_from_timings`.

Test signals: parse native and explicit indexes; test missing `display-timings`, invalid index, and release behavior under kmemleak-style checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/of_videomode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/screen_info_generic.c -->
# sources/distributed-fs/ceph-client/drivers/video/screen_info_generic.c

Purpose: generic helpers for interpreting `struct screen_info` firmware display data. It derives I/O/memory resources consumed by text/framebuffer devices and translates linear framebuffer color metadata into a generic pixel format.

Important APIs, types, and functions: exported `screen_info_resources`, `__screen_info_lfb_bits_per_pixel`, and `screen_info_pixel_format`. Internal helpers initialize named `struct resource` objects and identify EGA/VGA graphics modes.

Control flow: `screen_info_resources` switches on `screen_info_video_type` and emits resource descriptors for MDA, CGA, EGA mono/color, VGA color, and linear framebuffer EFI/VESA types, subject to caller array length. Unsupported platform-specific types return `-EINVAL`. Pixel-format handling computes effective bits-per-pixel from depth and channel/reserved bit extents, fills indexed formats for depth <=8, and fills direct channel offsets for linear framebuffers.

State and persistence: no state; operates on caller-provided `screen_info`, resources, and pixel-format structures.

Dependencies and integration points: used by sysfb/simplefb/simpledrm and firmware framebuffer arbitration paths. Depends on `linux/screen_info.h`, `ioport`, and `<video/pixel_format.h>`.

Risks: support is intentionally limited to common text and linear framebuffer types. Resource computation trusts firmware-provided base/size helpers. The bpp derivation handles historical inconsistencies but may still reject values above `U8_MAX`.

Test signals: unit tests or boot checks for each supported video type, resource array truncation behavior, zero LFB base/size handling, XRGB1555/RGB565/XRGB8888 bpp derivation, indexed 8-bpp format, and unsupported types returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/screen_info_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/screen_info_pci.c -->
# sources/distributed-fs/ceph-client/drivers/video/screen_info_pci.c

Purpose: PCI-specific helpers for firmware framebuffer relocation and parent-device discovery. It tracks which display PCI BAR contains the firmware linear framebuffer and updates `screen_info` if firmware framebuffer memory is relocated by PCI resource assignment.

Important APIs, types, and functions: exported `screen_info_apply_fixups` and `screen_info_pci_dev`. Internal state includes `screen_info_lfb_pdev`, BAR index, original resource start, and framebuffer offset. Internal helpers include `__screen_info_relocation_is_valid`, `__screen_info_lfb_pci_bus_region`, `screen_info_fixup_lfb`, and `__screen_info_pci_dev`.

Control flow: a PCI header fixup runs for display-class devices, converts the screen_info LFB bus range into a resource, finds the containing PCI resource, and records pdev/BAR/offset/original base once. Later `screen_info_apply_fixups` compares current BAR start with the original; if relocated and still valid, it updates the primary display LFB base, otherwise warns and disables usability by not applying the invalid relocation. `screen_info_pci_dev` derives screen resources and scans display-class PCI devices for a containing memory resource.

State and persistence: static boot/runtime state tracks one firmware framebuffer PCI owner. It mutates `sysfb_primary_display.screen` when applying fixups. No disk persistence.

Dependencies and integration points: depends on PCI fixup infrastructure, `sysfb_primary_display`, `screen_info_resources`, PCI bus-to-resource translation, and display-class resource matching. Integrates with firmware framebuffer/simple framebuffer setup.

Risks: only one LFB owner is tracked. Invalid relocation warns but leaves consumers dependent on later handling. Resource math must avoid overflow and relies on firmware screen_info accuracy. PCI device references from scanning must be managed by callers according to PCI API expectations.

Test signals: boot systems where EFI/VESA framebuffer is inside a display BAR; test PCI BAR relocation before sysfb registration; validate offset calculation through host bridge translation; run unsupported/non-LFB types; verify `screen_info_pci_dev` returns matching pdev or NULL/ERR_PTR correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/screen_info_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/sticore.c -->
# sources/distributed-fs/ceph-client/drivers/video/sticore.c

Purpose: HP PARISC STI firmware core for graphics console support. It discovers STI ROMs on native PARISC and PCI graphics cards, copies and interprets ROM metadata/fonts, initializes firmware global configuration, exports font/block drawing helpers, and provides access to detected STI devices.

Important APIs, types, and functions: exported console helpers include `sti_putc`, `sti_set`, `sti_clear`, `sti_bmove`, `sti_font_convert_bytemode`, `sti_get_rom`, and `sti_call`. Discovery/setup functions include `sti_read_rom`, `sti_try_rom_generic`, `sti_init_glob_cfg`, `sti_init_graph`, `sti_inq_conf`, `sticore_pa_init`, `sticore_pci_init`, and `sti_init_roms`. Global state tracks `default_sti`, `num_sti_roms`, and `sti_roms`.

Control flow: boot options may set default STI path and font selection. `sti_get_rom` lazily initializes ROM discovery, registering PARISC and PCI drivers. Probe tries ROM addresses from device data, HPA, PAGE0, or enabled PCI ROM BAR. `sti_try_rom_generic` validates ROM signatures, handles PCI image indirection, copies byte- or word-mode ROMs, cooks font lists, maps region descriptors to physical addresses, allocates low-memory shared STI data, disables PCI ROM after copying, calls firmware `init_graph`, queries configuration, and registers the STI in global arrays. Drawing helpers build firmware inptr/outptr structures, handle 32-bit ROM calls on 64-bit kernels by using low-memory copies, serialize calls with `sti->lock`, and retry while firmware returns busy.

State and persistence: persistent runtime state is global detected ROM list, selected default STI, per-STI copied ROM/font/config data, firmware global config, and hardware/firmware initialized graphics state. Fonts and STI data are allocated with low-memory constraints. No storage persistence.

Dependencies and integration points: PARISC-specific PDC, GSC, hardware path, page0, cache flush, low-memory allocation, optional PCI and PPC-style font support. It integrates with sticon/console users through `<video/sticore.h>` exports and with PARISC/PCI device buses.

Risks: architecture- and firmware-specific code with real-mode STI calls; pointer width handling is critical and guarded by overflow warnings. `sticore_pci_remove` is a `BUG()`, so removal is not supported. Some older GSC/STI card revisions are explicitly rejected. ROM copying and byte-mode conversion depend on exact firmware layout. Global lazy init and fixed `MAX_STI_ROMS` limit scalability.

Test signals: PARISC boot on native and PCI STI hardware; boot parameters `sti=` and `sti_font=` with built-in and ROM fonts; 32-bit and 64-bit kernels with 32-bit and 64-bit STI ROMs; console putc/clear/bmove rendering; unsupported card revision rejection; PCI ROM enable/disable behavior; suspend/removal expectations documented as unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/sticore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/vgastate.c -->
# sources/distributed-fs/ceph-client/drivers/video/vgastate.c

Purpose: shared VGA state save/restore library. It captures and restores VGA register sets, DAC color maps, text memory, and font planes so framebuffer drivers can take over legacy VGA hardware and later return it to the prior console state.

Important APIs, types, and functions: exported `save_vga(struct vgastate *state)` and `restore_vga(struct vgastate *state)`. Internal `struct regstate` stores saved font/text/cmap/register buffers. Helpers include `save_vga_text`, `restore_vga_text`, `save_vga_mode`, `restore_vga_mode`, `save_vga_cmap`, `restore_vga_cmap`, and `vga_cleanup`.

Control flow: `save_vga` allocates `regstate`, optionally saves cmap, mode registers, and fonts/text depending on `state->flags`, defaulting register counts and framebuffer memory base/size when absent. Text/font save temporarily blanks the display and reprograms VGA planes to access font/text planes. `restore_vga` restores mode, fonts/text, then cmap, and always cleans allocated save buffers. Register save/restore handles misc, CRTC, attribute, graphics, and sequencer registers with VGA I/O helper routines.

State and persistence: saved state is heap/vmalloc memory referenced by `state->vidstate` until restore or cleanup. It maps legacy VGA memory with `ioremap` during save/restore. No persistence beyond memory and caller-owned `vgastate`.

Dependencies and integration points: used by legacy fbdev drivers such as `vt8623fb`. Depends on `<video/vga.h>`, fbdev, vmalloc, and direct VGA register/memory access.

Risks: assumes readable/writable VGA DAC and standard VGA plane behavior. Save fails if font memory window is too small or allocations fail. It skips text save when current mode appears graphics. Register programming can disturb active display during save/restore; callers need serialization around hardware ownership. Return convention is `1` for failure rather than negative errno.

Test signals: save/restore around fbdev open/close on VGA-compatible hardware; text console content/font/cmap preservation; 4-plane font paths; memory allocation failure injection; nonstandard `num_*` register counts; depth-4 restore behavior; ioremap failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/vgastate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/videomode.c -->
# sources/distributed-fs/ceph-client/drivers/video/videomode.c

Purpose: generic conversion helpers from `struct display_timing`/`struct display_timings` to `struct videomode`.

Important APIs, types, and functions: exported `videomode_from_timing` and `videomode_from_timings`.

Control flow: `videomode_from_timing` copies the typical pixel clock, active area, porch, sync length, and flags fields into a videomode. `videomode_from_timings` fetches a timing by index with `display_timings_get`, returns `-EINVAL` if missing, and delegates conversion.

State and persistence: no state; pure transformation of caller-provided structures.

Dependencies and integration points: used by `of_videomode.c` and display drivers converting parsed timing tables to a single active mode. Depends on `<video/display_timing.h>` and `<video/videomode.h>`.

Risks: min/max timing ranges are discarded in favor of typical values. Index validation is only as strong as `display_timings_get`.

Test signals: convert valid timing with flags; invalid index returns `-EINVAL`; verify min/max ranges do not affect output except through `.typ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/videomode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/Kconfig

Purpose: top-level Kconfig menu for virtualization support drivers. It groups VM-oriented device drivers and sources submenus for vboxguest, Nitro Enclaves, ACRN, and confidential-computing support.

Important APIs, types, and functions: config symbols include `VIRT_DRIVERS`, `VMGENID`, and `FSL_HV_MANAGER`; it sources `drivers/virt/vboxguest/Kconfig`, `drivers/virt/nitro_enclaves/Kconfig`, `drivers/virt/acrn/Kconfig`, and `drivers/virt/coco/Kconfig`.

Control flow: `VIRT_DRIVERS` gates most nested virtualization drivers. `VMGENID` defaults to yes and supports RNG reseeding after VM cloning. `FSL_HV_MANAGER` depends on `FSL_SOC` and selects `EPAPR_PARAVIRT`.

State and persistence: build configuration state only.

Dependencies and integration points: consumed by `drivers/virt/Makefile` and architecture/platform virtualization driver builds. `coco` is sourced outside the `VIRT_DRIVERS` conditional.

Risks: disabling `VIRT_DRIVERS` skips most virtual environment drivers but not the `coco` submenu. Defaults such as `VMGENID=y` affect built-in footprint.

Test signals: menuconfig visibility, dependency resolution, and object inclusion for VMGENID, Freescale HV, Nitro, ACRN, vboxguest, and coco configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/Makefile

Purpose: top-level Makefile for virtualization support drivers. It maps virtualization Kconfig symbols to object files and subdirectories.

Important APIs, types, and functions: object assignments include `fsl_hypervisor.o`, `vmgenid.o`, `vboxguest/`, `nitro_enclaves/`, `acrn/`, and `coco/`.

Control flow: Kbuild includes objects conditionally by config. `vboxguest/` and `coco/` are entered unconditionally from this Makefile, while internal Kconfig/Makefiles decide built objects. `acrn/` is included when `CONFIG_ACRN_HSM` is set.

State and persistence: build-system state only.

Dependencies and integration points: tied to `drivers/virt/Kconfig` and child directory Makefiles such as `drivers/virt/acrn/Makefile`.

Risks: unconditional directory traversal can expose child Makefile issues even when no objects are selected. Config-symbol mismatches would silently omit drivers.

Test signals: build matrix for each virtualization driver config and `make drivers/virt/` traversal with features disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/Kconfig

Purpose: Kconfig entry for the ACRN Hypervisor Service Module. It controls the `/dev/acrn_hsm` management driver used in ACRN Service VMs.

Important APIs, types, and functions: config symbol `ACRN_HSM` is tristate, depends on `ACRN_GUEST`, and selects `EVENTFD`.

Control flow: enabling this config builds the ACRN HSM module or built-in driver; the help text documents that it is for privileged management Service VMs, not ordinary User VMs.

State and persistence: build configuration state only.

Dependencies and integration points: consumed by `drivers/virt/Makefile` and `drivers/virt/acrn/Makefile`; runtime code checks ACRN hypervisor and privileged-VM CPUID feature before registering.

Risks: selecting it in a non-privileged ACRN guest compiles but runtime init returns permission/state errors. Eventfd is required for ioeventfd/irqfd integration.

Test signals: Kconfig dependency resolution with and without `ACRN_GUEST`; built-in and module builds; runtime registration only in privileged Service VM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/Makefile -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/Makefile

Purpose: Makefile for the ACRN HSM driver aggregate object.

Important APIs, types, and functions: `obj-$(CONFIG_ACRN_HSM) := acrn.o`; `acrn-y` links `hsm.o`, `vm.o`, `mm.o`, `ioreq.o`, `ioeventfd.o`, and `irqfd.o` into the driver.

Control flow: Kbuild creates one `acrn` module/built-in object from the listed compilation units when `CONFIG_ACRN_HSM` is enabled.

State and persistence: build-system only.

Dependencies and integration points: ties the files researched here (`hsm.c`, `ioeventfd.c`, headers) to companion VM/memory/ioreq/irqfd implementation files outside this work item.

Risks: the driver is incomplete if any listed object does not compile; interface contracts in `acrn_drv.h` span all components.

Test signals: module and built-in link tests for `CONFIG_ACRN_HSM`; symbol resolution across all six objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/acrn_drv.h -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/acrn_drv.h

Purpose: shared private header for the ACRN Hypervisor Service Module. It defines VM, memory mapping, I/O request client, ioeventfd/irqfd integration state, and cross-file function prototypes.

Important APIs, types, and functions: key structures are `vm_memory_region_op`, `vm_memory_region_batch`, `vm_memory_mapping`, `acrn_ioreq_buffer`, `acrn_ioreq_range`, `acrn_ioreq_client`, and `acrn_vm`. Constants include `ACRN_NAME_LEN`, `ACRN_MEM_MAPPING_MAX`, memory operation types, `ACRN_INVALID_VMID`, VM flags, and ioreq client flags. It declares global `acrn_dev`, `acrn_vm_list`, `acrn_vm_list_lock`, and APIs for VM creation/destruction, memory map/unmap, ioreq lifecycle, MSI injection, ioeventfd, and irqfd.

Control flow: not executable by itself; it codifies the in-kernel object graph. `struct acrn_vm` owns lifecycle state for one User VM associated with an open `/dev/acrn_hsm` file, including mapping arrays, ioreq clients, shared pages, eventfd lists, and workqueues.

State and persistence: declares in-memory state only. VM state is per open file and destroyed on release; no disk persistence.

Dependencies and integration points: depends on UAPI `<linux/acrn.h>`, miscdevice, hypercall wrappers, lists, locks, pages, eventfd-driven components, and companion source files `hsm.c`, `vm.c`, `mm.c`, `ioreq.c`, `ioeventfd.c`, and `irqfd.c`.

Risks: fixed `ACRN_MEM_MAPPING_MAX` limits mapped regions. Locking responsibilities are spread across mutexes, spinlocks, rwlocks, waitqueues, and bitmaps, so contract drift can cause races. Flexible array batches require correct allocation sizing. Header-level prototypes expose a broad internal API.

Test signals: compile all ACRN objects; static analysis for lock pairing and flexible-array sizing; VM lifecycle tests covering create, memory map, ioreq, ioeventfd, irqfd, destroy, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/acrn_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/hsm.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/hsm.c

Purpose: main ACRN HSM miscdevice implementation. It exposes `/dev/acrn_hsm`, associates one `struct acrn_vm` with each open file, dispatches management ioctls to hypercalls and internal VM/ioreq helpers, and provides a sysfs CPU-removal hook for the Service VM.

Important APIs, types, and functions: file operations are `acrn_dev_open`, `acrn_dev_ioctl`, and `acrn_dev_release`. Module lifecycle is `hsm_init`/`hsm_exit`. `pmcmd_ioctl` handles power-management queries. Sysfs path uses `remove_cpu_store`, `DEVICE_ATTR_WO(remove_cpu)`, visibility callback, and `acrn_dev` miscdevice. Ioctl dispatch covers VM create/start/pause/reset/destroy, vCPU regs, memseg map/unmap, MMIO/PCI/vdev assign/deassign, ptdev interrupts, irqline, MSI injection, interrupt monitor page, default ioreq client lifecycle, request completion, ioreq clearing, PM CPU state, ioeventfd, and irqfd.

Control flow: open allocates a zeroed `acrn_vm` with invalid VMID. All ioctls except create require a valid VMID. Create copies and validates user creation data, delegates to `acrn_vm_create`, and copies resulting data back. Most device-assignment and interrupt ioctls `memdup_user` a fixed structure, call the corresponding hypercall wrapper with physical address, then free it. Memory and ioreq paths delegate to internal helpers. Interrupt monitor pins one long-term user page and passes its physical address to the hypervisor. Release destroys the VM and frees the `acrn_vm`. Init checks that the kernel runs under ACRN and is the privileged VM, registers the miscdevice, then sets up ioreq interrupts.

State and persistence: per-file VM state persists from open to release; monitor pages may remain pinned until replaced or VM destruction; miscdevice and sysfs state persist while module is loaded. No disk persistence.

Dependencies and integration points: depends on x86 ACRN hypervisor CPUID/hypercall ABI, miscdevice, user-copy APIs, pin_user_pages, CPU hotplug, internal VM/MM/ioreq/ioeventfd/irqfd code, and UAPI ioctl structures from `<linux/acrn.h>`.

Risks: HSM relies on the hypervisor for most parameter sanity checks, so kernel-side validation is selective. `ACRN_IOCTL_SET_IRQLINE` passes `ioctl_param` directly as a hypercall GPA-style argument, making UAPI semantics important. Long-term pinned pages must be correctly unpinned by VM teardown. Open creates an object even before VM creation, so invalid-state checks are critical. CPU removal sysfs can offline CPUs and must roll back on hypercall failure.

Test signals: run in privileged ACRN Service VM; ioctl ABI tests for invalid VM state, reserved fields, create/destroy lifecycle, all hypercall wrappers, user-copy faults, monitor page replacement/unpinning, ioeventfd/irqfd delegation, PM queries, and module init rejection outside ACRN or outside privileged VM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/hsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/hypercall.h -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/hypercall.h

Purpose: private ACRN HSM hypercall wrapper header. It defines ACRN hypercall IDs and provides typed inline wrappers around `acrn_hypercall1`/`acrn_hypercall2`.

Important APIs, types, and functions: hypercall IDs cover Service VM CPU removal, VM lifecycle, vCPU register setup, MSI/interrupt monitor/irqline, ioreq buffer and completion, memory region mapping, PCI/MMIO/vdev assignment, ptdev interrupts, and PM CPU state. Inline wrappers include `hcall_sos_remove_cpu`, `hcall_create_vm`, `hcall_start_vm`, `hcall_pause_vm`, `hcall_destroy_vm`, `hcall_reset_vm`, `hcall_set_vcpu_regs`, `hcall_inject_msi`, `hcall_vm_intr_monitor`, `hcall_set_irqline`, `hcall_set_ioreq_buffer`, `hcall_notify_req_finish`, `hcall_set_memory_regions`, `hcall_create_vdev`, `hcall_destroy_vdev`, `hcall_assign_mmiodev`, `hcall_deassign_mmiodev`, `hcall_assign_pcidev`, `hcall_deassign_pcidev`, `hcall_set_ptdev_intr`, `hcall_reset_ptdev_intr`, and `hcall_get_cpu_state`.

Control flow: wrappers are direct one- or two-argument calls with no validation or marshalling beyond hypercall ID selection. Callers must allocate and pass Service VM physical addresses for structure arguments where required.

State and persistence: no state.

Dependencies and integration points: depends on `<asm/acrn.h>` for low-level hypercall functions. Included by `acrn_drv.h` and used throughout the ACRN HSM implementation.

Risks: thin wrappers mean ABI mismatches, wrong physical addresses, or missing validation propagate directly to the hypervisor. Hypercall ID constants must match the hypervisor exactly.

Test signals: compile-time coverage through ACRN HSM; runtime ioctl tests that exercise each wrapper and validate expected hypervisor return codes; ABI synchronization checks against ACRN hypervisor headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/hypercall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/ioeventfd.c -->
# sources/distributed-fs/ceph-client/drivers/virt/acrn/ioeventfd.c

Purpose: ACRN HSM ioeventfd support. It lets userspace associate eventfd objects with expected User VM MMIO or PIO writes, allowing fast notification paths for emulated devices such as vhost/virtio.

Important APIs, types, and functions: internal `struct hsm_ioeventfd` stores list linkage, eventfd context, address, data match, length, type, and wildcard flag. Public internal APIs are `acrn_ioeventfd_init`, `acrn_ioeventfd_config`, and `acrn_ioeventfd_deinit`. Helpers include `ioreq_type_from_flags`, `acrn_ioeventfd_shutdown`, `hsm_ioeventfd_is_conflict`, `acrn_ioeventfd_assign`, `acrn_ioeventfd_deassign`, `hsm_ioeventfd_match`, and `acrn_ioeventfd_handler`.

Control flow: init creates a non-default ioreq client named `ioeventfd-<vmid>` with `acrn_ioeventfd_handler` and initializes the VM list/mutex. Config either assigns or deassigns based on `ACRN_IOEVENTFD_FLAG_DEASSIGN`. Assign validates range overflow and allowed widths 1/2/4/8, obtains an eventfd context from the userspace fd, allocates state, sets PIO or MMIO type, determines wildcard versus data-match behavior, rejects conflicts under the VM mutex, registers the I/O range with the ioreq client, and appends to the list. Handler ignores reads by returning zero data, matches writes by type/address/length/data, and signals the eventfd. Deinit destroys the ioreq client and shuts down all eventfds.

State and persistence: per-VM linked list of ioeventfd registrations protected by `ioeventfds_lock`; each entry holds an eventfd reference until deassign or deinit. Registrations last for the VM lifetime or until explicit deassign.

Dependencies and integration points: depends on Linux eventfd, ACRN ioreq clients/ranges, UAPI `struct acrn_ioeventfd`, and VM state in `acrn_drv.h`. Integrated through `ACRN_IOCTL_IOEVENTFD` in `hsm.c`.

Risks: conflict detection is keyed by eventfd, address, type, and data/wildcard overlap; different eventfds can register overlapping ranges, so dispatch semantics depend on ioreq range routing. Deassign matches only by eventfd, not by address/data, so one fd registration is removed per call. Handler requires exact base address match and `p->length >= len`, not containment of sub-offsets. Reads are deliberately ignored and return zero.

Test signals: ioctl assign/deassign for MMIO and PIO, invalid widths, overflow address+len, eventfd fd errors, duplicate/conflicting registrations, wildcard and data-match writes, ignored reads, concurrent config and ioreq handling, VM deinit cleanup and eventfd reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virt/acrn/ioeventfd.c -->
