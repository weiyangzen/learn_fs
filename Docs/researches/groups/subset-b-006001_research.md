# subset-b-006001 Research

Grouped source research for Linux video headers in `sources/distributed-fs/ceph-client/include/video`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/gbe.h -->
# sources/distributed-fs/ceph-client/include/video/gbe.h

## Purpose
`gbe.h` describes the SGI GBE (Graphics Back End) hardware register aperture and timing metadata used by the SGI framebuffer driver. It is a low-level MMIO contract: `struct sgi_gbe` lays out control, timing, framebuffer, WID, color/gamma map, cursor, and video-capture registers with padding chosen to match the hardware address map.

## Important APIs, Types, and Functions
The central type is `struct sgi_gbe`, a volatile register map with fields such as `ctrlstat`, `dotclock`, `i2c`, `sysclk`, video timing registers `vt_*`, flat-panel controls `fp_*`, frame/overlay/DID DMA controls, `mode_regs[32]`, `cmap[6144]`, `gmap`, `gmap10`, cursor registers, and `vc_0` through `vc_8`. Helper macros `MASK`, `GET`, `SET`, `GET_GBE_FIELD`, and `SET_GBE_FIELD` encode register bitfield manipulation from the many `GBE_*_MSB/LSB` constants. `struct gbe_timing_info` carries mode geometry, sync/blanking positions, refresh/pixel-clock values, and PLL parameters.

## Control Flow
The header has no executable driver flow, but it dictates the programming sequence: choose timing data, program PLL fields in `dotclock`, set VT sync/blank/pixel-enable windows, configure frame size/depth/tile pointer/DMA enable bits, load WID/color/gamma/cursor state, then enable scanout DMA. Drivers use the bitfield macros to assemble register values before writing the volatile MMIO struct.

## State and Persistence Behavior
All persistent state represented here is hardware state in the GBE register block and display tables. Color maps, gamma tables, cursor glyphs, timing registers, and DMA enables live until reset, power loss, or driver reprogramming; the header itself owns no software lifetime or file-backed persistence.

## Dependencies and Integration Points
The header depends on fixed-width integer types and Linux-style `u32` definitions from including code. It integrates SGI framebuffer mode setup, palette/gamma programming, cursor support, I2C display probing, flat-panel signaling, and DMA frame buffer management with the GBE MMIO aperture.

## Risks and Test Signals
Risks include incorrect padding or volatile register width breaking the MMIO map, bitfield off-by-one errors, programming invalid timing/PLL values, FIFO reset sequencing mistakes, and confusion between shadow/in-hardware DMA control registers. Test signals include booting SGI hardware or emulation through mode set, palette/gamma updates, cursor movement, flat-panel and CRT timing validation, DMA enable/disable transitions, and static checks that register offsets in `struct sgi_gbe` match hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/gbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/hecubafb.h -->
# sources/distributed-fs/ceph-client/include/video/hecubafb.h

## Purpose
`hecubafb.h` defines the platform contract for the Hecuba e-paper framebuffer driver and Apollo controller command set. It separates framebuffer logic from board-specific GPIO/data/acknowledge handling.

## Important APIs, Types, and Functions
Apollo commands include `APOLLO_START_NEW_IMG`, `APOLLO_STOP_IMG_DATA`, `APOLLO_DISPLAY_IMG`, `APOLLO_ERASE_DISPLAY`, and `APOLLO_INIT_DISPLAY`. Hecuba interface bits include wakeup, data strobe, read/write, command/data, and acknowledge bits. `struct hecubafb_par` stores the `fb_info`, board pointer, and send-command/send-data callbacks. `struct hecuba_board` supplies module ownership plus `remove`, `set_ctl`, `set_data`, `wait_for_ack`, and `init` callbacks.

## Control Flow
The framebuffer driver calls board initialization, emits Apollo commands/data through `send_command` and `send_data`, toggles board control/data lines via board callbacks, waits for acknowledge transitions, and displays or erases images with the controller command bytes.

## State and Persistence Behavior
Runtime state is limited to the framebuffer private data and board callbacks. Image persistence is primarily an e-paper hardware property after `APOLLO_DISPLAY_IMG`; the header has no persistent software store.

## Dependencies and Integration Points
The header integrates framebuffer core state (`struct fb_info`), loadable board modules, and board-level GPIO or bus code. Board drivers can implement polling or interrupt-backed acknowledge waits.

## Risks and Test Signals
Risks include inverted control bits, missing acknowledge waits, callback lifetime issues with the owner module, and image transfer framing errors. Test signals include init/display/erase command traces, ack timeout testing, board remove cleanup, and framebuffer updates on real Hecuba/Apollo hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/hecubafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/ili9320.h -->
# sources/distributed-fs/ceph-client/include/video/ili9320.h

## Purpose
`ili9320.h` is the register, bitfield, SPI framing, suspend-mode, and platform-data definition header for the ILI9320 LCD controller. It lets board/display code describe panel size, reset handling, and controller initialization values.

## Important APIs, Types, and Functions
Register macros cover oscillator, driver, entry mode, display controls, RGB interface controls, power controls, GRAM address registers, gamma registers, address-window registers, scroll/partial-display registers, and interface registers. Bit macros include oscillator enable, driver scan options, entry-mode address/BGR/DFM/TRI bits, display-on fields, RGB interface modes and signal polarities, power rail fields, driver scan line fields, base-image flags, and interface timing fields. SPI helpers include `ILI9320_SPI_IDCODE`, `ILI9320_SPI_ID(x)`, read/write/data/index bits. `enum ili9320_suspend` distinguishes off vs deep suspend, and `struct ili9320_platdata` carries dimensions, reset callback, suspend policy, and platform-specific register values.

## Control Flow
Panel drivers assert/deassert reset through `platdata->reset`, write oscillator and power sequencing registers, program entry mode/RGB interface/gamma/window state, and later use GRAM address registers for pixel writes. Suspend chooses between controller-off and deeper sleep behavior from `enum ili9320_suspend`.

## State and Persistence Behavior
The header describes controller register state. Platform data remains for device lifetime; active display, gamma, interface, GRAM address, and power state reside in panel hardware and must be restored after reset or deep suspend.

## Dependencies and Integration Points
It integrates LCD platform drivers, SPI or parallel bus transports, framebuffer/LCD class code, and board-specific reset GPIO control. The register constants are the shared language between transport-neutral panel setup and bus-specific write routines.

## Risks and Test Signals
Risks include unmasked shift macros accepting out-of-range values, wrong RGB/BGR ordering, invalid power sequencing delays in implementation code, and reset callback polarity mistakes. Test signals include panel probe, suspend/resume in both modes, RGB interface timing validation, gamma/address-window programming, and pixel-format/color-order tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/ili9320.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/imx-ipu-image-convert.h -->
# sources/distributed-fs/ceph-client/include/video/imx-ipu-image-convert.h

## Purpose
`imx-ipu-image-convert.h` exposes the asynchronous image-conversion API for the i.MX IPU v3 image converter. It supports format adjustment/verification, prepared streaming contexts, queued conversion runs, abort, and one-shot conversion.

## Important APIs, Types, and Functions
`struct ipu_image_convert_ctx` is opaque. `struct ipu_image_convert_run` contains the context, input/output DMA addresses, completion status, and a private list node. `ipu_image_convert_cb_t` is the completion callback. APIs are `ipu_image_convert_adjust()`, `ipu_image_convert_verify()`, `ipu_image_convert_prepare()`, `ipu_image_convert_unprepare()`, `ipu_image_convert_queue()`, `ipu_image_convert_abort()`, and `ipu_image_convert()`.

## Control Flow
V4L2 drivers typically call `ipu_image_convert_adjust()` during try-format, `ipu_image_convert_verify()` before committing a format, `ipu_image_convert_prepare()` at stream-on, allocate and queue dynamic run objects while streaming, receive completed run objects through the callback, and call unprepare or abort at stream-off. The one-shot helper prepares and queues an initial run automatically while returning the context through `run->ctx`.

## State and Persistence Behavior
Conversion state is held in the opaque context and per-run objects. Active and pending runs are transient DMA operations; `unprepare()` and `abort()` complete outstanding runs with error status. No state persists beyond the conversion context or across reboot.

## Dependencies and Integration Points
The header depends on `video/imx-ipu-v3.h`, DMA address types, and Linux list infrastructure. It integrates V4L2 mem2mem/capture pipelines with IPU IC tasks, rotation modes, tiled conversion constraints, and DMA-backed image buffers.

## Risks and Test Signals
Risks include stack-allocated run objects despite the API requiring dynamic allocation, unverified formats reaching `prepare()`, callback lifetime races during abort/unprepare, DMA address mismatches, and leaked contexts after one-shot conversion. Test signals include try-format clamping, invalid-format rejection, repeated queue/complete cycles, abort while active and pending, stream-off cleanup, rotation/tile cases, and callback error-status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/imx-ipu-image-convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/imx-ipu-v3.h -->
# sources/distributed-fs/ceph-client/include/video/imx-ipu-v3.h

## Purpose
`imx-ipu-v3.h` is the central public interface for Freescale/NXP i.MX IPU v3 display, capture, DMA, conversion, deinterlace, and pixel-processing blocks. It defines hardware channel numbers, image formats, colorspace data, signal timing, and subsystem operations used by DRM, framebuffer, and V4L2 drivers.

## Important APIs, Types, and Functions
Important types include `struct ipu_soc`, `struct ipu_di_signal_cfg`, `struct ipuv3_channel`, `struct ipu_rgb`, `struct ipu_image`, `struct ipu_ic_colorspace`, `struct ipu_ic_csc_params`, `struct ipu_ic_csc`, and `struct ipu_client_platformdata`. Enums cover IPU variants, CSI destinations, rotation modes, color spaces, motion modes, channel IRQ types, IC tasks, and many fixed IDMAC channel numbers. APIs cover IRQ mapping, common mux/dump helpers, IDMAC get/put/enable/buffer/link operations, CPMEM programming, DC/DI/DMFC/DP/PRG/CSI/IC/VDI/SMFC get/put/configure/enable/disable paths, colorspace conversion calculation, DRM-fourcc and V4L2 pixel-format colorspace mapping, and degrees-to-rotation conversion. Inline helpers include `ipu_rot_mode_is_irt()`, `ipu_channel_alpha_channel()`, and `ipu_ic_fill_colorspace()`.

## Control Flow
Client drivers acquire IPU sub-block handles, configure muxes and timing, program channel parameter memory with image layout and DMA buffers, link flow units where needed, configure display or capture pipelines, enable sub-blocks in dependency order, service EOF/status IRQs, and disable/put resources during teardown. Display paths typically combine DI timing, DC/DMFC/DP setup, IDMAC channels, and optional PRG. Capture/conversion paths combine CSI/SMFC/IC/VDI and IDMAC channels.

## State and Persistence Behavior
State is in opaque IPU objects and hardware registers: channel allocation, buffer-ready bits, CPMEM descriptors, flow links, display timing, colorspace matrices, and active sub-block enables. State lasts while devices and channels are held and is lost or restored through driver power-management paths, not persisted in files.

## Dependencies and Integration Points
The header depends on Linux types, V4L2, DRM color management, framebuffer bitfields, OF nodes, media bus formats, and generic `videomode`. It is a cross-subsystem integration point for DRM/KMS display drivers, V4L2 capture/mem2mem code, device tree platform data, DMA buffer programming, and IPU IRQ handling.

## Risks and Test Signals
Risks include channel-number misuse, incorrect alpha-channel mapping, unsupported rotation sent to non-IRT paths, colorspace/quantization errors, stale double-buffer readiness, incorrect enable/disable ordering, and resource leaks from unmatched get/put calls. Test signals include display modeset, capture streaming, IC conversion with RGB/YUV and limited/full range, deinterlace setup, PRG modifier support, suspend/resume, IRQ mapping, buffer flip timing, and static checks for get/put balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/imx-ipu-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/kyro.h -->
# sources/distributed-fs/ceph-client/include/video/kyro.h

## Purpose
`kyro.h` defines private framebuffer state and user ioctl payloads for the STMicroelectronics/PowerVR Kyro framebuffer driver, especially display timing and overlay/video-mode operations.

## Important APIs, Types, and Functions
`struct kyrofb_info` stores MMIO base, a 16-entry pseudo-palette, horizontal/vertical timing fields, resolution, refresh, pixel and horizontal clocks, pixel depth, and write-combine cookie. Ioctls use magic `k` and include overlay create, viewport set, video mode set, UV stride, overlay offset, and stride commands. Payload structs are `overlay_create`, `overlay_viewport_set`, and `set_video_mode`.

## Control Flow
The driver populates `kyrofb_info`, programs timing and palette data into hardware, and handles user ioctls by creating/configuring overlays or changing mode-related values. User-space passes simple width/height/linear/viewport/depth records through ioctl.

## State and Persistence Behavior
State is per-framebuffer runtime state plus hardware overlay/mode registers. The pseudo-palette is cached in software for console/framebuffer use; no persistent configuration is stored by this header.

## Dependencies and Integration Points
It integrates framebuffer driver internals, PCI/MMIO mapping, write-combining setup, and legacy user-space overlay ioctl ABI. It expects Linux ioctl encoding and fixed-width types from included kernel headers.

## Risks and Test Signals
Risks include ioctl ABI compatibility, unchecked dimensions or linear flags, stale write-combine mappings, and mismatch between cached timing fields and programmed hardware. Test signals include fbdev mode changes, palette updates, overlay creation/viewport ioctls from 32-bit and native userspace, stride/offset validation, and unload cleanup of MMIO/write-combine resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/kyro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mach64.h -->
# sources/distributed-fs/ceph-client/include/video/mach64.h

## Purpose
`mach64.h` is a comprehensive ATI Mach64/Rage register and bit definition catalog for framebuffer and acceleration drivers. It maps CRTC, memory, DAC, clock/PLL, GUI engine, overlay/capture, AGP, LCD, power-management, and chip-identification registers.

## Important APIs, Types, and Functions
The file defines macros only. Major register groups include CRTC timing, DSP/memory-buffer controls, cursor, clock/PLL, configuration/status, memory control, DAC, GUI draw engine destination/source/host/pattern/scissor/data-path/color-compare/FIFO/status registers, overlay/capture/scaler, AGP, LCD panel controls, and VGA extended registers. Important field families cover mix/ROP values, engine bounds, bus/test/DSP masks, PLL indices and fields, memory and DAC types, chip IDs for GX/CX/CT/ET/VT/GT/Rage XL/Mobility variants, `IS_XL()` and `IS_MOBILITY()` predicates, destination/source/data-path pixel width fields, GUI status bits, power-management masks, and LCD stretching/LVDS/backlight fields.

## Control Flow
No functions exist, but driver control flow follows the register groups: identify chip and memory/DAC/clock type, program PLL and CRTC timings, configure memory/DSP FIFO thresholds, initialize DAC/palette and cursor state, enable the GUI engine, emit accelerated blit/fill/line operations through draw-engine registers, and manage LCD/power states on mobile chips.

## State and Persistence Behavior
The header owns no state. It names hardware state held in Mach64 registers, including mode timings, FIFO thresholds, engine command state, cursor/palette, panel stretch state, and power-management mode. That state persists until reset, suspend, or driver reprogramming.

## Dependencies and Integration Points
It is consumed by ATI Mach64 framebuffer code and any low-level helper that performs MMIO or port-I/O register access. It integrates PCI chip discovery, VGA compatibility, fbdev acceleration, DAC/PLL setup, LCD panel management, overlay/capture, and suspend/resume power handling.

## Risks and Test Signals
Risks include wrong offsets across chip families, using CT/ET/VT/GT-specific masks on the wrong ASIC, FIFO/engine programming without idle checks, PLL misprogramming, and ABI regressions in accelerated fb operations. Test signals include chip-ID detection on representative Mach64/Rage variants, mode-setting across pixel depths, accelerated copy/fill/text, cursor/palette tests, LCD stretch/backlight on Mobility hardware, suspend/resume restore, and static review of duplicate aliases and family-specific registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mach64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/maxinefb.h -->
# sources/distributed-fs/ceph-client/include/video/maxinefb.h

## Purpose
`maxinefb.h` provides fixed physical/KSEG1 addresses and register numbers for the DECstation 5000/xx onboard framebuffer and IMS332 video controller.

## Important APIs, Types, and Functions
The file defines `MAXINEFB_IMS332_ADDRESS`, `DS5000_xx_ONBOARD_FBMEM_START`, and IMS332 register indices for cursor RAM, color palette, and cursor color palette. There are no functions or structs.

## Control Flow
Framebuffer code maps or directly accesses the uncached KSEG1 framebuffer base and IMS332 registers, then programs palette and hardware cursor memory using the register numbers multiplied by the controller's 32-bit register spacing.

## State and Persistence Behavior
Framebuffer pixels and IMS332 palette/cursor state are hardware memory/register state. They persist while the machine remains powered and are reset by firmware or driver initialization.

## Dependencies and Integration Points
The header depends on MIPS `asm/addrspace.h` for `KSEG1ADDR`. It integrates DECstation platform framebuffer code with fixed legacy memory maps.

## Risks and Test Signals
Risks include using cached instead of uncached addresses, wrong register scaling by four, palette byte-order mistakes (`0x00BBGGRR`), and assuming the onboard framebuffer exists on other DECstation models. Test signals include console display on DECstation 5000/xx, palette writes, cursor rendering, and platform gating around the fixed address map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/maxinefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/metronomefb.h -->
# sources/distributed-fs/ceph-client/include/video/metronomefb.h

## Purpose
`metronomefb.h` defines the memory layout and board callback contract for the Metronome e-paper framebuffer controller.

## Important APIs, Types, and Functions
`struct metromem_cmd` describes a 64-byte command packet with opcode, argument words, and checksum. `struct metronomefb_par` stores command, waveform, image, checksum, DMA, framebuffer, board, waitqueue, frame count, size, and timing data. `struct metronome_board` provides reset/standby, cleanup, event wait, interrupt setup, framebuffer and I/O setup, panel type query, shared memory pointer, framebuffer dimensions, waveform size, and host framebuffer pointer.

## Control Flow
The driver asks the board to set up I/O, framebuffer memory, IRQs, and panel metadata; then it fills command/image/waveform memory, computes checksums, toggles reset/standby lines, waits for controller events, and coordinates with the host LCD controller when present.

## State and Persistence Behavior
Runtime state includes DMA-backed metronome memory, frame counters, checksums, waitqueue state, and board callbacks. E-paper display contents can remain visible without refresh, but software state is transient and must be rebuilt after device reset.

## Dependencies and Integration Points
It integrates fbdev, DMA memory, wait queues, board/platform code, IRQ setup, and optional host LCD controller state. Board callbacks hide GPIO, memory-mapping, and event-delivery details.

## Risks and Test Signals
Risks include checksum mismatch, DMA buffer layout errors, incorrect waveform size, event wait deadlocks, reset/standby polarity mistakes, and host framebuffer coordination failures. Test signals include command checksum validation, full/partial update events, interrupt and polling wait paths, suspend/resume, cleanup after failed setup stages, and visual e-paper refresh correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/metronomefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mipi_display.h -->
# sources/distributed-fs/ceph-client/include/video/mipi_display.h

## Purpose
`mipi_display.h` is a shared constant header for MIPI Display standards, especially DSI packet data types and DCS command/pixel-format values. It is used by panel, bridge, DSI host, and display driver code to construct and decode protocol packets.

## Important APIs, Types, and Functions
The first enum lists processor-to-peripheral DSI transaction types, including sync events, generic short/read/long writes, DCS short/read/long writes, max-return-packet-size, null/blanking packets, compressed streams, and packed pixel stream encodings. The second enum lists peripheral-to-processor responses, including acknowledge/error and short/long read responses. The DCS enum includes reset, display ID/status/power/pixel-format reads, sleep/normal/partial/invert/display on/off commands, address-window commands, memory read/write, tearing, scroll, brightness/CABC, DDB, and PPS commands. Pixel-format macros encode DCS 24/18/16/12/8/3-bit values.

## Control Flow
DSI hosts and panel drivers select a packet type, command byte, and payload length, then transmit through their bus-specific APIs. Read paths decode response packet type constants and map command reads to returned bytes. Video mode code uses pixel-stream packet constants for stream setup.

## State and Persistence Behavior
The header has no state. The constants represent wire-protocol values; resulting state lives in the panel or DSI host after packets are sent.

## Dependencies and Integration Points
It is standalone and integrates with DRM MIPI DSI helpers, fbdev panel drivers, bridge drivers, and vendor-specific panel init sequences. It provides the common vocabulary for DCS commands across otherwise unrelated drivers.

## Risks and Test Signals
Risks include confusing generic and DCS packet types, wrong packed-pixel stream selection, DCS version differences for newer brightness/CABC/PPS commands, and assuming all panels support every command. Test signals include packet trace comparison, panel init/readback, DSI error-report handling, pixel-format negotiation, display on/off/sleep transitions, and read-response decoding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mipi_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mmp_disp.h -->
# sources/distributed-fs/ceph-client/include/video/mmp_disp.h

## Purpose
`mmp_disp.h` defines the common display-controller interface for Marvell MMP display paths, overlays, panels, modes, and platform data. It gives buffer, controller, and panel drivers a shared object model and callback surface.

## Important APIs, Types, and Functions
Pixel formats include packed/planar YUV, RGB565/1555/888, RGBA/BGRA, RGB666, and pseudocolor; `pixfmt_to_stride()` returns bytes per pixel or luma-plane stride unit. Core structs include `mmp_win`, `mmp_addr`, `mmp_mode`, `mmp_overlay_ops`, `mmp_overlay`, `mmp_panel`, `mmp_path_ops`, `mmp_path`, `mmp_path_info`, `mmp_buffer_driver_mach_info`, `mmp_mach_path_config`, `mmp_mach_plat_info`, and `mmp_mach_panel_info`. Public APIs register and look up paths/panels and inline helpers dispatch mode, on/off, modelist, overlay, fetch, window, and address operations.

## Control Flow
Controller drivers register paths with overlay ops and path callbacks. Panel drivers register panels matched by path name. Buffer/fb drivers look up a path, get an overlay, set fetch ID, window geometry, DMA addresses, and enable status. Path mode and power callbacks propagate to controller-specific hardware code and panel callbacks.

## State and Persistence Behavior
Runtime state is in path and overlay objects: open counts, status, mode, current window, DMA addresses, panel attachment, and mutexes. Registration lists persist for device lifetime only; no persistent storage exists.

## Dependencies and Integration Points
The header depends on Linux kthreads indirectly, devices, list heads, mutexes, and flexible array support. It integrates MMP display controllers, panels, fb/buffer drivers, DMA fetch IDs, platform machine data, and output types such as parallel, DSI, and HDMI.

## Risks and Test Signals
Risks include missing null checks on callback pointers despite inline object checks, incorrect stride for planar formats, open-count/status races, overlay flexible-array allocation errors, and path/panel name mismatches. Test signals include path/panel registration and unregister, modelist propagation, overlay window/address programming for each format class, concurrent open/close, DSI/HDMI/parallel output selection, and invalid pixfmt stride behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/mmp_disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/neomagic.h -->
# sources/distributed-fs/ceph-client/include/video/neomagic.h

## Purpose
`neomagic.h` defines NeoMagic framebuffer acceleration, cursor, VGA-extension, PCI ID, MMIO, and private-state metadata for the NeoMagic fbdev driver.

## Important APIs, Types, and Functions
Macros cover blitter status/control bits, mode depth/resolution bits, cursor register offsets and flags, sync-suppression bits, debug logging, PCI chip IDs, MMIO size, and extended CRTC/graphics register limits. `Neo2200` maps blitter/MMIO registers such as status, control, colors, pitch, clip, source/destination, extent, and page registers. `struct neofb_par` stores VGA state, register images for VGA and panel registers, clock programming fields, write-combine cookie, MMIO base, cursor state, Neo2200 MMIO pointer, panel dimensions, clock limit, display routing flags, quirks, and pseudo-palette. `biosMode` maps a resolution to a BIOS mode number.

## Control Flow
The driver saves VGA/panel registers into `neofb_par`, programs mode and clock fields, uses MMIO blitter registers for accelerated operations, updates cursor registers relative to `cursorOff`, and restores cached register state during mode switches or suspend/resume.

## State and Persistence Behavior
`neofb_par` is the runtime state carrier and register-image cache. Hardware state includes VGA registers, panel centering, blitter registers, cursor memory, and palette. The software cache persists for the framebuffer lifetime and is not stored across reboot.

## Dependencies and Integration Points
The kernel-only part depends on VGA state handling, PCI IDs, MMIO mapping, fbdev console/palette paths, and write-combining setup. It integrates laptop internal/external panel routing, legacy VGA registers, and Neo2200 acceleration.

## Risks and Test Signals
Risks include register image drift, chip-ID-specific behavior, cursor memory lifetime (`cursorPad` comment marks a weak area), blitter FIFO/busy synchronization, and panel stretch/internal/external output quirks. Test signals include mode-set and restore across supported chips, accelerated fill/copy, cursor enable/move, palette updates, suspend/resume, internal/external display toggles, and debug builds with `NEOFB_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/neomagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/newport.h -->
# sources/distributed-fs/ceph-client/include/video/newport.h

## Purpose
`newport.h` defines the SGI NEWPORT graphics hardware register layout, draw-mode/control bitfields, context snapshot type, and inline helper routines for VC2, color map, XMAP9, and busy-wait operations.

## Important APIs, Types, and Functions
Core MMIO types are `npireg_t`, `npfreg_t`, `union np_dcb`, `struct newport_rexregs`, `struct newport_cregs`, `struct newport_regs`, and `newport_ctx`. Register fields cover REX draw modes, plane/depth/source/blend/logical-op bits, geometry iterators, color/slope values, DCB mode/data, configuration/status bits, VC2 indexed registers/control bits, color-map access, DCB protocol cycles, XMAP9 FIFO/mode controls, and BT445 access. Inline helpers include `newport_vc2_set()`, `newport_vc2_get()`, `newport_cmap_setaddr()`, `newport_cmap_setrgb()`, `newport_wait()`, `newport_bfwait()`, `xmap9FIFOWait()`, and `xmap9SetModeReg()`.

## Control Flow
Drivers write `regs->set` to stage REX/DCB state and `regs->go` to execute operations. VC2 helpers write DCB mode words, send indexed register addresses and data, and read back indexed values. Color-map helpers set an address and stream RGB data. Busy waits poll graphics or bus-busy status until idle or timeout. XMAP9 programming waits for FIFO availability and selects protocol timing based on clock frequency.

## State and Persistence Behavior
Hardware state includes REX draw registers, clipping/configuration, DCB devices, VC2 timing/cursor/display controls, color maps, and XMAP9 mode registers. `newport_ctx` can snapshot selected graphics state for context save/restore. No file-backed persistence exists.

## Dependencies and Integration Points
It integrates SGI framebuffer/graphics code with NEWPORT REX, VC2 video timing, CMAP/XMAP RAMDAC-style devices, and DCB bus protocols. It uses volatile MMIO structure access rather than accessor functions.

## Risks and Test Signals
Risks include endian-sensitive DCB byte/word access, busy-wait timeout tuning, incorrect set/go register selection, DCB protocol timing mistakes at different pixel clocks, and context save omissions. Test signals include mode setup through VC2, palette updates, XMAP9 mode programming at multiple clock ranges, accelerated draw operations, timeout-path tests for busy waits, and visual cursor/color correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/newport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/nomodeset.h -->
# sources/distributed-fs/ceph-client/include/video/nomodeset.h

## Purpose
`nomodeset.h` declares the shared helper that tells display drivers whether boot policy restricts them to firmware-provided display drivers only.

## Important APIs, Types, and Functions
The only API is `bool video_firmware_drivers_only(void);`.

## Control Flow
Display drivers call the helper during probe or modeset-driver selection. A true result should make native modesetting drivers defer or avoid binding so firmware framebuffer/simple display drivers remain in control.

## State and Persistence Behavior
The header owns no state. The implementation likely reflects boot parameters or global video policy established during kernel initialization; that policy persists for the boot session.

## Dependencies and Integration Points
It integrates DRM/fbdev/native graphics drivers with global video boot policy and firmware framebuffer fallback behavior.

## Risks and Test Signals
Risks include drivers ignoring the helper, using it too late after hardware takeover, or returning inconsistent policy between built-in and module drivers. Test signals include booting with and without `nomodeset`, verifying native GPU driver probe suppression, firmware framebuffer retention, and no regression for drivers that are themselves firmware/simple display drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/nomodeset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/of_display_timing.h -->
# sources/distributed-fs/ceph-client/include/video/of_display_timing.h

## Purpose
`of_display_timing.h` declares Open Firmware/device-tree helpers for reading display timing nodes into generic display timing structures.

## Important APIs, Types, and Functions
`OF_USE_NATIVE_MODE` is `-1`. With `CONFIG_OF`, APIs are `of_get_display_timing()` and `of_get_display_timings()`. Without OF, inline stubs return `-ENOSYS` or `NULL`.

## Control Flow
Panel or display drivers call these helpers with a device node and timing name or parent node. The OF implementation parses timing properties and optionally native-mode selection; non-OF builds compile through the stubs and must handle failure.

## State and Persistence Behavior
The helpers allocate or fill runtime timing structures from static device-tree data. The header itself owns no state; callers own returned `display_timings` lifetimes as defined by the implementation.

## Dependencies and Integration Points
It depends on `linux/errno.h` and forward declarations for device tree and timing structs. It integrates panel/display drivers with DT `display-timings` bindings and generic timing conversion code.

## Risks and Test Signals
Risks include callers not handling `-ENOSYS`/`NULL`, native-mode index misuse, malformed DT timing ranges, and memory-lifetime mistakes around returned timing sets. Test signals include DT parsing for named and native modes, non-OF build coverage, invalid/missing property handling, and conversion into videomode or controller-specific timing structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/of_display_timing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/of_videomode.h -->
# sources/distributed-fs/ceph-client/include/video/of_videomode.h

## Purpose
`of_videomode.h` declares the device-tree helper for retrieving a `struct videomode` from a display-timings node by index.

## Important APIs, Types, and Functions
The single API is `int of_get_videomode(struct device_node *np, struct videomode *vm, int index);` with forward declarations for `device_node` and `videomode`.

## Control Flow
Drivers call the helper during probe or mode enumeration. It parses the indexed timing from DT and writes the normalized `videomode` output for later controller-specific setup.

## State and Persistence Behavior
The helper fills caller-owned runtime memory from static DT data. The header has no state or persistence behavior.

## Dependencies and Integration Points
It integrates DT panel/display timing descriptions with the generic `videomode` representation and downstream display controller programming.

## Risks and Test Signals
Risks include invalid index handling, missing display-timings nodes, callers ignoring parse errors, and mismatches between DT ranges and fixed controller capabilities. Test signals include indexed timing parsing, native/default timing selection through callers, malformed DT cases, and mode application on a controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/of_videomode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/omapfb_dss.h -->
# sources/distributed-fs/ceph-client/include/video/omapfb_dss.h

## Purpose
`omapfb_dss.h` defines the legacy OMAP Display Subsystem fbdev-facing API: display types, planes, overlay managers, timings, DSI configuration, output-driver operation tables, display-device state, driver callbacks, registration APIs, ISR APIs, and CONFIG-dependent stubs.

## Important APIs, Types, and Functions
Important definitions include DISPC IRQ masks, `enum omap_display_type`, `omap_plane`, `omap_channel`, `omap_color_mode`, load modes, transparency key types, signal levels/edges, VENC type, DSI pixel format/mode/transfer mode, display caps/state, rotation type/angle, overlay caps, and output IDs. Core structs include DSI video/config data, `omap_video_timings`, CPR coefficients, `omap_overlay_info`, `omap_overlay`, `omap_overlay_manager_info`, `omap_overlay_manager`, `omap_dsi_pin_config`, `omap_dss_writeback_info`, per-output ops tables for DPI/SDI/DVI/ATV/HDMI/DSI, `omap_dss_device`, and `omap_dss_driver`. APIs under `CONFIG_FB_OMAP2` cover version/init checks, driver/display/output registration, device iteration/find/get/put, timing conversion, feature queries, overlay/manager access, output connection, default helpers, DISPC ISR registration, compatibility init, and OF source lookup; stubs provide compile-time no-op or failure behavior when disabled.

## Control Flow
Display drivers register `omap_dss_driver` callbacks and `omap_dss_device` instances. Outputs connect source and destination devices, managers bind overlays to outputs, overlay info is programmed, managers apply pending state and wait for go/vsync, and DISPC ISRs report frame/underflow/sync events. DSI paths additionally configure pins, bus timing, virtual channels, HS/LP behavior, packet reads/writes, TE, and update callbacks.

## State and Persistence Behavior
Runtime state is rich: display devices track source/destination links, state, manager/output bindings, timing, caps, type-specific PHY fields, panel fields, driver pointer, owner, and resume activation flag. Overlays and managers hold dynamic binding and info state. State lasts while registered and is restored through driver suspend/resume, not persisted across reboot.

## Dependencies and Integration Points
The header depends on Linux list/kobject/device/interrupt APIs, OMAP DSS platform data, videomode, HDMI/audio infoframe forward declarations, and device tree. It integrates fbdev OMAP display, panels, encoders, HDMI/DVI/DSI/VENC outputs, DISPC interrupts, overlay composition, writeback, and DT graph discovery.

## Risks and Test Signals
Risks include calling blocking operations from interrupt context despite comments, state drift between overlay/manager/display objects, CONFIG stub behavior hiding missing dependencies, DSI virtual-channel leaks, timing conversion errors, and sync/underflow interrupt mishandling. Test signals include driver/display/output registration lifecycle, overlay manager apply/go/vsync waits, DISPC ISR mask registration, DSI command/video mode transfers, HDMI EDID/infoframe paths, VENC PAL/NTSC timings, suspend/resume activation, and builds with and without `CONFIG_FB_OMAP2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/omapfb_dss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/omapvrfb.h -->
# sources/distributed-fs/ceph-client/include/video/omapvrfb.h

## Purpose
`omapvrfb.h` exposes the OMAP VRFB rotation-engine interface used to map framebuffer memory at multiple rotation angles.

## Important APIs, Types, and Functions
`OMAP_VRFB_LINE_LEN` is 2048. `struct vrfb` stores context id, four virtual and physical angle views, resolution, offsets, bytes per pixel, and YUV mode. With `CONFIG_OMAP2_VRFB`, APIs include support check, context request/release, size adjustment, minimum physical size, maximum height, setup, angle mapping, and context restore. Without the option, inline stubs return safe defaults or no-op.

## Control Flow
Callers check support, request a VRFB context, adjust dimensions to VRFB alignment, allocate enough physical memory, call setup with physical base and geometry, map a requested rotation angle, use the selected rotated view for display or blit, and release the context during teardown. Resume paths call restore context.

## State and Persistence Behavior
VRFB context state is in `struct vrfb` and hardware mapping registers. It persists while the context is allocated and must be restored after suspend or hardware reset. Stub builds provide no real hardware state.

## Dependencies and Integration Points
It integrates OMAP fbdev/DSS rotation paths with a SoC-specific memory remapping engine. It depends on MMIO pointer types and is often used with overlay rotation settings in OMAP display code.

## Risks and Test Signals
Risks include treating stub success as real rotation support, underallocating physical memory due to alignment, invalid rotation indices, context leaks, and missing restore after resume. Test signals include all four rotation angles, YUV and RGB modes, max-height/min-size calculations, suspend/resume restore, context exhaustion, and builds without `CONFIG_OMAP2_VRFB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/omapvrfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/permedia2.h -->
# sources/distributed-fs/ceph-client/include/video/permedia2.h

## Purpose
`permedia2.h` defines register offsets, RAMDAC indexed registers, flags, constants, and chip type identifiers for the 3Dlabs Permedia2 framebuffer driver.

## Important APIs, Types, and Functions
Constants include reference/max pixel clocks, register aperture size, and `PM2TAG(r)` for FIFO tags. Register groups cover reset/FIFO/aperture/config, memory control, output FIFO, screen timing, RAMDAC palette/cursor/indexed registers, rasterizer/render/scissor/texture/framebuffer/local-buffer/YUV/statistics/sync paths, and Permedia2V-specific RAMDAC extensions. Field macros cover render primitive/fast fill/texture/sync bits, PLL lock/reset, VGA/video enable, RAMDAC palette width/pixel formats, sync polarities, framebuffer read/write enables, texture sizes, delta order, memory bank count, aperture swap modes, and cursor mode. `pm2type_t` distinguishes Permedia2 and Permedia2V.

## Control Flow
The framebuffer driver probes the chip type, maps the register aperture, programs RAMDAC clocks and pixel format, writes screen timing and video enable registers, sets palette/cursor state, and may use render/framebuffer registers for fills or synchronization. `PM2TAG()` supports tagged FIFO command emission.

## State and Persistence Behavior
The header names hardware registers only. Runtime state includes programmed mode timing, RAMDAC state, cursor palette/pattern, framebuffer masks, and render engine configuration held in the device.

## Dependencies and Integration Points
It integrates fbdev mode setting and acceleration with Permedia2/Permedia2V MMIO and RAMDAC programming. It assumes Linux fixed-width integer types in consuming code.

## Risks and Test Signals
Risks include using Permedia2V extensions on base hardware, incorrect RAMDAC indexed register access, PLL lock handling, FIFO tag mistakes, and pixel-format/sync-polarity mismatches. Test signals include mode setting near clock limits, palette/cursor operations, render sync/fill, FIFO-space handling, Permedia2 vs Permedia2V probe paths, and register-offset audit against hardware specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/permedia2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pixel_format.h -->
# sources/distributed-fs/ceph-client/include/video/pixel_format.h

## Purpose
`pixel_format.h` provides a small generic pixel-format descriptor and comparison helpers for indexed and RGB bitfield formats.

## Important APIs, Types, and Functions
`struct pixel_format` stores bits per pixel, an indexed flag, and either index bitfield metadata or alpha/red/green/blue bitfields. Predefined initializer macros include `PIXEL_FORMAT_C8`, `XRGB1555`, `RGB565`, `RGB888`, `XRGB8888`, `XBGR8888`, and `XRGB2101010`. `pixel_format_cmp()` performs lexicographic comparison of descriptor fields, and `pixel_format_equal()` wraps it for equality.

## Control Flow
Callers construct or use predefined descriptors, then compare them to select compatible formats, sort formats, or test exact equality. For indexed formats only the index field is compared; for non-indexed formats alpha/red/green/blue fields are compared in order.

## State and Persistence Behavior
There is no runtime state beyond caller-owned descriptors. The predefined macros are compile-time initializers.

## Dependencies and Integration Points
It integrates display/fb helper code that needs format matching independent of DRM fourcc or fbdev var structures. It expects `bool` to be available from including headers.

## Risks and Test Signals
Risks include comparing non-normalized descriptors, missing alpha semantics for X formats, callers assuming `memcmp()` byte layout instead of documented ordering, and unmasked initializer values. Test signals include equality and ordering unit tests across indexed/RGB formats, compile coverage for static initializers, and conversion tests from fbdev/DRM format descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pixel_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/platform_lcd.h -->
# sources/distributed-fs/ceph-client/include/video/platform_lcd.h

## Purpose
`platform_lcd.h` defines a minimal generic platform-LCD power-control callback interface.

## Important APIs, Types, and Functions
`struct plat_lcd_data` contains `probe` and `set_power` callbacks. The same struct is forward-declared before definition for callback signatures.

## Control Flow
A platform LCD driver or board file supplies the callbacks. The LCD device calls `probe()` for board-specific initialization and `set_power()` when display power state changes.

## State and Persistence Behavior
The header carries no state. Any power state or GPIO/regulator state is held by the board-specific implementation.

## Dependencies and Integration Points
It integrates simple platform LCD devices with board-specific power sequencing, usually around GPIOs, regulators, or panel enable lines.

## Risks and Test Signals
Risks include underspecified power values, missing error reporting from `set_power`, callback lifetime issues, and inconsistent sequencing with framebuffer enable/disable. Test signals include probe failure handling, repeated power on/off, suspend/resume, and board-specific GPIO/regulator traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/platform_lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pm3fb.h -->
# sources/distributed-fs/ceph-client/include/video/pm3fb.h

## Purpose
`pm3fb.h` is the register and bitfield definition header for the 3Dlabs GLINT Permedia3 framebuffer driver. It covers control/status, memory, video timing, overlay, RAMDAC, 3D/render, framebuffer/local-buffer, texture, 2D setup, alias registers, ioctl, FIFO, and clock limits.

## Important APIs, Types, and Functions
The file defines macros only. Major groups include `PM3ResetStatus` and control/status registers, aperture mode fields, memory control, screen timing and `PM3VideoControl`, overlay mode/geometry/scaling registers, direct and indexed RAMDAC registers, cursor and overlay RAMDAC controls, D/K/M clock setup and lock fields, framebuffer read/write buffer registers, local-buffer read/write formats, logical operation, LUT, pixel-size, render, rasterizer, scissor, texture, window, 2D config/render/glyph/rectangle registers, fill aliases, sync/statistics/filter registers, `PM3FBIO_RESETCHIP`, `PM3_FIFO_SIZE`, `PM3_REGS_SIZE`, and `PM3_MAX_PIXCLOCK`.

## Control Flow
The framebuffer driver maps registers, programs memory/aperture and clock/RAMDAC state, sets screen timing and video enable bits, configures palette/cursor/overlay, uses framebuffer/render/2D setup registers for accelerated operations, waits for sync/completion, and may expose reset through the ioctl constant.

## State and Persistence Behavior
All state represented is hardware state: clocks, display timing, RAMDAC/cursor/palette, overlay buffers/scaling, render and framebuffer modes, local-buffer settings, and FIFO/sync state. It persists until reset, mode change, or power transition.

## Dependencies and Integration Points
It integrates the pm3fb driver with PCI/MMIO register access, fbdev mode setting, RAMDAC programming, 2D acceleration, overlay support, and legacy ioctl userspace.

## Risks and Test Signals
Risks include wrong bitfield composition macros, FIFO overflow due to missing space checks, pixel clock programming beyond `PM3_MAX_PIXCLOCK`, overlay scaling division edge cases, reset ioctl ABI issues, and confusion between direct/indirect RAMDAC registers. Test signals include mode-setting across depths, palette/cursor, accelerated rectangles/glyphs/blits, overlay enable/scale/color formats, sync/fifo tests, reset ioctl behavior, and register audit against Permedia3 documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pm3fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pmag-ba-fb.h -->
# sources/distributed-fs/ceph-client/include/video/pmag-ba-fb.h

## Purpose
`pmag-ba-fb.h` defines memory-resource offsets and Bt459 RAMDAC register offsets for the TURBOchannel PMAG-BA Color Frame Buffer card.

## Important APIs, Types, and Functions
Resource offsets identify framebuffer memory, Bt459 RAMDAC, IRQ acknowledge, option ROM, Bt438 clock-chip reset, and total address-space size. Bt459 byte-wide register offsets include low/high address, data window, and color-map window. There are no functions or structs.

## Control Flow
The PMAG-BA driver maps the TURBOchannel resource, adds these offsets to reach framebuffer, RAMDAC, IRQ ack, ROM, and clock reset regions, then programs the Bt459 through address/data/cmap byte windows.

## State and Persistence Behavior
State is hardware state in framebuffer memory, Bt459 palette/control registers, IRQ latch, and clock chip. The header owns no runtime data.

## Dependencies and Integration Points
It integrates DEC TURBOchannel framebuffer probing with resource mapping, interrupt acknowledgment, RAMDAC palette setup, and option ROM access.

## Risks and Test Signals
Risks include overlapping ROM/Bt438 offset interpretation, byte-wide RAMDAC access alignment, missed IRQ acknowledgments, and mapping the wrong address-space size. Test signals include TURBOchannel resource probing, palette writes, IRQ ack behavior, framebuffer console output, and ROM/clock reset access sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pmag-ba-fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pmagb-b-fb.h -->
# sources/distributed-fs/ceph-client/include/video/pmagb-b-fb.h

## Purpose
`pmagb-b-fb.h` defines resource offsets and video timing field encodings for the TURBOchannel PMAGB-B Smart Frame Buffer card.

## Important APIs, Types, and Functions
Resource offsets cover option ROM, SFB ASIC, general-purpose outputs, Bt459 RAMDAC, framebuffer memory, and total size. SFB register offsets include horizontal/vertical video setup, video base address, and TURBOchannel/video clock counters. Field macros define back-porch, sync, front-porch, active-pixel/scan-line shifts and masks, base-row mask, and Bt459 byte-wide address/data/cmap offsets.

## Control Flow
The driver maps the card aperture, programs SFB timing registers by packing porch/sync/active fields, sets video base row, optionally reads clock counters, and configures the Bt459 palette through its byte-wide window.

## State and Persistence Behavior
Framebuffer memory, timing registers, GP outputs, and RAMDAC state are hardware state. No software state is defined in this header.

## Dependencies and Integration Points
It integrates TURBOchannel SFB hardware with DEC framebuffer drivers, mode timing setup, palette programming, and framebuffer memory mapping.

## Risks and Test Signals
Risks include incorrect shift/mask packing for timing fields, active pixel/line limits, video base row alignment, byte-wide Bt459 access mistakes, and confusion with PMAG-BA offsets. Test signals include known-resolution mode programming, palette update, framebuffer base panning if supported, clock-counter reads, and console display on PMAGB-B hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pmagb-b-fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pxa168fb.h -->
# sources/distributed-fs/ceph-client/include/video/pxa168fb.h

## Purpose
`pxa168fb.h` defines platform data, pixel formats, pin modes, and private framebuffer state for Marvell PXA168 LCD controller support.

## Important APIs, Types, and Functions
Macros define dumb/smart interface pin modes, dumb RGB lane allocation modes, default framebuffer size, and packed/planar RGB/YUV/pseudocolor pixel format constants including `PIX_FMT_UYVY422PACK`. `struct pxa168fb_info` stores device, clock, fb_info, MMIO base, DMA framebuffer start, pseudo-palette, pixel format, blanked/rbswap/active flags. `struct pxa168fb_mach_info` carries platform id, mode list, default pixel format, pin allocation, dumb-mode lane routing, GPIO output mask/data, signal polarity flags, panel lane swap, active state, and enable flag.

## Control Flow
Platform code supplies `pxa168fb_mach_info`; the driver maps registers, enables the clock, allocates framebuffer memory, selects a mode and pixel format, programs pin allocation and dumb/smart panel routing, sets signal polarities and GPIO output bits, and tracks blank/active state in `pxa168fb_info`.

## State and Persistence Behavior
Runtime state is split between immutable or boot-time machine info and mutable framebuffer info. Hardware state includes LCD controller registers, pin mux/output state, DMA framebuffer base, blank/active state, and pseudo-palette. It persists for device lifetime and must be restored after suspend/resume.

## Dependencies and Integration Points
It depends on fbdev mode structures, interrupt declarations, devices, clocks, MMIO, and DMA addresses from including code. It integrates PXA168 board files/platform data with fbdev, panel wiring, LCD clocks, and scanout buffer management.

## Risks and Test Signals
Risks include mismatched pixel format names with MMP formats, lane-swap and RGB/BGR confusion, insufficient default framebuffer size for larger modes, polarity errors, and active/blank state divergence from hardware. Test signals include each supported panel wiring mode, RGB/YUV pixel formats, pseudo-palette updates, blank/unblank, suspend/resume, clock enable/disable, DMA base programming, and platform mode-list validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/pxa168fb.h -->
