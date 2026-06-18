# subset-b-005571 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ps3fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/ps3fb.c

Purpose: implements the PlayStation 3 GPU framebuffer driver. It exposes a Linux fbdev backed by PS3 XDR video memory and mirrors the visible frame into GPU-accessible DDR memory through LV1 hypervisor blits and display flips.

Important APIs/types/functions: `struct ps3fb_priv` holds the global GPU context, mapped driver-info area, IRQ, vsync wait queue, open count, flip state, blank state, and update kthread. `struct ps3fb_par` is the per-fb mode state, including PS3 AV mode ids, frame counts, XDR/DDR pitches, frame sizes, offsets, and pseudo palette. Mode helpers include `ps3fb_cmp_mode`, `ps3fb_vmode`, `ps3fb_native_vmode`, and `ps3fb_find_mode`. fbdev operations are `ps3fb_check_var`, `ps3fb_set_par`, `ps3fb_setcolreg`, `ps3fb_pan_display`, `ps3fb_mmap`, `ps3fb_blank`, and `ps3fb_ioctl`. Probe and teardown are `ps3fb_probe`, `ps3fb_shutdown`, `ps3fb_init`, and `ps3fb_exit`.

Control flow: module init parses `ps3fb` options and registers a PS3 system-bus driver only when preallocated PS3 video memory exists. Probe opens the hypervisor GPU device, allocates GPU memory and context, maps driver-info memory, wires a vsync IRQ, maps XDR memory into the GPU IOIF aperture, sets up framebuffer support, registers fbdev, and starts `ps3fbd`. Mode changes flow through `fb_set_var`: `check_var` finds a compatible native PS3 AV mode and forces ARGB8888, while `set_par` sets PS3 AV output if needed, recalculates frame layout, clears XDR and DDR buffers, and primes display memory. Vsync interrupts update `vblank_count`, wake waiters, and kick the kthread to copy the visible frame unless userspace has enabled external flip mode. IOCTLs expose vblank wait/query, PS3 mode set/get, screen layout, external flip on/off, and explicit frame selection.

State and persistence: persistent state lives in the static `ps3fb` singleton, per-framebuffer `ps3fb_par`, hypervisor GPU allocations, mapped driver-info memory, and the fbdev mode/cmap. The framebuffer memory is cleared at setup and mode changes to avoid stale data exposure. Runtime updates are synchronized with `ps3_gpu_mutex`, fb console locks, atomics, a wait queue, and a kthread. State does not persist across module unload or shutdown; teardown unregisters fbdev, stops the kthread, frees IRQs and GPU resources, unmaps driver info, and closes the hypervisor device.

Dependencies and integration: depends on PS3 platform headers and services (`ps3av`, `ps3gpu`, `lv1call`, `ps3_system_bus`), fbdev/fbcon, Linux kthreads/freezer, IRQ handling, VM mmap helpers, and firmware version checks for XDR pitch constraints. It integrates with PS3 AV mode numbering and exports `PS3_MODULE_ALIAS_GPU_FB`.

Risks: mode matching and offset math must keep XDR virtual memory, DDR fullscreen memory, and PS3 AV native timing aligned. Hypervisor calls can fail at many stages, so cleanup order is critical. The kthread and IRQ share state through flags and atomics, making blanking and external flip paths race-sensitive. `ps3fb_find_mode` clamps line lengths differently on old firmware. IOCTLs copy user data and control display flips, so validation of mode ids and frame indices is essential.

Test signals: build with PS3 framebuffer support, boot on PS3 hardware, verify framebuffer registration and reported video memory, exercise fbcon, panning, mmap writes, blank/unblank, `FBIO_WAITFORVSYNC`, PS3 mode IOCTLs, external flip on/off, and shutdown/unload. Useful negative signals are LV1 call failures, missing vsync interrupts, timeout from wait-for-vsync, incorrect centered offsets, corrupted pitches, or stale contents after mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ps3fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pvr2fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pvr2fb.c

Purpose: provides fbdev support for NEC PowerVR2 display hardware, primarily Sega Dreamcast and optionally NEC Neon250 PCI boards. It programs display-window, sync, border, palette, and VRAM registers while presenting a packed-pixel framebuffer.

Important APIs/types/functions: `struct pvr2fb_par` stores derived hardware timing, border/window positions, display start address, interlace/doublescan/lowres flags, MMIO base, and a 16-entry pseudo palette. Parameter tables map cable and output names. fbdev operations include `pvr2fb_setcolreg`, `pvr2fb_blank`, `pvr2fb_check_var`, `pvr2fb_set_par`, and optional DMA-backed `pvr2fb_write`. Board paths are `pvr2fb_dc_init`/`pvr2fb_dc_exit` for Dreamcast and `pvr2fb_pci_probe`/`pvr2fb_pci_remove` for PCI. Shared setup is centralized in `pvr2fb_common_init`.

Control flow: module init parses non-module boot options, allocates one `fb_info`, then tries each compiled board backend. The Dreamcast backend checks `mach_is_dreamcast`, detects cable type through SH registers when not overridden, sets fixed VRAM/MMIO addresses, installs a vsync IRQ, and optionally reserves DMA. The PCI backend removes conflicting apertures, enables the PCI device, requests BAR regions, and supplies BARs as VRAM/MMIO. Common init maps VRAM and registers, clears VRAM, selects mode/pan/wrap defaults, finds an fb mode, allocates a cmap, registers fbdev, and forces initial display programming. Runtime mode setting converts fb margins back to PVR2 border and display-window registers. Vsync IRQs apply pending pan, full mode reprogram, and blank changes.

State and persistence: global module state includes `fb_info`, `currentpar`, cable/output options, pending `do_vmode_full`, `do_vmode_pan`, `do_blank`, and `is_blanked`. Hardware state persists in MMIO registers until mode changes, blanking, or driver removal. The framebuffer maps physical VRAM through `ioremap`; optional SH store queues add a cached write path. No persistent storage exists beyond hardware registers and module globals.

Dependencies and integration: depends on fbdev, aperture helpers, PCI core, SH Dreamcast platform registers/IRQs, optional PVR2 DMA support, optional SH store queues, and platform-specific cable/output detection. It integrates with fb mode parsing and the fb console through standard `fb_ops`.

Risks: the timing conversion is explicitly approximate and several mode comments mark undocumented or unstable behavior. `pvr2fb_set_par` computes `disp_start` using `(line_length * yoffset) * line_length`, which deserves scrutiny because a byte offset would normally be one multiplication by line length plus x offset. Global pending state is applied only from the vsync interrupt, so systems without the IRQ path may miss delayed updates. Optional DMA write pins user pages and uses a weak physical-contiguity check; boundary checks are sensitive to `count`, page rounding, and `ppos`. Cable/output overrides can drive incompatible sync modes.

Test signals: build Dreamcast and PCI configurations, boot with VGA and TV cable modes, check register programming through visible output, exercise mode selection, panning/ywrap, blank/unblank during vsync, cmap writes at 16/24/32 bpp, optional DMA writes, PCI probe/remove, and boot options (`cable:`, `output:`, `nopan`, `nowrap`, mode strings). Watch for invalid PAL/NTSC hsync totals, blanking stuck behind pending IRQ state, DMA short pins, and mismatched VRAM bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pvr2fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.c

Purpose: implements a Marvell PXA168/PXA910 LCD controller fbdev driver for a single graphics plane connected to a "dumb" panel. It allocates write-combined framebuffer memory, programs LCD controller registers, handles basic palette/truecolor modes, panning, blanking, and one graphics-frame IRQ.

Important APIs/types/functions: the driver consumes `struct pxa168fb_mach_info` platform data and uses `struct pxa168fb_info` from public platform headers as private fb state. Pixel format helpers are `determine_best_pix_fmt`, `set_pix_fmt`, and `set_mode`. Register programming helpers include `set_clock_divider`, `set_dma_control0`, `set_dma_control1`, `set_graphics_start`, `set_dumb_panel_control`, and `set_dumb_screen_dimensions`. fbdev operations are `pxa168fb_check_var`, `pxa168fb_set_par`, `pxa168fb_setcolreg`, `pxa168fb_blank`, and `pxa168fb_pan_display`. Driver lifecycle is `pxa168fb_probe` and `pxa168fb_remove`.

Control flow: probe requires platform data, an `LCDCLK`, one MMIO resource, and an IRQ. It allocates `fb_info`, initializes fixed fb metadata from platform data, maps registers, allocates `DEFAULT_FB_SIZE` write-combined DMA memory, sets the graphics start address, seeds the initial mode from platform modes/pixel format, builds a modelist, normalizes the mode, enables the clock, programs controller registers, initializes default SRAM/IO pad values, allocates a cmap, installs an IRQ, enables graphics frame interrupt, and registers fbdev. `check_var` selects a supported pixel format, validates pan bounds, total dimensions under 2048, and framebuffer size. `set_par` disables panel output, writes active size, clock divider, DMA controls, pitch, graphics dimensions, dumb-panel timing/polarity controls, porch registers, and re-enables output.

State and persistence: state is held in `pxa168fb_info`, fbdev `fix`/`var`/cmap, write-combined framebuffer memory, MMIO registers, and platform data fields such as RGB swap, dumb mode, GPIO masks, active flag, and polarity flags. `is_blanked` alters the dumb-panel mode to blank output. Panning is persistent through the graphics start-address register until changed. Remove disables graphics DMA, unregisters fbdev, disables IRQ generation, frees cmap and framebuffer memory, disables the clock, and releases fb_info.

Dependencies and integration: depends on platform-device resources, DMA mapping, Linux clk, fbdev modelist helpers, platform data in `<video/pxa168fb.h>`, and the local register map in `pxa168fb.h`. It does not include device tree matching in this source.

Risks: `determine_best_pix_fmt` mutates `fbi->pix_fmt` during `check_var`, so validation has side effects on private state. Clock divider programming uses only an integer divider despite comments about fractional stages. Register writes use literal bits for several fields rather than only local macros, increasing maintenance risk. `pxa168fb_remove` passes `info->fix.smem_start` as the DMA handle to `dma_free_wc`, relying on the stored physical address matching `fb_start_dma`. IRQ handling only acknowledges one graphics-frame condition and returns `IRQ_NONE` otherwise.

Test signals: build with PXA168/PXA910 platform data, probe with valid and missing resources, confirm framebuffer memory allocation and MMIO mapping, display known patterns at 8/16/24/32 bpp, verify pseudo-color SRAM palette writes, panning start-address changes, blank/unblank dumb-panel mode, clock rates for several modes, IRQ acknowledgement, and remove-path DMA/clock cleanup. Negative tests should cover unsupported bitfields, oversized virtual resolution, invalid total dimensions, and missing platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.h

Purpose: defines the local PXA168/PXA910 LCD controller register offsets and bitfield helpers used by `pxa168fb.c`. It is a hardware register map rather than an exported API header.

Important APIs/types/functions: no functions or structs are defined. Key register groups include video DMA start/pitch/size registers, graphics start/pitch/position/size registers, hardware cursor registers, total and active timing registers, porch and blank color registers, color-key and alpha controls, SPI and smart-panel registers, DMA control registers, SRAM controls, clock divider, contrast/saturation/hue controls, dumb-panel control, IO pad control, interrupt enable/status registers, and mode constants. Format constants include `VMODE_*` and `GMODE_*`; dumb panel constants include `DUMB16_RGB565_*`, `DUMB18_RGB666_*`, `DUMB24_RGB888_0`, and `DUMB_BLANK`; IO pad modes include `IOPAD_DUMB*` and `IOPAD_SMART*`.

Control flow: the header contributes symbolic addresses and bit encoders to driver control flow. `pxa168fb.c` uses graphics registers for framebuffer base/pitch/size, `LCD_SPU_DMA_CTRL0/1` for format and trigger control, `LCD_SPU_DUMB_CTRL` for panel enable/blanking/polarity, `LCD_CFG_SCLK_DIV` for pixel clock division, `SPU_IOPAD_CONTROL` for platform pin muxing, and `SPU_IRQ_ENA`/`SPU_IRQ_ISR` for graphics-frame interrupt handling.

State and persistence: these macros describe persistent MMIO state in the LCD controller. They do not store kernel state themselves. Register fields persist in hardware until rewritten, reset, power loss, or driver removal. Palette SRAM writes are coordinated through `LCD_SPU_SRAM_WRDAT` and `LCD_SPU_SRAM_CTRL`.

Dependencies and integration: included only by the PXA168 fb driver in this set. It complements public platform data from `<video/pxa168fb.h>` and Linux `readl`/`writel` register access. Names are hardware-specific and not namespaced for generic reuse.

Risks: many masks and shifts are open-coded macros with no type checking. Some comments contain typos or historical naming ("Dump LCD Panel Control Register"), so readers must validate against silicon documentation. Duplicate or similar bit names for DMA/video/graphics paths make it easy to program the wrong plane. The header contains no compile-time field range checks; out-of-range arguments can bleed into neighboring fields.

Test signals: compile coverage through `pxa168fb.c` is the primary signal. Hardware tests should verify that each macro group used by the driver writes the expected register values for panel timing, pixel formats, palette mode, RGB swap, blanking, IO pad allocation, and IRQ enable/acknowledge. Static review should compare offsets and masks against the PXA168/PXA910 LCD controller reference manual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.c

Purpose: implements the PXA3xx Graphics Controller Unit misc-device driver. It serves DirectFB-style userspace by accepting command batches through `write`, exposing a shared DMA area and MMIO through `mmap`, and offering reset/wait-idle ioctls.

Important APIs/types/functions: private state is `struct pxa3xx_gcu_priv`, containing MMIO, clock, shared DMA page, misc device, wait queues, spinlock, timestamp base, and free/ready/running batch lists. `struct pxa3xx_gcu_batch` wraps coherent DMA command buffers. Register helpers are `gc_readl` and `gc_writel`. Core engine functions are `pxa3xx_gcu_reset`, `run_ready`, `flush_running`, `pxa3xx_gcu_handle_irq`, `pxa3xx_gcu_wait_idle`, and `pxa3xx_gcu_wait_free`. File operations are `pxa3xx_gcu_open`, `pxa3xx_gcu_write`, `pxa3xx_gcu_ioctl`, and `pxa3xx_gcu_mmap`. Lifecycle functions are `pxa3xx_gcu_probe` and `pxa3xx_gcu_remove`.

Control flow: probe allocates private state, initializes queues and spinlock, configures a fixed-minor misc device, maps MMIO, gets/enables the clock, requests IRQ, allocates the shared coherent area, registers miscdev, allocates eight coherent batch buffers, stores platform drvdata, and resets hardware. A user `write` waits for a free batch if needed, copies command words from userspace, appends an end command, queues the batch on the ready list, and starts the engine if idle. `run_ready` builds a ring in the shared buffer that jumps through queued batch physical addresses, moves ready batches to running, and programs ring base/tail/length registers. IRQ handling consumes end-of-extended-buffer status, returns running batches to the free list, wakes waiters, starts more ready work or marks hardware idle, and clears status. IOCTL reset aborts/reinitializes under spinlock; wait-idle sleeps until `hw_running` clears or timeout logic detects no forward progress.

State and persistence: persistent state includes coherent shared memory visible to userspace, coherent batch buffers, hardware ring registers, list heads for free/ready/running batches, shared counters/statistics, and `hw_running`. State is protected primarily by a spinlock around list and hardware-start transitions; comments state that some statistic fields rely on userspace locking. Remove waits idle, deregisters miscdev, frees shared DMA, disables the clock, and frees only buffers on the free list.

Dependencies and integration: depends on platform-device resources, miscdevice, DMA coherent allocation/mmap, IRQs, spinlocks, wait queues, clk, OF matching for `marvell,pxa300-gcu`, and the ABI definitions in `pxa3xx-gcu.h`. Userspace must understand the shared structure, ioctls, batch format, and direct MMIO mapping.

Risks: the ABI deliberately exposes MMIO to userspace, so correctness and security depend heavily on trusted userspace. `remove` waits for idle before freeing, but `pxa3xx_gcu_free_buffers` walks only the free list, so forced teardown with batches still queued/running would leak unless idle completed. `pxa3xx_gcu_write` truncates `count` to 32-bit words and silently ignores trailing bytes. Timeout heuristics infer progress from hardware pointer changes and interrupt counts. The top comment notes an external system-bus arbiter enable requirement that Linux does not handle.

Test signals: build with misc device and OF matching, probe on PXA3xx with required bus arbiter setup, confirm `/dev/pxa3xx-gcu` registration, mmap shared area and MMIO at required offsets/sizes, submit batches below and above `PXA3XX_GCU_BATCH_WORDS`, exercise wait-free under more than eight queued batches, wait-idle completion, reset during idle and active states, IRQ-driven batch recycling, remove after idle, and timeout behavior with wedged hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.h

Purpose: defines the userspace-visible ABI for the PXA3xx GCU misc driver: shared memory layout, buffer sizing, ABI magic, batch size, and ioctl numbers.

Important APIs/types/functions: `PXA3XX_GCU_BUFFER_WORDS` sizes the shared ring-buffer command area to almost 256 KiB. `PXA3XX_GCU_SHARED_MAGIC` identifies the ABI version and is set by kernel reset for userspace validation. `PXA3XX_GCU_BATCH_WORDS` limits a submitted batch to 8192 32-bit words. `struct pxa3xx_gcu_shared` contains the command ring, `hw_running`, the physical ring address, statistic counters (`num_words`, `num_writes`, `num_done`, `num_interrupts`, `num_wait_idle`, `num_wait_free`, `num_idle`), and `magic`. IOCTLs are `PXA3XX_GCU_IOCTL_RESET` and `PXA3XX_GCU_IOCTL_WAIT_IDLE`.

Control flow: userspace mmaps the shared area described by this header, validates `magic`, observes `hw_running` and counters, submits command data with `write`, and uses ioctls for reset or idle synchronization. The driver writes `buffer_phys` and `magic` during `pxa3xx_gcu_reset`, increments counters during writes/waits/IRQs, and uses the ring buffer to chain DMA batch buffers.

State and persistence: this header defines shared kernel/userspace state but does not allocate it. Runtime state persists in coherent DMA memory until reset, driver removal, or device reset. Counters are diagnostic, not transactional, and comments in the C file indicate not all updates are atomic.

Dependencies and integration: included by `pxa3xx-gcu.c` and expected by the matching DirectFB or other userspace client. It uses Linux integer types and `_IO` ioctl encoding via the C file's includes.

Risks: changing `struct pxa3xx_gcu_shared`, buffer sizing, or ioctl values breaks userspace unless `PXA3XX_GCU_SHARED_MAGIC` is bumped. `unsigned long buffer_phys` is ABI-width dependent, which matters for 32-bit versus 64-bit consumers. The shared flags and counters are not a complete synchronization contract by themselves.

Test signals: compile the kernel driver and userspace client against the same header, verify `magic`, mmap size, ioctl numbers, and batch-size rejection. ABI tests should check 32-bit userspace assumptions, counter monotonicity, and reset reinitialization of `hw_running`, `buffer_phys`, and statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-gcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-regs.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-regs.h

Purpose: supplies PXA2xx/PXA3xx LCD controller register offsets and bitfield macros used by `pxafb.c` for base plane, overlays, palette DMA, interrupts, timing, and smart-panel command programming.

Important APIs/types/functions: no functions or structs are defined. Major register offsets include `LCCR0` through `LCCR5`, `LCSR`/`LCSR1`, branch registers `FBR0` through `FBR6`, overlay controls `OVL1C*`/`OVL2C*`, command/status registers `CMDCR` and `PRSR`, frame descriptor registers `FDADR0` through `FDADR6`, and TMED registers. Macros encode control bits such as `LCCR0_ENB`, `LCCR0_LCDT`, `LCCR0_OUC`, `LCCR3_BPP`, `LCCR3_PixClkDiv`, `LCCR4_PAL_FOR_*`, interrupt masks/status bits, `LDCMD_PAL`, overlay dimensions/position/format, and smart-panel status flags.

Control flow: `pxafb.c` uses this header to derive shadow register values in mode activation, program panel timing, enable/disable the LCD controller, construct DMA descriptors with palette chaining, branch to new frame descriptors for panning and overlays, handle disable/command/branch interrupts, and encode overlay dimensions and pixel formats.

State and persistence: the header defines MMIO state layout only. Actual state persists in LCD controller registers and DMA descriptor memory managed by `pxafb.c`. Macros such as `LCCR1_DisWdth`, `LCCR2_DisHght`, and `OVLxC1_PPL` encode "value minus one" hardware fields, so caller inputs become persistent hardware timing.

Dependencies and integration: local to the fbdev PXA driver family in this source set. It is included by `pxafb.c`, which supplies register accessors and policy. It reflects hardware definitions and must remain aligned with platform data flags from `<linux/platform_data/video-pxafb.h>`.

Risks: macro arguments are not range checked and can underflow for zero values in "minus one" encoders. Some branch register comments are copy-pasted and label several registers as DMA channel 2. Polarity macros use multiplication by zero/one constants, which can be surprising but is intentional for bit selection. Incorrect mask use can leave interrupts unmasked or acknowledge the wrong channel.

Test signals: compile coverage through `pxafb.c`, static comparison against hardware reference manuals, and hardware tests for panel enable/disable, timing, palette DMA, panning branch registers, overlay enable/disable branch completions, smart-panel command completion, and IRQ status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.c

Purpose: implements the Intel/Marvell PXA2xx/PXA3xx LCD controller fbdev driver. It supports base framebuffer operation, palette and truecolor formats, panning through DMA branch descriptors, optional PXA27x/PXA3xx overlay framebuffers, optional smart-panel command DMA, cpufreq retiming, power management, platform data, and device tree display timings.

Important APIs/types/functions: private state and DMA structures are defined in `pxafb.h`; register bits come from `pxa3xx-regs.h`. Important helpers include `pxafb_var_to_bpp`, `pxafb_var_to_lccr3`, `pxafb_set_pixfmt`, `pxafb_getmode`, `pxafb_adjust_timing`, `setup_frame_dma`, `setup_base_frame`, `get_pcd`, `setup_parallel_timing`, `setup_smart_timing`, `pxafb_activate_var`, `set_ctrlr_state`, `pxafb_enable_controller`, `pxafb_disable_controller`, and `pxafb_handle_irq`. fbdev operations are `pxafb_check_var`, `pxafb_set_par`, `pxafb_pan_display`, `pxafb_setcolreg`, and `pxafb_blank`. Optional overlay operations are `overlayfb_open`, `overlayfb_release`, `overlayfb_check_var`, and `overlayfb_set_par`. Probe/remove are `pxafb_probe` and `pxafb_remove`.

Control flow: init parses optional `pxafb` parameters and registers the platform driver. Probe copies platform data or derives modes from device tree, applies command-line overrides, validates mode data, allocates and initializes `pxafb_info`, maps MMIO, allocates coherent DMA descriptor/palette/command memory, allocates video RAM, requests IRQ, initializes smart-panel support if configured, validates and applies the initial mode, registers fbdev, initializes overlays, registers cpufreq notifier, and enables the controller. Mode setting normalizes requested formats and geometry, prepares palette/cmap state, calculates timing registers and DMA descriptors, and schedules controller re-enable if active registers differ. Blanking, PM, cpufreq, and reprogramming are serialized through `set_ctrlr_state` and a work item so sleepable disable/enable sequences run in task context.

State and persistence: persistent driver state includes `pxafb_info`, fbdev state, coherent DMA descriptor buffer, palette memory, optional smart command buffer, allocated framebuffer memory, overlay framebuffer memory, shadow registers `reg_lccr*`, physical descriptor addresses, controller state machine values, completions, regulator/clock state, and platform callbacks. Hardware state persists in LCD controller registers until rewritten. Panning persists by branch register updates, overlays persist through overlay control registers and descriptors, and smart-panel updates persist through command DMA.

Dependencies and integration: depends on fbdev, platform devices, clk, DMA coherent allocation, IRQs, cpufreq notifier, PM hooks, regulator framework, PXA CPU detection, platform data in `<linux/platform_data/video-pxafb.h>`, optional OF graph/display timings, and optional smart-panel/overlay Kconfig features. It exports no module symbols from this file, but smart-panel helpers are callable within the driver when configured.

Risks: this is a broad hardware driver with multiple optional paths sharing descriptor arrays and registers. Mode validation depends on platform data quality and only warns on some illegal LCCR combinations. Controller state transitions mix workqueue, mutex, completions, IRQs, cpufreq, and PM, so races around disable/re-enable and overlay activity are plausible. Overlay memory is separately allocated and must be freed only after unregister. Smart-panel path starts a kthread but remove does not visibly stop it in this file, requiring careful config-path review. Command-line parsing uses many string prefixes and mutates platform timing in place.

Test signals: build matrix with base driver, `CONFIG_FB_PXA_OVERLAY`, `CONFIG_FB_PXA_SMARTPANEL`, `CONFIG_CPU_FREQ`, `CONFIG_PM`, platform data, and OF timings. Runtime tests should cover probe/remove failure unwinds, mode validation, palette and truecolor cmap behavior, panning branch completion, blank/unblank, suspend/resume, cpufreq transition, regulator callbacks, smart-panel queue/flush/timeouts, overlay open/set/release for RGB and YUV formats, and IRQ completion for disable, command, and branch events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.h

Purpose: defines private data structures, DMA descriptor layouts, overlay metadata, controller state constants, and geometry limits for `pxafb.c`.

Important APIs/types/functions: `struct pxafb_dma_descriptor` mirrors the hardware DMA descriptor fields `fdadr`, `fsadr`, `fidr`, and `ldcmd`. Palette and DMA channel enums define base, overlay, cursor, command, and branch descriptor indices. `struct pxafb_dma_buff` groups palette storage, smart-panel command buffer, palette descriptors, and doubled frame DMA descriptors for branch updates. Overlay definitions include `OVERLAY1`, `OVERLAY2`, YUV/RGB format ids, `NONSTD_TO_XPOS`, `NONSTD_TO_YPOS`, `NONSTD_TO_PFOR`, `struct pxafb_layer_ops`, and `struct pxafb_layer`. `struct pxafb_info` is the main driver state container.

Control flow: `pxafb.c` allocates `struct pxafb_info`, fills it from platform data, and uses the embedded `fb_info` as the registered base framebuffer. DMA setup writes into `pxafb_dma_buff`; panning and overlays select channel indices from the enums; smart-panel code writes commands into `cmd_buff`; state transitions use `C_DISABLE`, `C_ENABLE`, `C_DISABLE_CLKCHANGE`, `C_ENABLE_CLKCHANGE`, `C_REENABLE`, `C_DISABLE_PM`, `C_ENABLE_PM`, and `C_STARTUP`.

State and persistence: `pxafb_info` persists for the lifetime of the platform device and holds MMIO base, clock, DMA buffers and physical addresses, framebuffer memory and physical address, palette pointer/size, platform-derived LCCR config, shadow registers, hsync timing, volatile controller state, workqueue and mutex synchronization, completions, optional smart-panel thread state, optional overlay state, cpufreq notifier, regulator state, power callbacks, and copied machine info. Overlay state tracks registered status, usage count, control registers, video memory, branch completion, and parent pointer.

Dependencies and integration: included by `pxafb.c` and relies on fbdev, clk, DMA address types, completions, mutexes, work structs, wait queues, regulators, notifier blocks, and platform machine info definitions included by the C file before this header.

Risks: this private header is tightly coupled to `pxafb.c`; changing enum order or descriptor layout can break hardware programming. The doubled descriptor arrays rely on `DMA_MAX * 2` and `PAL_MAX * 2` indexing discipline. `video_mem` is declared `void __iomem *` even though it is allocated with normal pages in `pxafb.c`, which can confuse access assumptions. `state` and `task_state` are volatile bytes, but correctness depends on external locking/workqueue rules rather than volatility.

Test signals: compile all optional PXA framebuffer configurations, validate descriptor offsets with `offsetof` users in `pxafb.c`, run overlay and smart-panel paths that exercise every channel enum, and check controller state transitions during blanking, PM, and cpufreq changes. Static review should ensure every allocated field is released on remove/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pxafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/q40fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/q40fb.c

Purpose: implements a minimal fbdev driver for the Q40 m68k machine framebuffer. It exposes a fixed 1024x512 16-bpp truecolor framebuffer at the Q40 physical screen address.

Important APIs/types/functions: `q40fb_fix` describes fixed framebuffer properties: id `Q40`, 1 MiB memory, packed pixels, truecolor, 2048-byte lines, and no acceleration. `q40fb_var` describes the fixed mode and RGB bitfields. `q40fb_setcolreg` fills the 16-entry pseudo palette for truecolor console use. `q40fb_probe` allocates/registers fbdev and enables display hardware. `q40fb_init` registers both a platform driver and synthetic platform device.

Control flow: module init exits if fb options disable `q40fb`, then registers the platform driver and platform device. Probe rejects non-Q40 machines with `MACH_IS_Q40`, sets `smem_start` to `0xFE800000`, allocates `fb_info` with space for a 16-entry pseudo palette, copies fixed/variable mode data, points `screen_base` at the already mapped physical screen address, allocates a 256-entry cmap, writes display control via `master_outb(3, DISPLAY_CONTROL_REG)`, and registers the framebuffer.

State and persistence: state is limited to static fixed/variable descriptors, one allocated `fb_info`, the pseudo palette stored in `info->par`, the cmap, and the Q40 display control register. There is no remove path or dynamic mode state. Framebuffer contents persist in physical screen memory while the machine is running.

Dependencies and integration: depends on m68k Q40 platform macros/register access (`MACH_IS_Q40`, `master_outb`, `DISPLAY_CONTROL_REG`), fbdev default I/O-memory ops, platform-device registration, and fixed early mapping from Q40 setup code.

Risks: no remove/unregister path is present because this is effectively a built-in style platform driver. `screen_base` is assigned from the physical address cast to a pointer, relying on Q40 setup mapping. Color bitfields are unusual (`red` offset 6, `green` 11, `blue` 0 with 6 blue bits), so palette conversion must match hardware. The driver accepts color register numbers up to 255 but only uses pseudo palette entries below 16.

Test signals: build for Q40/m68k, boot on Q40 or emulator with `MACH_IS_Q40`, verify fbdev registration, visible 1024x512 output, correct fbcon colors through pseudo palette, cmap allocation, and display enable register side effect. Negative signal is probe returning `-ENXIO` on non-Q40 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/q40fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/Makefile

Purpose: describes the Kbuild composition of the Riva framebuffer driver module/object.

Important APIs/types/functions: `obj-$(CONFIG_FB_RIVA) += rivafb.o` builds the driver when `CONFIG_FB_RIVA` is enabled. `rivafb-objs := fbdev.o riva_hw.o nv_driver.o` composes the main object from fbdev glue, Riva hardware support, and NV driver code. When `CONFIG_FB_RIVA_I2C` is enabled, `rivafb-i2c.o` is appended to `rivafb-objs`.

Control flow: Kbuild evaluates the config symbols at build time. With Riva framebuffer disabled, no object is built from this directory entry. With it enabled, the listed objects are linked into `rivafb.o`; optional I2C support is included only under its config symbol.

State and persistence: no runtime state exists in the Makefile. Its persistent effect is the build graph and the resulting linked object composition.

Dependencies and integration: integrates with Linux Kbuild, fbdev Riva source files in the same directory, and Kconfig symbols `CONFIG_FB_RIVA` and `CONFIG_FB_RIVA_I2C`. The SPDX tag declares GPL-2.0.

Risks: object ordering can matter if initialization or unresolved symbol dependencies rely on link order. New source files must be added to `rivafb-objs` under the correct config guard. If Kconfig changes symbol names, this Makefile must be updated or the driver silently stops building optional pieces.

Test signals: run kernel builds with `CONFIG_FB_RIVA=n`, `m`, or `y`, and with `CONFIG_FB_RIVA_I2C` toggled. Confirm `rivafb.o` includes `rivafb-i2c.o` only when expected and that all listed source objects are present in the directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/Makefile -->
