# subset-b-005522 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.c

Purpose: implements the MediaTek MTU3 gadget Queue Management Unit support. QMU offloads data movement for non-control endpoints by programming General Purpose Descriptors in DMA-coherent rings, starting/stopping endpoint queues, translating hardware current-pointer registers back to software descriptors, completing `usb_request` objects, and handling QMU exception interrupts.

Important APIs, types, and functions: the file operates on `struct mtu3`, `struct mtu3_ep`, `struct mtu3_request`, `struct mtu3_gpd_ring`, and hardware `struct qmu_gpd`. Public entry points are `mtu3_qmu_init`, `mtu3_qmu_exit`, `mtu3_gpd_ring_alloc`, `mtu3_gpd_ring_free`, `mtu3_prepare_transfer`, `mtu3_insert_gpd`, `mtu3_qmu_start`, `mtu3_qmu_stop`, `mtu3_qmu_resume`, `mtu3_qmu_flush`, and `mtu3_qmu_isr`. Internal helpers convert GPD virtual/DMA addresses, read/write TX/RX queue start/current registers including high-address fields, advance ring enqueue/dequeue cursors, prepare TX/RX GPDs, walk completed descriptors, and recover RX or ZLP-related TX errors.

Control flow: `mtu3_qmu_init` creates a DMA pool sized for one endpoint ring and asserts that GPDs are 16 bytes. Each endpoint calls `mtu3_gpd_ring_alloc`, which allocates a zeroed `MAX_GPD_NUM` ring and initializes `start`, `enqueue`, `dequeue`, and `end`. Queueing code in the gadget layer calls `mtu3_prepare_transfer` to check ring space, then `mtu3_insert_gpd`; TX descriptors carry request DMA address, request length, next-GPD address, IOC/HWO flags, and old/new SoC ZLP encoding, while RX descriptors carry buffer length and next-GPD address. `mtu3_qmu_start` writes the ring DMA base to endpoint-specific TQSAR/RQSAR plus high-address registers, enables endpoint DMA request bits, configures ZLP/coalescing/error interrupts, and starts the hardware queue unless already active. `mtu3_qmu_stop` writes STOP, polls `QMU_Q_ACTIVE` clear in atomic context, and flushes TX FIFO before and after stop.

Interrupt flow: `mtu3_qmu_isr` reads masked done status from `U3D_QISAR0`, acknowledges it with W1C, reads exception status from `U3D_QISAR1`, emits trace data, and dispatches done processing before exception processing. `qmu_done_tx` and `qmu_done_rx` translate current GPD DMA pointer into a ring pointer, then walk from `dequeue` until current or a hardware-owned descriptor is reached. For each completed descriptor they verify that the next queued request owns that GPD, set `request.actual` from the descriptor data length, trace it, and complete the request through `mtu3_req_complete`. `qmu_exception_isr` handles RX checksum/length errors by marking the active request `-EAGAIN`, bypassing the descriptor, and resuming QMU; RX ZLP errors are logged; TX length errors are used on older SoCs to send a ZLP through BMU after disabling DMAREQEN and waiting for FIFO room.

State and persistence: there is no on-disk persistence. Runtime state is the per-endpoint GPD ring, DMA pool, `mreq->gpd` pointer, hardware queue registers, endpoint DMA enable bits, request queue state owned by the gadget layer, and SoC variant flag `mtu->gen2cp`, which changes descriptor field layout and ZLP encoding. The ring deliberately reserves one descriptor slot to simplify full/empty handling. Memory barriers ensure HWO is set only after descriptor contents and next-pointer fields are visible to hardware.

Dependencies and integration points: depends on Linux DMA pool APIs, `readl_poll_timeout_atomic`, MTU3 register helpers/macros from `mtu3.h`, USB gadget request state, and tracepoints from `mtu3_trace.h`. It is called from the MTU3 gadget endpoint queue/start/stop paths and feeds completions back through `mtu3_req_complete`. It directly controls QMU and endpoint DMA registers under the broader MTU3 interrupt and endpoint-locking model.

Risks: descriptor ownership is ordering-sensitive; moving the barrier or setting HWO before next/buffer fields can expose partially initialized GPDs. `gpd_dma_to_virt` returns NULL for out-of-ring current pointers, but completion paths do not deeply recover beyond breaking or logging, so corrupted hardware pointers can stall queues. `gpd_ring_empty` is really a "no free GPD" test because one slot is reserved; callers must preserve that convention. TX ZLP handling intentionally triggers length-error flow on old SoCs, making error interrupt masking part of normal behavior. `mtu3_qmu_stop` uses fixed 1 ms polling and only logs on timeout, so teardown may proceed with stale hardware state. Error recovery bypasses descriptors and resumes hardware, which must match request queue ownership exactly to avoid completing the wrong request.

Test signals: build with MTU3 gadget/QMU support and both original and gen2cp descriptor layouts. Runtime tests should cover ring allocation/free, full-ring queue refusal, TX and RX transfers at zero, short, maxpacket, and multi-packet sizes, request zero/ZLP handling on both SoC formats, QMU start when active/inactive, stop timeout behavior, flush resetting cursors, RX checksum/length/ZLP exception paths, TX length-error ZLP path, completion races where a second request finishes before a tasklet-style pass, DMA addresses above 4 GiB, and disconnect/reset while requests are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.h

Purpose: declares the MTU3 QMU interface used by the gadget endpoint code and defines descriptor-ring sizing and maximum buffer constants. It is the narrow public contract for allocating QMU rings, preparing descriptors, controlling hardware queues, and servicing QMU interrupts.

Important APIs, types, and symbols: constants are `MAX_GPD_NUM`, `QMU_GPD_SIZE`, `QMU_GPD_RING_SIZE`, `GPD_BUF_SIZE`, and `GPD_BUF_SIZE_EL`. Function declarations cover queue control (`mtu3_qmu_start`, `mtu3_qmu_stop`, `mtu3_qmu_resume`, `mtu3_qmu_flush`), descriptor insertion and capacity checks (`mtu3_insert_gpd`, `mtu3_prepare_transfer`), ring lifetime (`mtu3_gpd_ring_alloc`, `mtu3_gpd_ring_free`), interrupt handling (`mtu3_qmu_isr`), and global pool lifetime (`mtu3_qmu_init`, `mtu3_qmu_exit`).

Control flow: the header encodes the lifecycle expected by users: initialize the controller QMU pool once, allocate a ring per endpoint, prepare/insert GPDs as requests are queued, start/resume/stop/flush the endpoint queue as endpoint state changes, handle QMU interrupts through `mtu3_qmu_isr`, free endpoint rings, and finally destroy the controller pool.

State and persistence: no persistent state is declared. The constants define in-memory DMA ring shape: 64 descriptors per endpoint and one contiguous ring sized as `MAX_GPD_NUM * sizeof(struct qmu_gpd)`. Buffer limits distinguish original hardware with roughly 64 KiB GPD data length from extended layout hardware with roughly 1 MiB descriptors.

Dependencies and integration points: assumes `struct mtu3`, `struct mtu3_ep`, `struct mtu3_request`, `struct qmu_gpd`, and `irqreturn_t` are visible through the including MTU3 driver headers. It is consumed by MTU3 gadget and core files that need QMU acceleration but keeps descriptor bit layout private to `mtu3_qmu.c`.

Risks: `QMU_GPD_SIZE` depends on the included definition of `struct qmu_gpd`; compile-time ordering matters. The buffer-size constants are not enforced in this header, so callers and descriptor-preparation code must ensure request segmentation or rejection. `mtu3_prepare_transfer` has a misleading name because its implementation returns the ring-full condition rather than preparing hardware directly.

Test signals: compile all MTU3 files that include this header, check `QMU_GPD_SIZE == 16` at runtime build assertion in `mtu3_qmu.c`, and exercise queueing limits around 64 descriptors plus old/new hardware maximum request lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.c

Purpose: materializes MTU3 tracepoints and provides a formatted debug helper that routes driver log messages into the trace subsystem. It is the single translation unit that defines the trace events declared in `mtu3_trace.h`.

Important APIs, types, and functions: `CREATE_TRACE_POINTS` causes `mtu3_trace.h` to instantiate tracepoint storage and generated functions. `mtu3_dbg_trace(struct device *dev, const char *fmt, ...)` wraps varargs in `struct va_format` and emits `trace_mtu3_log`. It includes `mtu3_debug.h` first so debug macros can call into this helper and includes `mtu3_trace.h` for event definitions.

Control flow: any MTU3 code using the debug trace helper passes a device and format string. `mtu3_dbg_trace` initializes a `va_list`, packages it as `va_format`, calls the tracepoint, and then releases the `va_list`. Tracepoint enablement/filtering is handled by the kernel tracing infrastructure, not by this file.

State and persistence: there is no driver state or persistent data. Runtime effects are trace ring-buffer records controlled by ftrace/perf tracing configuration.

Dependencies and integration points: depends on Linux tracepoint support, `struct device`, `struct va_format`, and the MTU3 trace header. It integrates with the MTU3 driver's debugging path and with user-visible tracing under the `mtu3` trace system.

Risks: this file must be compiled exactly once for the MTU3 trace events; defining `CREATE_TRACE_POINTS` elsewhere would duplicate symbols, while omitting this object would leave trace events unresolved. The helper forwards a live `va_list` only during the trace call, so tracepoint code must consume it synchronously, which matches `__vstring` tracepoint semantics.

Test signals: build with tracing enabled, ensure `mtu3_trace.o` is included once, enable `mtu3:mtu3_log` through tracefs, trigger MTU3 debug paths, and verify formatted device-prefixed messages appear without format warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.h

Purpose: declares the tracepoint surface for the MediaTek MTU3 controller driver. The events cover generic driver logs, USB2/USB3 interrupt summaries, QMU interrupt summaries, control setup packets, gadget request lifecycle, QMU GPD preparation/completion/ZLP handling, and gadget endpoint state.

Important APIs, types, and events: `TRACE_SYSTEM mtu3` groups events under `mtu3`. `TRACE_EVENT(mtu3_log)` records device name and formatted message. Interrupt events are `mtu3_u3_ltssm_isr`, `mtu3_u2_common_isr`, and `mtu3_qmu_isr`. Event classes `mtu3_log_setup`, `mtu3_log_request`, `mtu3_log_gpd`, and `mtu3_log_ep` define reusable payloads for setup packets, `struct mtu3_request`, `struct qmu_gpd`, and `struct mtu3_ep`; derived events include `mtu3_handle_setup`, `mtu3_alloc_request`, `mtu3_free_request`, `mtu3_gadget_queue`, `mtu3_gadget_dequeue`, `mtu3_req_complete`, `mtu3_prepare_gpd`, `mtu3_complete_gpd`, `mtu3_zlp_exp_gpd`, `mtu3_gadget_ep_enable`, `mtu3_gadget_ep_disable`, and `mtu3_gadget_ep_set_halt`.

Control flow: included normally, the header provides tracepoint declarations and inline call sites through generated `trace_mtu3_*` functions. Included from `mtu3_trace.c` with `CREATE_TRACE_POINTS`, it instantiates the tracepoint definitions. The footer sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE mtu3_trace` so `trace/define_trace.h` can locate this header during kernel trace generation.

State and persistence: no persistent state is owned here. Each enabled event snapshots selected runtime fields: endpoint names, flags, GPD words converted from little-endian, request actual/length/status/zero/no_interrupt fields, setup packet fields converted from little-endian, and interrupt bitmasks. Disabled tracepoints have minimal static-key overhead.

Dependencies and integration points: includes Linux tracepoint infrastructure and `mtu3.h` for register bit names and MTU3 structures. It integrates with QMU code, gadget endpoint code, setup handling, and interrupt handlers. User-space consumers see these events through tracefs/perf/ftrace using the `mtu3` event system.

Risks: trace events dereference driver pointers such as `mreq->mep`, `mep->gpd_ring`, and `gpd` fields, so call sites must only trace while those objects are valid. Event print formats assume MTU3 bit definitions from `mtu3.h` are visible and stable. The event name/API surface is consumed by tracing scripts, so renaming events or changing payloads can break diagnostics. The header must remain safe for multiple inclusion under `TRACE_HEADER_MULTI_READ`.

Test signals: build with `CONFIG_TRACEPOINTS`, enable individual MTU3 events, exercise setup packets, endpoint enable/disable/halt, request queue/dequeue/complete, QMU descriptor preparation/completion, QMU exceptions, USB2 reset/suspend/resume, and USB3 LTSSM interrupts; verify decoded event output matches hardware register state and does not fault when requests complete concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/Kconfig

Purpose: defines the kernel configuration surface for Mentor Graphics Inventra MUSB high-speed dual-role USB controller support, including role selection, platform glue drivers, and DMA engine choices.

Important APIs, types, and options: top-level `USB_MUSB_HDRC` builds the `musb-hdrc` core when USB host or gadget infrastructure and MMIO are available. The role choice offers `USB_MUSB_HOST`, `USB_MUSB_GADGET`, and `USB_MUSB_DUAL_ROLE`, with dependencies ensuring host/gadget framework availability and DMA for gadget/dual-role operation. Platform glue symbols include `USB_MUSB_SUNXI`, `USB_MUSB_DA8XX`, `USB_MUSB_TUSB6010`, `USB_MUSB_OMAP2PLUS`, `USB_MUSB_DSPS`, `USB_MUSB_UX500`, `USB_MUSB_JZ4740`, `USB_MUSB_MEDIATEK`, and `USB_MUSB_POLARFIRE_SOC`. DMA options include `MUSB_PIO_ONLY`, `USB_UX500_DMA`, `USB_INVENTRA_DMA`, `USB_TI_CPPI41_DMA`, and `USB_TUSB_OMAP_DMA`.

Control flow: enabling `USB_MUSB_HDRC` opens a role selection and then platform/DMA selections. Platform symbols select or depend on needed PHY, extcon, role-switch, architecture, OF, or DMAengine support. DMA options are hidden when `MUSB_PIO_ONLY` is selected, making PIO the guaranteed fallback and DMA a per-platform compile-time feature.

State and persistence: Kconfig state is build-time only and persists in the kernel `.config`. It controls which source objects are compiled by the Makefile and which conditional code paths are visible in the core and glue drivers.

Dependencies and integration points: integrates with Linux USB host core, USB gadget core, architecture symbols, PHY frameworks, extcon, role switch, DMAengine, TI CPPI41, and platform-specific SoC support. The Makefile consumes these symbols to build core, gadget, host, debugfs, platform glue, and DMA backend objects.

Risks: invalid combinations can be subtle because role symbols concatenate in the Makefile to include host/gadget objects. `USB_INVENTRA_DMA` is shared across OMAP2PLUS, MediaTek, JZ4740, and PolarFire, so enabling it without compatible platform ops would fail later. `USB_MUSB_POLARFIRE_SOC` selects dual-role mode directly, which can surprise configurations expecting role choice only from user selection. PIO-only builds must still compile all role paths that reference DMA abstractions through stubs.

Test signals: run Kconfig build matrix for host-only, gadget-only, dual-role, and PIO-only; compile each platform glue under its architecture and `COMPILE_TEST` where allowed; verify module names and dependencies; and check that DMA backends are included only when their platform and DMA symbols are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/Makefile

Purpose: maps MUSB Kconfig symbols to kernel objects, assembling the common `musb_hdrc` core module plus optional host, gadget, debugfs, platform glue, and DMA backend objects.

Important APIs, types, and targets: `obj-$(CONFIG_USB_MUSB_HDRC) += musb_hdrc.o` builds the core module. `musb_hdrc-y` always includes `musb_core.o` and `musb_trace.o`. Host support adds `musb_virthub.o` and `musb_host.o`; gadget support adds `musb_gadget_ep0.o` and `musb_gadget.o`; debugfs adds `musb_debugfs.o`. Platform glue objects are `omap2430.o`, `musb_dsps.o`, `tusb6010.o`, `da8xx.o`, `ux500.o`, `jz4740.o`, `sunxi.o`, `mediatek.o`, and `mpfs.o`. DMA backend objects are `musbhsdma.o`, `tusb6010_omap.o`, `ux500_dma.o`, and `musb_cppi41.o`.

Control flow: Kbuild expands role symbols by concatenating `CONFIG_USB_MUSB_HOST` and `CONFIG_USB_MUSB_DUAL_ROLE` or gadget equivalents, so dual-role builds include both host and gadget objects. Trace compilation adds `-I$(src)` for `musb_trace.o` so `define_trace.h` can find the local trace header.

State and persistence: no runtime state. Build output shape persists in kernel/module artifacts: the main module is `musb_hdrc` while platform glue may be built as separate objects/modules depending on configuration.

Dependencies and integration points: consumes the symbols from `Kconfig` and depends on source files in the same directory. It integrates with Linux Kbuild's composite-object mechanism and tracepoint header include requirements.

Risks: role-object inclusion depends on string concatenation, so unusual Kconfig states could include or omit host/gadget code unexpectedly if dependencies regress. Tracepoint builds are sensitive to the local include path. Platform glue objects are built independently from the core object; symbol visibility through exports and module load ordering must remain valid.

Test signals: compile representative configurations for built-in and modular `USB_MUSB_HDRC`, all three roles, debugfs on/off, PIO-only and each DMA backend, and each platform glue as module where Kconfig permits. Verify `musb_trace.o` compiles with generated trace headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/cppi_dma.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/cppi_dma.h

Purpose: defines data structures and descriptor bit fields for TI CPPI and CPPI 4.1 DMA integration used by MUSB platforms. It is a private header shared by DMA backend implementation and platform glue that need CPPI channel/controller state.

Important APIs, types, and symbols: hardware state-RAM structures are `struct cppi_tx_stateram` and `struct cppi_rx_stateram`. Descriptor flags include `CPPI_SOP_SET`, `CPPI_EOP_SET`, `CPPI_OWN_SET`, `CPPI_EOQ_MASK`, `CPPI_ZERO_SET`, `CPPI_RXABT_MASK`, masks for packet/buffer length, and `CPPI_TEAR_READY`. `struct cppi_descriptor` models a CPPI buffer descriptor with hardware overlay fields plus software next pointer, DMA address, and original RX buffer length. `struct cppi_channel` wraps the generic `struct dma_channel` with MUSB endpoint, direction, RNDIS mode, buffer progress, state RAM, descriptor free/active lists, and TX completion list. `struct cppi` is the controller state for older CPPI channels. `struct cppi41_dma_channel` is the per-channel state used by the DMAengine-based CPPI 4.1 backend.

Control flow: older CPPI code uses descriptor/state-RAM definitions to program linked buffer descriptors and track active TX/RX channels. CPPI41 code uses `cppi41_dma_channel` with DMAengine channels, cookies, programmed/actual lengths, packet size, TX FIFO recheck list, ZLP flag, and saved USB toggle state.

State and persistence: no persistent storage. Runtime state is DMA descriptor memory, DMAengine channel state, CPPI state RAM registers, per-channel progress counters, allocation flags, and endpoint references. Descriptor alignment is fixed at 16 bytes for hardware consumption.

Dependencies and integration points: includes Linux list, slab, errno, DMA pool, DMAengine, and MUSB core/DMA abstraction headers. It connects MUSB's generic `dma_controller`/`dma_channel` interfaces to TI CPPI hardware and CPPI41 DMAengine plumbing used by DA8xx and DSPS glue.

Risks: hardware overlay structs must match CPPI state RAM and descriptor layout exactly. Descriptor ownership flags and teardown bits are hardware-visible, so endian/layout mistakes corrupt DMA. `struct cppi41_dma_channel` mixes generic DMA abstraction state and DMAengine state; lifecycle mismatches can leak DMA channels or complete stale transfers. The header exposes both older CPPI and CPPI41 models, so changes must avoid assuming one backend's fields apply to the other.

Test signals: compile CPPI41 and older CPPI users, validate descriptor alignment and field offsets against hardware documentation, run DMA TX/RX bulk traffic, exercise teardown/abort, RNDIS mode, ZLP generation, RX short packets, and channel allocation/release under repeated endpoint enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/cppi_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/da8xx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/da8xx.c

Purpose: implements the DA8xx/OMAP-L1x MUSB platform glue layer. It adapts the common MUSB core to TI DA8xx wrapper registers, mixed interrupt routing, clock/PHY handling, VBUS/ID polling quirks, CPPI41 DMA callbacks, child `musb-hdrc` platform-device registration, and suspend/resume.

Important APIs, types, and functions: `struct da8xx_glue` stores parent device, child MUSB platform device, generic USB PHY device, clock, and PHY. Register definitions describe the DA8xx USB wrapper, interrupt masks, endpoint masks, and Mentor core offset. Platform ops are `da8xx_ops` with quirks `MUSB_INDEXED_EP`, `MUSB_PRESERVE_SESSION`, `MUSB_DMA_CPPI41`, and `MUSB_DA8XX`; hooks include `da8xx_musb_init`, `da8xx_musb_exit`, `da8xx_musb_enable`, `da8xx_musb_disable`, `da8xx_musb_set_mode`, optional CPPI41 DMA init/exit, `da8xx_musb_try_idle`, `da8xx_babble_recover`, and `da8xx_musb_set_vbus`. Probe/remove are `da8xx_probe` and `da8xx_remove`.

Control flow: probe obtains clock and PHY, builds platform data from DT when present, registers a generic USB PHY, populates CPPI41 child devices from OF auxdata, and registers a `musb-hdrc` child with inherited resources and DA8xx platform ops. MUSB core initialization then calls `da8xx_musb_init`, which shifts `musb->mregs` by the Mentor core offset, enables the clock, checks wrapper revision, gets the USB2 PHY handle, sets up the OTG polling timer, resets the wrapper, initializes and powers the PHY, and installs `da8xx_musb_interrupt`. Enable/disable manipulate DA8xx wrapper interrupt mask registers rather than normal Mentor interrupt enable registers and force a DRVVBUS interrupt to start role polling.

Interrupt and role flow: `da8xx_musb_interrupt` reads masked wrapper interrupt status, clears it, maps wrapper TX/RX/USB bits into `musb->int_tx`, `musb->int_rx`, and `musb->int_usb`, handles DRVVBUS as a proxy for VBUS/ID change, applies VBUS error workaround state transitions, and then calls `musb_interrupt`. Because DA8xx lacks proper ID-change reporting, `otg_timer` periodically reads DEVCTL and transitions between A/B OTG states, forcing or clearing SESSION as needed. `set_mode` maps MUSB host/peripheral/OTG mode requests to generic PHY modes.

State and persistence: no persistent state. Runtime state lives in `da8xx_glue`, wrapper registers, MUSB core state, `musb->dev_timer`, PHY/clock state, and optional regulator-derived power value. Suspend powers off the PHY and disables the clock; resume re-enables the clock and PHY power.

Dependencies and integration points: depends on platform devices, OF, clocks, generic PHY, legacy `usb_phy_generic`, DMA mask setup, regulator current limit lookup, CPPI41 DMA if configured, and MUSB core platform ops. It binds OF compatible `ti,da830-musb` and registers `musb-hdrc` as a child.

Risks: DA8xx interrupt handling intentionally avoids normal Mentor IRQ registers except setup; using the wrong register set can lose interrupts. ID/VBUS state is inferred through DRVVBUS and polling, so timers and state transitions are fragile. `da8xx_probe` dereferences/updates `pdata` after optional DT allocation; non-DT platforms must provide valid platform data. Suspend/resume only handle PHY/clock at glue level while MUSB core also has PM state. CPPI41 DMA callback writes EOI, so DMA completion ordering with wrapper interrupt acknowledgement matters.

Test signals: build with and without `CONFIG_USB_TI_CPPI41_DMA`, probe through DT and platform data, verify child `musb-hdrc` registration, clock/PHY failure unwinds, wrapper interrupt masks, DRVVBUS host/device transitions, VBUS error workaround, babble recovery reset, regulator current-limit conversion, CPPI41 DMA completion EOI, suspend/resume clock/PHY transitions, and removal after active host/gadget traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/da8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/jz4740.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/jz4740.c

Purpose: implements the Ingenic JZ4740/JZ4770 MUSB gadget-only glue layer. It supplies FIFO layouts, PHY/role-switch setup, a gadget-safe interrupt wrapper, clock/resource management, and child `musb-hdrc` registration for Ingenic SoCs.

Important APIs, types, and functions: `struct jz4740_glue` tracks the child platform device, initialized MUSB pointer, `udc` clock, and `usb_role_switch`. `jz4740_musb_interrupt` handles DMA IRQs if Inventra DMA is enabled, reads Mentor interrupt registers, masks host-mode USB IRQ bits because the controller is gadget-only, and dispatches to `musb_interrupt`. `jz4740_musb_init` obtains generic PHY or legacy USB PHY, powers it, registers a role switch, marks dynamic FIFO mode, and installs the ISR. `jz4740_musb_exit` unregisters role switch and powers down PHY. Platform data instances describe JZ4740 and JZ4770 endpoint/FIFO topologies.

Control flow: probe matches OF data for the SoC, allocates a `musb-hdrc` child, obtains/enables the `udc` clock, sets a 32-bit DMA mask, adds inherited resources and SoC-specific platform data, and registers the child. MUSB core then calls the platform init hook, which configures PHY and role switch. The role-switch set callback reports USB role changes to the PHY notifier chain as `USB_EVENT_NONE`, `USB_EVENT_VBUS`, or `USB_EVENT_ID`.

State and persistence: no persistent state. Runtime state includes clock enablement, selected SoC FIFO config, role-switch object, PHY power state, and `glue->musb` back pointer. `musb->dyn_fifo = true` is forced because silicon lacks a usable ConfigData register.

Dependencies and integration points: depends on OF match data, clocks, generic PHY or `usb_phy`, USB role-switch framework, platform-device child registration, optional Inventra DMA, and MUSB core. Kconfig constrains this glue to gadget mode and selects role switch support.

Risks: host role is exposed only as a PHY notifier event even though the MUSB controller is configured gadget-only; role-switch users must not expect full host operation. The interrupt wrapper masks host bits to prevent undefined hardware state from reaching common core; removing that mask can cause false host transitions. Probe enables the clock before child registration and only disables it in error/remove paths, so child init failures must unwind correctly. PHY selection supports both generic and legacy paths, increasing probe-deferral combinations.

Test signals: compile JZ4740/JZ4770 variants with and without Inventra DMA, probe OF compatibles, verify clock enable/disable unwind, role-switch registration and user role changes, generic PHY and legacy PHY paths, gadget enumeration, reset/resume/suspend/SOF interrupt masking, dynamic FIFO setup for both FIFO tables, and remove after gadget unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/jz4740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/mediatek.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/mediatek.c

Purpose: implements the MediaTek MUSB platform glue layer. It configures clocks, PHY, role switching, MediaTek-specific interrupt clearing, endpoint bus-control offsets, data-toggle registers, FIFO layout, DMA interrupt masking, and child `musb-hdrc` registration.

Important APIs, types, and functions: `struct mtk_glue` stores parent device, MUSB pointer/child, generic USB PHY device, PHY, USB transceiver, current PHY mode, three clocks, current USB role, and role switch. Role helpers are `mtk_otg_switch_set`, `musb_usb_role_sx_set`, `musb_usb_role_sx_get`, `mtk_otg_switch_init`, and `mtk_otg_switch_exit`. Interrupt handling is split between `mtk_musb_interrupt`, which reads level-1 wrapper interrupt status/mask, and `generic_interrupt`, which W1C-clears Mentor interrupt registers and dispatches to `musb_interrupt`. Platform ops include MediaTek clearb/clearw, busctl offset, mode switching, toggle get/set, optional Inventra DMA init/exit, and init/exit hooks.

Control flow: probe populates child devices, obtains three clocks, builds platform data and mode from `dr_mode` or compile-time host/gadget role, obtains PHY, registers a generic USB PHY and xceiv, enables runtime PM, enables clocks, then registers a `musb-hdrc` child. Core init calls `mtk_musb_init`, which attaches PHY/xceiv, enables TX/RX toggle control registers, registers role switch for OTG mode, initializes/powers PHY, sets PHY mode, unmasks DMA interrupts if present, and enables wrapper L1 interrupts. Role-switch transitions write/clear DEVCTL SESSION, change OTG state, set host/device mode flags, power PHY on/off when entering/leaving `USB_ROLE_NONE`, and update `phy_set_mode`.

State and persistence: no persistent state. Runtime state includes `glue->role`, `glue->phy_mode`, clock/runtime-PM references, PHY power, wrapper interrupt masks, MediaTek toggle registers, and MUSB core state. `mtk_musb_exit` tears down role switch, powers off/exits PHY, disables clocks, and drops runtime PM.

Dependencies and integration points: depends on OF, platform devices, bulk clocks, generic PHY, legacy `usb_phy_generic`, USB role switch, optional Inventra DMA, and MUSB core APIs. The OF compatible is `mediatek,mtk-musb`.

Risks: `mtk_musb_exit` unconditionally calls `mtk_otg_switch_exit`, but the role switch is only registered in OTG mode; non-OTG configurations need coverage for NULL/invalid unregister behavior. Runtime PM and clock enablement are split between parent probe and child core exit, so failures after `pm_runtime_get_sync` must unwind symmetrically. MediaTek interrupt registers use W1C semantics through custom clear functions; default clear-by-read would be wrong. Reset in peripheral mode clears ep0 FADDR; missing that step can break re-enumeration. Toggle get/set code uses direction naming that maps MUSB host queue direction to TX/RX hardware registers and must be tested.

Test signals: build with host, gadget, OTG, and Inventra DMA combinations; probe with `dr_mode` host/peripheral/otg; verify three-clock enable failures; generic PHY and generic USB PHY registration; role-switch userspace transitions; PHY power off/on for `USB_ROLE_NONE`; L1 interrupt dispatch for TX/RX/common/DMA; W1C clear behavior; ep0 reset FADDR clearing; data toggle preservation in host transfers; and remove after runtime-PM suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/mpfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/mpfs.c

Purpose: implements the Microchip PolarFire SoC MUSB glue layer. It provides MPFS-specific FIFO configuration, VBUS/session control, OTG polling, interrupt acknowledgement, child `musb-hdrc` registration, clock handling, and optional Inventra DMA support.

Important APIs, types, and functions: `struct mpfs_glue` tracks parent device, child MUSB device, registered generic PHY, and clock. `mpfs_musb_mode_cfg` and `mpfs_musb_hdrc_config` describe dynamic FIFO layout, endpoint count, and RAM bits. Platform hooks are `mpfs_musb_init`, `mpfs_musb_exit`, `mpfs_musb_set_vbus`, optional `mpfs_musb_try_idle`, and optional Inventra DMA init/exit via `mpfs_ops`. `mpfs_musb_interrupt` reads/acknowledges Mentor USB/TX/RX interrupt registers and dispatches to `musb_interrupt`.

Control flow: probe allocates a `musb-hdrc` child, obtains/enables the parent clock, sets a 39-bit coherent DMA mask, creates platform data with MPFS config and `dr_mode`, registers a generic USB PHY, adds parent resources/data to the child, and registers it. Core init obtains the USB2 transceiver, sets up the OTG polling timer, forces dynamic FIFO mode, installs the ISR, and turns on VBUS through `musb_platform_set_vbus`. VBUS on sets active/default-A/A_WAIT_VRISE, asserts SESSION, and marks host mode; VBUS off clears active/default-A, moves to B_IDLE, clears SESSION, and marks device mode. The OTG timer polls DEVCTL to compensate for missing transceiver status-change IRQs.

State and persistence: no persistent storage. Runtime state includes clock enablement, generic PHY platform device, MUSB timer, DEVCTL/session bits, OTG state, endpoint FIFO configuration, and child platform-device state.

Dependencies and integration points: depends on OF, clocks, platform-device resources, DMA mask setup, `usb_phy_generic`, MUSB core, and optional Inventra DMA. It binds `microchip,mpfs-musb`.

Risks: `mpfs_remove` calls `usb_phy_generic_unregister(pdev)` instead of unregistering `glue->phy`, which looks like a type/ownership bug and should be verified. Error paths may call `usb_phy_generic_unregister(glue->phy)` even when `glue->phy` was not assigned due to earlier failures. The controller relies on polling for ID changes and forces VBUS on in init, so role behavior is sensitive to `dr_mode` and external VBUS driver property. Interrupt code manually acknowledges Mentor interrupt registers before calling the core; ordering changes can lose events. The 39-bit DMA mask must match actual interconnect/DMA support.

Test signals: compile with PolarFire Kconfig and optional Inventra DMA, probe `microchip,mpfs-musb` with host/peripheral/otg `dr_mode`, verify clock failure cleanup, generic PHY registration/unregistration, dynamic FIFO setup, VBUS on/off transitions, OTG polling from B_IDLE/A_WAIT states, interrupt acknowledgement and dispatch, DMA above 32-bit addresses if supported, and remove/unbind with leak/type-checking tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.c

Purpose: implements the common Mentor Inventra MUSB HDRC/MHDRC controller core. It abstracts register and FIFO access, initializes endpoint FIFO topology, manages host/gadget/OTG state transitions, dispatches interrupts, provides sysfs controls, integrates DMA backends, registers host/gadget roles, handles probe/remove, and saves/restores hardware context for system and runtime PM.

Important APIs, types, and functions: exported/common entry points include `musb_get_mode`, `musb_readb`, `musb_writeb`, `musb_clearb`, `musb_readw`, `musb_writew`, `musb_clearw`, `musb_readl`, `musb_writel`, `musb_read_fifo`, `musb_write_fifo`, `musb_set_host`, `musb_set_peripheral`, `musb_load_testpacket`, `musb_hnp_stop`, `musb_start`, `musb_stop`, `musb_interrupt`, `musb_dma_completion`, `musb_mailbox`, and `musb_queue_resume_work`. Internal subsystems include ULPI accessors, default MMIO/FIFO/toggle methods, global interrupt handlers, FIFO setup tables, endpoint discovery, PM runtime session checking, babble recovery, instance allocation, core initialization, and platform driver probe/remove.

Control flow: `musb_probe` maps resources and calls `musb_init_controller`. Initialization validates platform data, allocates `struct musb` and host resources, initializes locks and default IO functions, calls platform `init` so glue can adjust base registers/PHY/ISR, installs platform-specific IO/DMA/fifo/toggle operations, enables runtime PM, initializes the USB PHY and optional DMA controller, disables interrupts, initializes work items, calls `musb_core_init` to detect/configure endpoints, requests the IRQ, sets wakeup, configures external VBUS if requested, initializes B_IDLE/device mode, then sets up host, gadget, or both according to `port_mode` and calls platform `set_mode`. Debugfs is created after the controller is live.

Interrupt flow: platform-specific ISRs populate `musb->int_usb`, `int_tx`, and `int_rx`, then call `musb_interrupt` under `musb->lock`. The core reads DEVCTL, traces the event, handles global USB IRQs in Mentor-documented order through `musb_stage0_irq`, handles ep0 as host or gadget, then iterates TX and RX endpoint bits and dispatches to host or gadget endpoint handlers. Global handlers manage resume, session request, VBUS error retries, suspend/HNP, connect, disconnect, reset/babble, root-hub notifications, gadget callbacks, and OTG timers.

Endpoint and FIFO flow: `musb_core_init` reads ConfigData and hardware version, records dynamic FIFO, bulk split/combine, and high-bandwidth ISO capabilities, configures ep0, then either programs FIFO layout from platform/static tables or discovers hardware FIFO sizes. `fifo_setup` writes FIFO size/address registers and records per-endpoint maxpacket/shared/double-buffer state. Endpoint register addressing supports indexed and flat models plus platform overrides.

State and persistence: no on-disk persistence. Runtime state is concentrated in `struct musb`: locks, platform ops, saved register context, delayed work, timers, endpoint descriptors, host/gadget role state, DMA controller, MMIO base pointers, interrupt masks, OTG state, port status, endpoint mask/count, power/session flags, runtime-PM flags, gadget/HCD pointers, and debugfs root. PM save/restore copies core registers, per-endpoint CSR/FIFO/type/interval/function/hub registers, DEVCTL/session state, and dynamic FIFO registers.

Dependencies and integration points: integrates with platform glue through `struct musb_platform_ops`, USB host HCD code, USB gadget code, USB PHY/ULPI APIs, generic PHY via glue, DMA abstraction from `musb_dma.h`, tracepoints, debugfs, sysfs attributes (`mode`, `vbus`, `srp`), runtime PM, workqueues, timers, and platform bus. Platform glue is responsible for wrapper IRQ acknowledgement and resource-specific clocks/PHYs.

Risks: global function pointers for `musb_readb`/`writeb`/DMA factory are assigned per initialized controller, which is risky for heterogeneous multi-controller systems with different access methods. Interrupt ordering is intentional; reordering global/ep0/TX/RX handling can break Mentor FSM behavior. Dynamic FIFO setup can overrun RAM or omit a usable bulk endpoint. Runtime-PM session tracking relies on delayed DEVCTL rechecks for known quirks and must not race with IRQ work flushing. `musb_queue_resume_work` refuses/queues work based on `is_runtime_suspended`; callers must hold the documented locks and PM references. Babble recovery drops session, reconfigures endpoints, and restarts, so active transfers can be disrupted. Probe error paths span host, gadget, PHY, DMA, IRQ, PM, and platform ops and need coverage.

Test signals: build host-only, gadget-only, dual-role, PIO-only, and each DMA backend. Runtime tests should cover probe/remove failure injection at platform init, PHY init, DMA create, IRQ request, host/gadget setup; endpoint FIFO modes 0-5 and platform FIFO tables; indexed and flat register maps; sysfs mode/vbus/srp; ULPI reads/writes; host connect/disconnect/reset/suspend/resume; gadget enumeration/control transfers; HNP timers; VBUS error retry exhaustion; babble recovery with platform recover success/failure; runtime suspend/resume with queued resume work; system suspend/resume preserving endpoint registers; and multiple controller instances where platform IO methods differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.h

Purpose: defines the common data model, platform operation contract, state helpers, endpoint structures, PM context structures, and core function prototypes for the MUSB HDRC driver family.

Important APIs, types, and symbols: role helpers include `is_peripheral_active`, `is_host_active`, `MUSB_HST_MODE`, `MUSB_DEV_MODE`, `MUSB_MODE`, `musb_set_state`, `musb_get_state`, and `musb_otg_state_string`. Ep0 state enums cover host and gadget control-transfer phases. `struct musb_platform_ops` is the glue contract for quirks, init/exit, enable/disable, endpoint/fifo/busctl offsets, MMIO methods, FIFO methods, data toggle methods, DMA init/exit, mode changes, idle/recover/VBUS hooks, root-reset hooks, PHY callback, and RX interrupt clearing. Core structures include `struct musb_hw_ep`, `struct musb_csr_regs`, `struct musb_context_registers`, and the central `struct musb`.

Control flow represented by the header: platform glue fills `musb_hdrc_platform_data` with `musb_platform_ops`; `musb_core.c` uses the inline wrappers to call optional hooks safely. Endpoint handlers use `next_in_request`/`next_out_request` to inspect gadget queues. PM code uses `musb_context_registers` to save/restore global and per-endpoint hardware state. Host/gadget code consumes the same `struct musb` fields for queues, endpoint state, port status, HCD/gadget references, and role flags.

State and persistence: no persistent storage. This header defines all major runtime state fields: locks, IO ops, platform ops, saved register context, work items, endpoint array, host scheduling lists, timers, DMA controller, MMIO bases, interrupt latches, PHY pointers, OTG state, IRQ/wakeup state, endpoint masks, power/session flags, runtime-PM flags, role mode, gadget state, HCD pointer, config pointer, old xceiver state, and optional debugfs root.

Dependencies and integration points: includes Linux USB, gadget, HCD, OTG, PHY, timer, workqueue, interrupt, and device headers plus local debug, DMA, IO, gadget, host, and register headers. It is included by core, platform glue, host/gadget endpoint code, DMA backends, and debugfs support.

Risks: `struct musb_platform_ops` is broad and optional-heavy; new glue must fill enough hooks for its register semantics or the core falls back to defaults that may be wrong. The central `struct musb` is shared by host, gadget, DMA, PM, IRQ, and glue code, so field ownership must be clear when changing locking or state transitions. The inline state helpers write either `xceiv->otg->state` or fallback `musb->otg_state`, so callers must handle missing xceiv consistently. Header inclusion pulls in both host and gadget headers, making role-specific build guards important.

Test signals: compile all MUSB role combinations and platform glue users; run sparse/lockdep around shared `struct musb` fields; validate platform ops defaults against each glue; exercise PM context save/restore; verify endpoint structure initialization for all `MUSB_C_NUM_EPS`; and check that host/gadget-only builds do not expose missing prototypes or role-specific fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_cppi41.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_cppi41.c

Purpose: implements the CPPI 4.1 DMAengine backend for MUSB platforms such as TI DSPS/AM335x and DA8xx. It maps MUSB's generic `dma_controller` interface to DMAengine channels, configures CPPI endpoint modes and auto-request registers, tracks transfer progress, works around TX FIFO early-completion and RX data-toggle errata, and provides channel create/destroy/allocation/program/abort operations.

Important APIs, types, and functions: `struct cppi41_dma_controller` wraps `struct dma_controller` with RX/TX channel arrays, early-TX hrtimer/list, cached RX/TX mode and auto-request registers, teardown/autoreq register offsets, mode setter callback, and channel count. Per-channel state is `struct cppi41_dma_channel` from `cppi_dma.h`. Exported entry points are `cppi41_dma_controller_create` and `cppi41_dma_controller_destroy`. Generic DMA methods are `cppi41_dma_channel_allocate`, `cppi41_dma_channel_release`, `cppi41_dma_channel_program`, `cppi41_dma_channel_abort`, and `cppi41_is_compatible`.

Control flow: controller creation requires a parent OF node with `dma-names`. It allocates controller/channel arrays, initializes the early-TX hrtimer, selects DA8xx or generic register layout/channel count from MUSB quirks, requests each named DMAengine channel, and initializes generic channel fields. Channel allocation chooses TX/RX by endpoint number and direction, rejects missing or already allocated channels, and binds the endpoint. Programming sets status busy, applies high-bandwidth multiplier in host mode, records buffer/length/packet/ZLP state, configures endpoint DMA/RNDIS/autoreq mode, prepares a DMAengine slave descriptor, installs `cppi41_dma_callback`, submits, traces, saves RX toggle, and issues pending DMA.

Completion flow: `cppi41_dma_callback` acknowledges platform DMA callback if present, ignores aborted completions, takes `musb->lock`, reads DMA residue, updates transferred count, fixes RX toggle if needed, determines whether transfer is done or needs another packet-sized iteration, and handles TX FIFO early-completion. High-speed TX briefly spins for FIFO empty; otherwise it queues the channel on `early_tx_list` and starts an hrtimer. `cppi41_trans_done` marks the generic channel free, records actual length and `rx_packet_done`, optionally sends a TX ZLP in PIO mode, traces, and calls `musb_dma_completion`, or programs the next chunk and for RX sets `REQPKT`.

State and persistence: no persistent state. Runtime state includes DMAengine cookies/channels, cached endpoint mode/autoreq register images, per-channel programmed/total/transferred lengths, saved USB data toggle, TX FIFO recheck list, hrtimer, DMA status, and MUSB endpoint CSR bits. Destroy cancels the timer, releases DMAengine channels, frees arrays, and frees the controller.

Dependencies and integration points: depends on DMAengine, OF `dma-names`, MUSB core registers and host/gadget callbacks, `cppi_dma.h`, tracepoints, DA8xx/DSPS wrapper callbacks, and MUSB quirk flags `MUSB_DA8XX`/`MUSB_DMA_CPPI41`. It is selected by `CONFIG_USB_TI_CPPI41_DMA` and invoked via platform ops from DA8xx/DSPS.

Risks: transfer iteration intentionally limits RX/device compatibility because AM335x Advisory 1.0.13 has no device-RX workaround; compatibility decisions must be honored by callers. Early-TX hrtimer/list manipulation is protected by `musb->lock`; missing list removal on abort would double-complete. Abort performs platform-specific teardown, delays up to 250 ms for DA8xx, flushes FIFOs, and loops on `dmaengine_terminate_all` returning `-EAGAIN`, so it can stall teardown. Mode/autoreq register caches must match hardware after suspend/resume or wrapper reset. `cppi41_dma_controller_create` returns NULL for most failures but `ERR_PTR(-EPROBE_DEFER)` for deferred probe, so caller handling must distinguish both.

Test signals: probe with valid/invalid/missing `dma-names`, allocate/release all TX/RX channels, program bulk TX/RX in host and gadget modes, test short packets, multi-packet transfers, high-bandwidth multiplier, TX ZLP, RX data-toggle erratum recovery, early-TX FIFO-empty timer path at full speed, abort during active TX/RX/iso, DA8xx register layout and teardown delay, DSPS DMA callback acknowledgement, suspend/resume with cached mode registers, and repeated module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_cppi41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debug.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debug.h

Purpose: provides basic logging macros and debugfs function declarations for the MUSB core and related files.

Important APIs, types, and symbols: `yprintk` wraps `printk` with function and line number. `WARNING`, `INFO`, and `ERR` specialize it for kernel warning/info/error facilities. `musb_dbg(struct musb *musb, const char *fmt, ...)` is declared for MUSB-specific debug logging. When `CONFIG_DEBUG_FS` is enabled, `musb_init_debugfs` and `musb_exit_debugfs` are declared; otherwise inline no-op stubs are provided.

Control flow: source files call the macros or `musb_dbg` for diagnostics. Core initialization and removal can call `musb_init_debugfs`/`musb_exit_debugfs` unconditionally because this header supplies no-op implementations when debugfs is disabled.

State and persistence: no runtime state is stored here. Debugfs state, when enabled, is owned by `musb_debugfs.c` and referenced through `struct musb`.

Dependencies and integration points: included by `musb_core.h` before the full `struct musb` definition, relying on forward declarations from the core header. Integrates with kernel printk and optional debugfs support.

Risks: macros use raw `printk` instead of device-scoped logging, so output context is limited to function/line. Format strings must be trusted kernel strings. The no-op debugfs stubs make debugfs absence silent, so tests must explicitly enable debugfs to validate observability.

Test signals: compile with `CONFIG_DEBUG_FS=y` and `n`, verify unconditional calls link in both cases, and trigger warning/info/error paths to ensure format strings and function/line output are sane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debugfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debugfs.c

Purpose: implements debugfs observability and manual controls for MUSB controllers. It exposes register dumps, USB test mode selection, and host soft-connect control under a per-controller debugfs directory.

Important APIs, types, and functions: `struct musb_register_map` and `musb_regmap` list core and DMA register names, offsets, and widths. `musb_regdump_show` reads and prints the register map under a runtime-PM reference. Test mode support is implemented by `musb_test_mode_show`, `musb_test_mode_open`, and `musb_test_mode_write`; it writes `MUSB_TESTMODE` and loads the USB test packet for "test packet". Soft-connect support is `musb_softconnect_show`, `musb_softconnect_open`, and `musb_softconnect_write`; it reads/updates DEVCTL SESSION and can call `musb_root_disconnect`. `musb_init_debugfs` creates files `regdump`, `testmode`, and `softconnect`; `musb_exit_debugfs` removes the directory tree.

Control flow: during core init, `musb_init_debugfs` creates a directory named after the controller under `usb_debug_root`. Reading `regdump` resumes the device, snapshots all listed registers with width-appropriate accessors, and autosuspends. Writing `testmode` copies a short user string, refuses changes if a test mode is already active, maps recognized strings to test bits, optionally writes the test packet to ep0 FIFO, then writes TESTMODE. `softconnect` only reports meaningful state for host A states and writing `0` or `1` clears or sets DEVCTL SESSION for selected host states.

State and persistence: debugfs files are runtime-only and disappear on remove/unmount. Writes affect hardware registers, `musb->context.devctl`, and root-hub connection state; there is no disk persistence.

Dependencies and integration points: depends on debugfs, seq_file, uaccess, MUSB register accessors, runtime PM, USB debug root, and host/gadget helper functions. It integrates with USB electrical compliance testing and manual host connection simulation.

Risks: debugfs writes directly affect controller state and can disrupt active transfers. `testmode` accepts unrecognized strings by leaving `test` at its previous value and still writing it, so invalid input may be a silent no-op. Register dump offsets include generic DMA registers that may not exist on all wrappers. Runtime-PM get return values are not checked in these debug paths. Softconnect logic is host-state-specific and will ignore writes in most other states.

Test signals: build with debugfs enabled, read `regdump` during idle and active transfers, write every supported test mode after USB reset, verify "test packet" loads ep0 FIFO, attempt second testmode write and invalid strings, exercise `softconnect` in A_HOST and A_WAIT_BCON, and remove the device while debugfs files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dma.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dma.h

Purpose: defines the generic DMA abstraction used by the MUSB core and platform-specific DMA backends. It lets host/gadget endpoint code interact with different DMA engines through common channel/controller operations while preserving PIO-only fallback builds.

Important APIs, types, and symbols: register offsets define the Inventra HSDMA register block. `DMA_ADDR_INVALID` marks invalid DMA addresses. Capability macros include `is_dma_capable`, `musb_dma_ux500`, `musb_dma_cppi41`, `tusb_dma_omap`, `musb_dma_inventra`, and `is_cppi_enabled`. `enum dma_channel_status` defines unknown/free/busy/bus-abort/core-abort states. `struct dma_channel` tracks backend-private data, max length, actual length, status, desired mode, and RX packet completion. `struct dma_controller` provides channel allocation/release/program/abort/compatibility and optional platform completion callback.

Control flow: endpoint code asks a `dma_controller` for a channel tied to a hardware endpoint and direction, programs it with maxpacket, mode, DMA address, and length, observes completion through backend interrupts/callbacks, and calls `musb_dma_completion` to resume host/gadget endpoint state. Abort/release are used during dequeue, endpoint disable, teardown, and error recovery. In `CONFIG_MUSB_PIO_ONLY`, controller create/destroy stubs compile out DMA.

State and persistence: no persistent state. Runtime state lives in backend-defined `private_data`, status fields, actual length, mode, and controller callbacks. The MUSB core holds the selected controller pointer in `struct musb`.

Dependencies and integration points: forward-declares `struct musb_hw_ep` and integrates with MUSB core, host/gadget endpoint code, and backend implementations for Inventra HSDMA, TUSB OMAP DMA, CPPI41, and UX500. Platform glue installs the desired `dma_init`/`dma_exit` hooks through `musb_platform_ops`.

Risks: DMA status is protected by the overall controller spinlock by convention; backend code must follow that locking or endpoint code can race status changes. `private_data` is a generic `void *` and the comment notes it ideally should be more specific. PIO-only stubs return NULL, so callers must handle no DMA path cleanly. Backend `is_compatible` decisions are critical for hardware errata such as CPPI41 RX constraints. Global DMA factory pointers in `musb_core.c` mean heterogeneous platform combinations need scrutiny.

Test signals: compile PIO-only and all DMA backend configurations, run endpoint transfers with DMA enabled/disabled via module parameter, exercise channel allocation exhaustion, incompatible transfer fallback, abort on active transfers, bus/core abort reporting, short RX packet handling, and `musb_dma_completion` dispatch in host and gadget roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dsps.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dsps.c

Purpose: implements the TI DSPS MUSB wrapper glue layer, used by AM33xx/DM816-style SoCs. It adapts wrapper register offsets/bit layouts, interrupt masking/dispatch, OTG polling, optional VBUS IRQs, PHY control, CPPI41 DMA callbacks, debugfs register dumps, babble recovery, special FIFO access, child `musb-hdrc` registration, and PM context save/restore.

Important APIs, types, and functions: `struct dsps_musb_wrapper` describes wrapper register offsets and bit positions. `struct dsps_context` saves wrapper registers across suspend. `struct dsps_glue` holds parent device, child MUSB device, wrapper descriptor, optional VBUS IRQ, timer state, babble-control flag, USBSS base, saved context, and debugfs objects. Platform ops `dsps_ops` provide init/exit, enable/disable, optional CPPI41 DMA init/exit, set_mode, recover, and RX interrupt clearing. Key functions include `dsps_musb_enable`, `dsps_musb_disable`, `dsps_check_status`, `otg_timer`, `dsps_interrupt`, `dsps_musb_init`, `dsps_musb_set_mode`, `dsps_musb_recover`, `dsps_create_musb_pdev`, `dsps_probe`, `dsps_suspend`, and `dsps_resume`.

Control flow: probe rejects accidental binding as the child `musb-hdrc`, finds wrapper data from OF, optionally installs 32-bit FIFO reads for DM816, maps USBSS, enables runtime PM, creates a child `musb-hdrc` device with `mc` memory/IRQ resources and platform data derived from DT properties, and optionally requests a threaded VBUS IRQ in peripheral mode. MUSB core init maps the wrapper control resource, obtains PHY/xceiv, checks revision, powers PHY, sets up OTG timer, resets the wrapper, installs ISR, clears OTG disable, detects babble-control support, starts polling, and initializes DSPS debugfs.

Interrupt and role flow: `dsps_musb_enable` writes wrapper endpoint/core interrupt enable registers and starts polling in B_IDLE. `dsps_interrupt` reads endpoint and core wrapper status, maps bits into MUSB interrupt fields, acknowledges wrapper status, handles DRVVBUS/VBUS error state transitions, dispatches to `musb_interrupt`, and restarts polling for B_IDLE/A_WAIT_BCON. `dsps_check_status`, queued through `musb_queue_resume_work` from the timer, polls DEVCTL to infer ID/VBUS state when no VBUS IRQ exists and manipulates SESSION based on role mode.

State and persistence: no disk persistence. Runtime state includes wrapper registers, USBSS IRQ state, MUSB core state, PHY power, timers, optional VBUS IRQ, debugfs regset, software babble flag, and saved wrapper context. Suspend saves wrapper control/interrupt/PHY/mode/TX/RX mode registers, disables USBSS DMA completion IRQ if used, and deletes timers; resume restores them and restarts polling when needed.

Dependencies and integration points: depends on OF resources/properties, platform devices, runtime PM, generic USB PHY, optional generic PHY, debugfs, CPPI41 DMA, MUSB core, USBSS parent mapping, and TI wrapper DT compatibles `ti,musb-am33xx` and `ti,musb-dm816`.

Risks: wrapper bitfields are data-driven; incorrect `dsps_musb_wrapper` values break interrupt and mode handling. `usbss_base = of_iomap(pdev->dev.parent->of_node, 0)` assumes a usable parent OF node/resource. Optional VBUS IRQ changes polling behavior, so both modes must be tested. `dsps_ops` is static and modified at probe for DM816 `read_fifo`, which is risky if multiple DSPS variants with different FIFO requirements coexist. Babble recovery can return `-EPIPE` when software control clears noise without session restart; core behavior depends on that return value. PM save/restore crosses wrapper and child MUSB runtime PM and can race timers/queued resume work if ordering regresses.

Test signals: build AM33xx and DM816 with/without CPPI41 DMA and PM, probe DT resources including `mentor,num-eps`, `mentor,ram-bits`, `mentor,power`, `mentor,multipoint`, `maximum-speed`, and optional VBUS IRQ; validate wrapper interrupt masks and DRVVBUS handling; host/peripheral/OTG mode forcing; timer polling without VBUS IRQ; CPPI41 USBSS completion IRQ enable/ack/suspend/resume; DM816 32-bit FIFO reads; debugfs wrapper regdump; babble noise and real babble recovery; system suspend/resume with active and idle sessions; and remove/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dsps.c -->
