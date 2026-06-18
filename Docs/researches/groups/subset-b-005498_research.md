# subset-b-005498 Research

Grouped research for the listed USB gadget UDC files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/epn.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/epn.c

## Purpose
Implements the Aspeed vHub generic endpoint pool, meaning all non-control endpoints assigned to the virtual downstream devices behind the vHub. It turns Linux gadget `usb_ep_ops` calls into Aspeed endpoint register programming, DMA staging, descriptor-ring operation for IN endpoints, request completion, halt/wedge handling, and endpoint allocation/disposal.

## Important APIs, Types, And Functions
The exported entry points are `ast_vhub_epn_ack_irq`, `ast_vhub_update_epn_stall`, and `ast_vhub_alloc_epn`. The endpoint operations table `ast_vhub_epn_ops` wires the file into the gadget core through enable, disable, dispose, queue, dequeue, set halt, set wedge, and request allocation/free helpers supplied by `core.c`.

Single-stage transfer helpers are `ast_vhub_epn_kick` and `ast_vhub_epn_handle_ack`. Descriptor-mode helpers are `ast_vhub_count_free_descs`, `ast_vhub_epn_kick_desc`, and `ast_vhub_epn_handle_ack_desc`. `ast_vhub_stop_active_req` handles DMA stop/reset when disabling or dequeuing active work. Request state is stored in `struct ast_vhub_req`: `actual`, `act_count`, `last_desc`, and `active`. Endpoint state is stored in the `epn` union member of `struct ast_vhub_ep`: hardware register base, global endpoint index, descriptor pointers, ring pointers, max chunk size, DMA config, direction/type flags, halt state, and mode flags.

## Control Flow
`ast_vhub_alloc_epn` finds a free global endpoint from `vhub->epns`, binds it to a downstream device endpoint number, allocates one coherent block containing a max-packet bounce buffer plus a 256-entry descriptor ring, installs `usb_ep_ops`, and links the endpoint into the gadget endpoint list. `ast_vhub_epn_enable` validates the USB endpoint descriptor, derives direction, type, maxpacket, descriptor-mode eligibility, chunk size, and config bits, resets endpoint DMA, writes `AST_VHUB_EP_CONFIG`, initializes descriptor or single-stage DMA mode, clears data toggle, and enables ACK interrupts for the global endpoint.

`ast_vhub_epn_queue` validates the request and endpoint/device state, maps request DMA when aligned and safe or when descriptor mode is used, otherwise leaves `req->dma` zero so the coherent bounce buffer is used. If the endpoint queue was empty, it immediately kicks either single-stage DMA or descriptor-ring DMA. ACK interrupts enter `ast_vhub_epn_ack_irq`; single-stage mode reads transferred length from `AST_VHUB_EP_DESC_STATUS`, copies OUT data from the bounce buffer if needed, detects short packets, completes finished requests, and kicks the next chunk. Descriptor mode reads a stable hardware read pointer, walks completed descriptors from `d_last`, sums lengths into `req.actual`, completes when `last_desc` is reached, and may add more descriptors.

Disable and dequeue paths stop hardware DMA, optionally restart the endpoint after removing only one request, nuke pending requests, disable endpoint config, and clear ACK interrupt state. Halt/wedge updates set `VHUB_EP_CFG_STALL_CTRL`, reject unsupported ISO stalls, and reject halting busy IN endpoints with `-EAGAIN`.

## State And Persistence Behavior
All state is in-memory driver state plus MMIO registers and coherent DMA memory. There is no filesystem persistence. Persistent while the controller is bound are global endpoint ownership (`ep->dev`), per-device endpoint slots (`dev->epns`), queue membership, descriptor ring pointers, DMA config, stall/wedge flags, and request progress. The driver drops and reacquires `vhub->lock` around gadget completion callbacks via `ast_vhub_done`, so queue state can change during completion and is rechecked after callbacks.

## Dependencies And Integration Points
Depends on the Linux USB gadget API, DMA mapping helpers, coherent DMA allocation, Aspeed vHub register definitions and shared structures in `vhub.h`, and shared request completion/allocation helpers from `core.c`. It is driven by ACK interrupts dispatched from the vHub core interrupt handler. It integrates with `dev.c` because each downstream virtual device owns a set of allocated generic endpoints, and with `hub.c` because device reset/suspend/resume controls when endpoint traffic is valid.

## Risks
Descriptor-ring accounting is delicate: the ring intentionally leaves one descriptor empty to distinguish full from empty, assumes only the head request is described at a time, and relies on `last_desc` matching the hardware read pointer. DMA safety depends on the alignment/multiple-of-packet rules for non-DMA bounce-buffer fallback, especially OUT endpoints that could overrun if directly mapped with an undersized tail packet. The Aspeed memory-order workaround in `vhub_dma_workaround` is essential before MMIO kicks; removing it can make hardware read stale descriptors or buffers. Completion callbacks run with the lock dropped, so every path after `ast_vhub_done` must tolerate queue mutation. Timeout in `ast_vhub_stop_active_req` indicates hardware may continue using DMA state after software thinks it stopped.

## Test Signals
Useful signals are enumeration of multiple downstream gadget functions, bulk/interrupt/iso IN and OUT traffic, large IN transfers that require descriptor mode, unaligned and short OUT requests that force bounce-buffer behavior, endpoint halt and wedge tests, dequeue of active transfers, disconnect/reset while transfers are pending, and dynamic allocation/exhaustion of the global endpoint pool. Kernel warnings from `CHECK`, DMA timeout messages, unexpected read-pointer mismatches, transfer byte count mismatches, or request completion after disable are high-value regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/epn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/hub.c

## Purpose
Emulates the upstream-facing USB 2.0 hub for the Aspeed vHub controller. It supplies the root hub descriptors and string descriptors, handles standard and hub-class control requests on the vHub EP0, maintains per-port status/change bits, drives the hardware status-change interrupt endpoint, and propagates hub reset/suspend/resume/wakeup events to the virtual downstream gadget devices.

## Important APIs, Types, And Functions
The public functions are `ast_vhub_init_hub`, `ast_vhub_std_hub_request`, `ast_vhub_class_hub_request`, `ast_vhub_device_connect`, `ast_vhub_hub_suspend`, `ast_vhub_hub_resume`, `ast_vhub_hub_reset`, and `ast_vhub_hub_wake_all`. Descriptor constants include `ast_vhub_dev_desc`, `ast_vhub_qual_desc`, `ast_vhub_conf_desc`, `ast_vhub_hub_desc`, and default English strings. Hub request helpers include descriptor/string responders, `ast_vhub_hub_dev_status`, `ast_vhub_hub_ep_status`, feature handlers, and port status handlers.

Port state lives in `struct ast_vhub_port` inside `struct ast_vhub`: `status`, `change`, and the attached `struct ast_vhub_dev`. vHub-wide state includes current upstream speed, suspend flag, remote wakeup enable, EP1 stall state, descriptor copies, and the list of language-specific string containers.

## Control Flow
`ast_vhub_init_hub` initializes speed to unknown, initializes wake work, and calls `ast_vhub_init_desc`. Descriptor initialization copies defaults, applies device-tree overrides for vendor/product/revision, optionally forces USB 1.1 descriptor values, sets hub port count, and loads either default strings or `vhub-strings` children with validated USB language IDs.

During early control traffic, `ast_vhub_std_hub_request` lazily samples `AST_VHUB_USBSTS` to determine full/high speed, then handles SET_ADDRESS, GET_STATUS, device/interface/endpoint features, configuration, descriptors, and interface requests. Descriptor responses are copied to the EP0 buffer before sending, allowing in-place type patching for other-speed configuration. `ast_vhub_class_hub_request` handles hub-class status/descriptor requests, port feature set/clear, and TT no-op requests. `ast_vhub_change_port_stat` updates USB port status, derives USB change bits from selected status transitions, suppresses enable-change on enable as required by host behavior, and mirrors changes into `AST_VHUB_EP1_STS_CHG`.

Device connect/disconnect changes CONNECTION and ENABLE state and can issue host remote wake. Port reset disables/suspends the port, calls `ast_vhub_dev_reset`, selects a speed compatible with the vHub upstream speed and gadget driver max speed, then sets ENABLE plus speed status. Suspend and resume forward bus state to every port that is not explicitly port-suspended. `ast_vhub_hub_wake_all` schedules `wake_work` so a downstream device wakeup can clear suspended port bits and signal remote wake without recursive call chains.

## State And Persistence Behavior
There is no disk persistence. Runtime state is the emulated USB hub state: descriptor copies, string container list allocated with devm memory, per-port status/change bits, remote wakeup enable, EP1 stall flag, upstream speed, and bus suspend flag. Port changes persist until the host clears the corresponding C_* feature. Bus reset clears wakeup enable, speed, non-connection port state, EP1 status-change hardware, and vHub address/config registers.

## Dependencies And Integration Points
Depends on USB descriptor and hub class definitions, device tree property parsing, `usb_gadget_get_string`, `usb_validate_langid`, `usb/ch11.h` hub feature constants, and shared vHub endpoint helpers from `ep0.c`. It integrates with `dev.c` through `ast_vhub_dev_suspend`, `ast_vhub_dev_resume`, and `ast_vhub_dev_reset`; with hardware through `AST_VHUB_CONF`, `AST_VHUB_EP1_CTRL`, `AST_VHUB_EP1_STS_CHG`, and `AST_VHUB_CTRL`; and with host enumeration through the hub interrupt endpoint.

## Risks
Hub behavior is host-sensitive. Incorrect change-bit semantics can break enumeration or upset OS-specific hub drivers; the file already contains a MacOS-oriented suppression of enable-change on enable. Port reset is effectively immediate rather than delayed, which may hide timing issues. Device-tree string parsing relies on a small fixed string ID set and EP0 buffer-size limits. Remote wake state is split between hub feature state and hardware wake signaling, so wake tests must cover both host-enabled and host-disabled cases. USB 1.1 forced mode modifies descriptors but shares much of the same control path as USB 2.0 mode.

## Test Signals
Important signals are host enumeration of the vHub itself, descriptor reads in full-speed and high-speed modes, custom device-tree VID/PID/revision/string descriptors, language descriptor reads, port connection-change and reset flows for each virtual port, suspend/resume propagation to downstream gadgets, remote wake from a suspended port, EP1 halt clear/set behavior, and repeated bus resets. `lsusb -v`, hub class request traces, dmesg debug logs, and gadget driver suspend/resume/reset callbacks provide practical validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/vhub.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/vhub.h

## Purpose
Defines the Aspeed vHub driver's hardware register map, bit fields, shared data structures, debug macros, DMA ordering workaround, and cross-file function prototypes. It is the shared contract among the vHub core, hub emulation, downstream device handling, EP0 handling, and generic endpoint handling.

## Important APIs, Types, And Functions
The header defines root vHub registers (`AST_VHUB_CTRL`, `AST_VHUB_CONF`, interrupt registers, EP0/EP1 registers, setup buffers), per-device registers (`AST_VHUB_DEV_*`), per-endpoint registers (`AST_VHUB_EP_*`), software reset bits, interrupt masks, EP config fields, DMA status fields, and descriptor word fields. Constants encode the legacy defaults of 15 generic endpoints, 5 ports, 64-byte EP0, 1024-byte EPn, and 256 descriptors.

Core types are `struct ast_vhub_desc`, `struct ast_vhub_req`, `enum ep0_state`, `struct ast_vhub_ep`, `struct ast_vhub_dev`, `struct ast_vhub_port`, `struct ast_vhub_full_cdesc`, and `struct ast_vhub`. The `to_ast_req`, `to_ast_ep`, and `to_ast_dev` helpers bridge Linux gadget objects back to driver-private objects. `enum std_req_rc` standardizes internal control-request handler results: stall, complete, data, or pass-to-driver.

The inline `vhub_dma_workaround` is a hardware-specific memory ordering primitive. It issues a barrier and dummy raw read from memory before MMIO writes that cause USB DMA, avoiding stale descriptor/buffer reads on Aspeed bus arbitration.

## Control Flow
The header does not run control flow by itself, but it defines the call graph between compilation units. `core.c` supplies request completion, nuking, request allocation, and hardware init. `ep0.c` supplies setup/ACK handling and control replies. `hub.c` supplies vHub hub request handling and bus/port state changes. `dev.c` supplies virtual downstream gadget lifecycle and standard device requests. `epn.c` supplies non-control endpoint ACK handling, stall updates, and endpoint allocation. Shared structures allow all these files to operate under a single `struct ast_vhub` lock and hardware register mapping.

## State And Persistence Behavior
The state model is entirely runtime. `struct ast_vhub` owns the platform device, MMIO base, IRQ, lock, clock/reset, EP0 coherent buffers, hub EP0, port array, endpoint pool, bus state, and descriptor copies. `struct ast_vhub_dev` represents a downstream virtual gadget with gadget-core state, driver pointer, port device, EP0, and endpoint pointer table. `struct ast_vhub_ep` represents either EP0 or generic EPn via a union, with request queues and DMA resources. Nothing here persists across driver unbind or reboot except hardware state initialized elsewhere.

## Dependencies And Integration Points
Includes USB core and hub chapter definitions (`linux/usb.h`, `linux/usb/ch11.h`) and assumes Linux gadget types are visible through implementation files. The register definitions map directly to Aspeed vHub hardware and are consumed by all vHub source files. Debug macros integrate with `CONFIG_USB_GADGET_VERBOSE` and `CONFIG_USB_GADGET_DEBUG`.

## Risks
This header is a high-blast-radius contract: changing bit definitions, structure layout expectations, or helper semantics affects every vHub component. The comment that EP0 device control bits must match vHub EP0 control bits is important for shared EP0 code. `VHUB_EP_TOGGLE_SET_EPNUM` and endpoint numbering must match hardware global endpoint indices, not just USB endpoint addresses. The DMA workaround is easy to mistake for an unnecessary read but documents a confirmed hardware race; bypassing it can break otherwise correct transfer code. Legacy constants are kept for AST2400/AST2500 compatibility, while newer revisions may use device tree sizing, so code should prefer runtime `max_ports` and `max_epns` where available.

## Test Signals
Header changes should be validated by building all Aspeed vHub objects, probing on supported SoCs, enumerating the hub with multiple downstream gadgets, exercising EP0 control requests and EPn DMA, and checking suspend/resume/reset. Compile-time failures in any vHub file, descriptor size build assertions, missing debug macro fields, or DMA data corruption after register/structure edits are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/vhub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed_udc.c

## Purpose
Implements the standalone Aspeed AST2600 USB device controller driver, separate from the multi-device vHub driver. It exposes one control endpoint plus four programmable endpoints to the Linux USB gadget framework, handles EP0 setup/status/data stages, programs endpoint DMA in single-stage or descriptor mode, dispatches controller interrupts, and binds the controller as an OF platform driver compatible with `aspeed,ast2600-udc`.

## Important APIs, Types, And Functions
Private state types are `struct ast_udc_request`, `struct ast_dma_desc`, `struct ast_udc_ep`, and `struct ast_udc_dev`. The gadget endpoint ops are implemented by `ast_udc_ep_enable`, `ast_udc_ep_disable`, request allocation/free, `ast_udc_ep_queue`, `ast_udc_ep_dequeue`, and `ast_udc_ep_set_halt`. Gadget ops are `ast_udc_gadget_getframe`, `ast_udc_wakeup`, `ast_udc_pullup`, `ast_udc_start`, and `ast_udc_stop`.

Transfer helpers include `ast_udc_done`, `ast_udc_nuke`, `ast_dma_descriptor_setup`, `ast_udc_epn_kick`, `ast_udc_epn_kick_desc`, `ast_udc_ep0_queue`, `ast_udc_ep0_in`, `ast_udc_ep0_out`, `ast_udc_epn_handle`, and `ast_udc_epn_handle_desc`. Setup handling is centralized in `ast_udc_ep0_handle_setup`, with `ast_udc_getstatus` and `ast_udc_ep0_data_tx` for simple standard replies. Platform lifecycle is handled by `ast_udc_probe`, `ast_udc_remove`, `ast_udc_init_ep`, `ast_udc_init_dev`, and `ast_udc_init_hw`.

## Control Flow
Probe allocates the device structure, maps registers, enables the clock, detects whether full-speed-only mode is requested from maximum speed, allocates one coherent DMA region for EP0 and all EPn buffers/descriptors, initializes endpoint objects, initializes hardware, requests the IRQ, and registers the gadget UDC. Hardware init enables PHY clock/reset, sets long descriptor mode for 256 descriptors, masks/acks interrupts, enables bus/EP0/EP-pool ACK interrupts, and clears EP0 control.

When a gadget driver starts, `ast_udc_start` records the driver and marks endpoints active. Pullup toggles `USB_UPSTREAM_EN`. Endpoint enable derives endpoint number, direction, type, maxpacket, descriptor-mode eligibility for IN endpoints, programs DMA mode and endpoint config, clears data toggle, and leaves the endpoint ready. Queueing maps the request for DMA, initializes progress, queues it, and kicks immediately if idle. EP0 queues write the EP0 data buffer address and set TX/RX ready bits; EPn queues either write a single DMA address/length or populate descriptors and update the hardware write pointer.

The ISR acknowledges `AST_UDC_ISR`, handles bus reset/suspend/resume by updating gadget state and invoking driver callbacks outside the lock, advances EP0 on IN/OUT ACKs, parses setup packets, and handles EP-pool ACKs by reading `AST_UDC_EP_ACK_ISR` and dispatching each active endpoint to single-stage or descriptor completion.

## State And Persistence Behavior
State is runtime-only: request queues, mapped DMA addresses, saved descriptor write pointer, endpoint stopped/dir/desc-mode flags, current gadget driver, `suspended_from`, `is_control_tx`, wakeup enable, and coherent descriptor memory. Hardware state lives in controller registers and is reset during probe/remove/stop. There is no persistent storage. Completion callbacks run with `udc->lock` dropped, so subsequent queue operations must tolerate callback-side mutation.

## Dependencies And Integration Points
Depends on Linux platform device, OF match, clock, DMA mapping, interrupt, and USB gadget APIs. It integrates with AST2600 UDC MMIO registers, coherent DMA memory, and gadget function drivers through `usb_add_gadget_udc`. Device tree supplies the compatible string and optional maximum-speed policy.

## Risks
The code has several fragile paths. `ast_udc_ep_dequeue` deletes the request from the queue before calling `ast_udc_done`, but `ast_udc_done` also deletes the request, which is a double-delete risk. If the request is not found, the post-loop check references the iterator variable after traversal in a way that is easy to get wrong. `ast_udc_ep_set_halt` uses `usb_endpoint_num(ep->desc)` and reads the root `AST_UDC_EP_CONFIG` for nonzero endpoints instead of the endpoint register helper, which looks suspicious and can misprogram stalls. `ast_udc_ep_queue` adds the request to the queue before DMA mapping and does not remove/unmap it on mapping or EP0 alignment failures. Descriptor-mode completion sums lengths into a `u16 total_len`, which can overflow if descriptor windows grow beyond 64 KiB. EP0 SET_ADDRESS writes address immediately rather than after status ACK, so host timing should be tested carefully.

## Test Signals
Primary signals are configfs gadget enumeration on AST2600, SET_ADDRESS/GET_STATUS handling, bulk/interrupt/iso transfers across all four programmable endpoints, descriptor-mode large IN transfers, single-stage fallback, active dequeue, halt/clear-halt, bus reset during traffic, suspend/resume callbacks, remote wake, and module remove while idle. KASAN/list-debug warnings around dequeue and queue error paths, incorrect endpoint halt behavior, DMA descriptor pointer warnings, or mismatched request actual lengths are high-value findings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.c

## Purpose
Implements the legacy Atmel AT91 full-speed USB Device Port controller as a PIO-only Linux USB gadget UDC driver. It manages six endpoints, FIFO reads/writes, EP0 control request handling, VBUS and pullup control, clock gating, suspend/resume/reset interrupts, chip-specific endpoint capacities, and OF platform binding for AT91RM9200 and AT91SAM926x variants.

## Important APIs, Types, And Functions
The driver uses `struct at91_udc`, `struct at91_ep`, and `struct at91_request` from `at91_udc.h`. Endpoint ops are `at91_ep_enable`, `at91_ep_disable`, `at91_ep_alloc_request`, `at91_ep_free_request`, `at91_ep_queue`, `at91_ep_dequeue`, and `at91_ep_set_halt`. Gadget ops are `at91_get_frame`, `at91_wakeup`, `at91_set_selfpowered`, `at91_vbus_session`, `at91_pullup`, `at91_start`, and `at91_stop`.

Transfer primitives are `read_fifo`, `write_fifo`, `done`, `nuke`, and `handle_ep`. EP0-specific control flow is in `handle_setup` and `handle_ep0`. Power and lifecycle helpers include `udc_reinit`, `reset_gadget`, `stop_activity`, `clk_on`, `clk_off`, `pullup`, VBUS IRQ/timer helpers, and PM suspend/resume. Chip-specific init/pullup is selected through `struct at91_udc_caps`.

## Control Flow
Probe allocates the controller, parses device tree GPIOs and compatible data, initializes endpoint objects/caps, maps UDP registers, applies chip-specific endpoint maxpacket setup, prepares clocks, disables the transceiver and interrupts, requests controller and optional VBUS IRQs or starts a VBUS polling timer, registers with the gadget core, enables wakeup, and creates an optional proc debug file.

The driver stays disconnected until both a gadget driver is bound and VBUS is present. `at91_start` records the gadget driver and marks the UDC enabled; `at91_pullup` and VBUS updates call `pullup`, which turns clocks/transceiver on or off and invokes chip-specific D+ pullup control. Endpoint queueing immediately tries to service an idle endpoint via PIO: IN requests write packet bytes into the FIFO and set TXPKTRDY; OUT requests pull bytes from RX banks and release banks. Ping-pong endpoints may rescan both banks before returning. Requests that cannot complete immediately are queued and endpoint interrupts are enabled.

The IRQ handler temporarily clocks the controller if needed, loops through pending masked IRQs up to five rescans, handles bus reset by resetting gadget state and enabling EP0, handles suspend/resume by toggling interrupt masks and invoking gadget callbacks, and dispatches endpoint IRQs. `handle_setup` reads an 8-byte setup packet, handles hardware-affecting standard requests such as SET_ADDRESS, SET_CONFIGURATION deferred config bit toggling, device/endpoint GET_STATUS, remote wakeup feature, and endpoint halt, otherwise delegates to the gadget driver. `handle_ep0` sequences setup, IN ACK, OUT data, status stages, deferred-address activation, and protocol stalls.

## State And Persistence Behavior
State is runtime-only and protected by a spinlock with IRQs disabled. It tracks VBUS, enabled, clocked, suspended, request pending, deferred address/config acknowledgements, current address, endpoint FIFO bank, endpoint direction/type/stopped state, and request queues. No data persists across unbind. Hardware state is deliberately reinitialized on reset, disconnect, clock-off, and endpoint enable/disable.

## Dependencies And Integration Points
Depends on Linux USB gadget, GPIO descriptor, clock, procfs debug, platform device, OF, regmap/syscon, and AT91 matrix definitions. It integrates with board wiring for VBUS and pullup GPIOs or SoC pullup registers, with two clocks (`pclk`, `hclk`), and with compatible-specific caps for at91rm9200, at91sam9260, at91sam9261, and at91sam9263.

## Risks
The CSR register has write-one/clear side effects, so the `SET_FX`/`CLR_FX` discipline is critical. PIO byte counts for IN completions are approximate because `req.actual` advances before host ACK; gadget drivers must tolerate this. Control-OUT deferred responses are explicitly unsupported and forced to stall if the gadget driver delays too long. VBUS polling uses timer/work and must be canceled by device lifetime management. Clocks are aggressively gated, so register access while unclocked is unsafe. Chip-specific endpoint size/ping-pong assumptions can break if compatible data or endpoint caps are changed. Several code paths unlock around callbacks and then resume touching driver state.

## Test Signals
Test full-speed enumeration, SET_ADDRESS timing, SET_CONFIGURATION, GET_STATUS, remote wakeup, endpoint halt/clear-halt, PIO IN/OUT transfers on each endpoint, ping-pong OUT buffering, disconnect/reconnect through VBUS GPIO, no-VBUS always-on mode, suspend/resume with wakeup enabled and disabled, and all compatible variants. Useful diagnostics are proc debug contents, endpoint interrupt masks, FIFO bank transitions, list-debug/KASAN around request completion, and gadget callback ordering during reset/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.h

## Purpose
Defines the AT91 USB Device Port register offsets, bit fields, endpoint count, minimal interrupt mask, core driver structures, request type, conversion helper, and debug macros used by `at91_udc.c`. It is the hardware and state contract for the full-speed PIO-only AT91 UDC driver.

## Important APIs, Types, And Functions
The header enumerates UDP registers such as `AT91_UDP_FRM_NUM`, `GLB_STAT`, `FADDR`, interrupt enable/disable/mask/status/clear, endpoint reset, endpoint CSR/FDR, and transceiver control. It defines CSR bits for TX completion, RX bank readiness, setup, stall, TX packet ready, endpoint type, direction, data toggle, endpoint enable, and RX byte count. `NUM_ENDPOINTS` fixes the driver at six endpoints. `MINIMUS_INTERRUPTUS` preserves reset/resume/suspend interrupts when most endpoint interrupts are disabled.

Driver structures are `struct at91_ep`, `struct at91_udc_caps`, `struct at91_udc_data`, `struct at91_udc`, and `struct at91_request`. `to_udc` maps a `usb_gadget` to the container. Debug macros `ERR`, `WARNING`, `INFO`, `DBG`, `VDBG`, and `PACKET` standardize driver logging.

## Control Flow
No executable control flow is implemented here beyond `to_udc`. The fields defined here directly drive `at91_udc.c`: endpoint queues and `int_mask` are used by queueing/IRQ dispatch; `is_pingpong`, `fifo_bank`, `is_in`, and `is_iso` guide FIFO service; UDC flags gate pullup, clocks, VBUS, suspend, and deferred EP0 status; chip-specific `caps` provide init and pullup callbacks; GPIO descriptors store board VBUS/pullup wiring.

## State And Persistence Behavior
All state described by the header is volatile in-memory kernel state. It models current USB controller state, endpoint queues, clocks, VBUS, and platform wiring, but nothing is persisted. Register definitions correspond to hardware state that is reprogrammed by probe, pullup, reset, endpoint enable/disable, and IRQ handling.

## Dependencies And Integration Points
Depends on Linux GPIO descriptors and USB gadget types included by the C file context. The register layout is based on the AT91RM9200 datasheet and shared by several AT91SAM variants with chip-specific differences supplied by `at91_udc_caps`. The matrix `regmap` pointer supports AT91SAM9261 pullup control.

## Risks
Bit definitions with side effects must remain accurate because endpoint CSR writes cannot simply echo read values. Changing `NUM_ENDPOINTS` without revisiting endpoint info, IRQ dispatch, and chip-specific maxpacket tables would corrupt assumptions. The `struct at91_udc` comment says the driver is non-SMP and protects chip registers by blocking IRQs; broader concurrency assumptions should be revisited before adding threaded or unlocked paths. The header's `ep_is_*` state fields are small bitfields, so updates must stay under lock.

## Test Signals
Header changes should be validated through build coverage and runtime enumeration on each compatible SoC. Exercise endpoint enable, FIFO reads/writes, bus reset, suspend/resume, VBUS changes, and chip-specific pullup logic. Compile errors in `at91_udc.c`, incorrect proc debug output, or broken endpoint IRQ masks indicate contract drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/at91_udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.c

## Purpose
Implements the Atmel/Microchip USBA high-speed USB device controller driver. It supports EP0 control handling, configurable endpoint FIFO layouts, DMA-capable endpoint transfers, FIFO fallback, debugfs inspection, VBUS-triggered start/stop, suspend/resume clock and bias handling, USB test modes, and OF platform binding for AT91SAM9, SAMA5D3, and SAM9X60 families.

## Important APIs, Types, And Functions
Endpoint operations are `usba_ep_enable`, `usba_ep_disable`, `usba_ep_alloc_request`, `usba_ep_free_request`, `usba_ep_queue`, `usba_ep_dequeue`, `usba_ep_set_halt`, `usba_ep_fifo_status`, and `usba_ep_fifo_flush`. Gadget operations are `usba_udc_get_frame`, `usba_udc_wakeup`, `usba_udc_set_selfpowered`, `atmel_usba_pullup`, `atmel_usba_start`, `atmel_usba_stop`, and `atmel_usba_match_ep`.

Transfer helpers include `next_fifo_transaction`, `submit_request`, `submit_next_request`, `receive_data`, `request_complete`, `request_complete_list`, `queue_dma`, `usba_update_req`, and `stop_dma`. EP0 and interrupt handling are centered on `handle_ep0_setup`, `usba_control_irq`, `usba_ep_irq`, `usba_dma_irq`, and `usba_udc_irq`. Platform/power code includes `usba_start`, `usba_stop`, `usba_vbus_irq_thread`, `start_clock`, `stop_clock`, `atmel_udc_of_init`, `usba_udc_probe`, remove, and PM callbacks.

## Control Flow
Probe maps separate control and FIFO resources, obtains clocks, initializes locks, disables the controller from a clean slate, parses OF compatible data and endpoint config, initializes endpoints and optional VBUS IRQ, registers the gadget UDC, and creates debugfs entries. Endpoint configuration is either automatic (`fifo_mode=0`, adjusted in `atmel_usba_match_ep`) or selected from static FIFO tables. Endpoint enable writes `EPT_CFG`, enables the endpoint, and enables endpoint and optional DMA interrupts; DMA endpoints set `AUTO_VALID` and disable endpoint interrupt reporting for DMA-owned transfers.

Queueing initializes request state. DMA-capable endpoints map the request, build a DMA control word, submit immediately if the queue is empty, and otherwise append to the queue. FIFO endpoints append and enable TX or RX readiness depending on direction and EP0 state. Completion removes requests, unmaps DMA when used, drops the spinlock, and calls gadget giveback.

EP0 is a state machine with `WAIT_FOR_SETUP`, data stages, status stages, address status, and test mode status. `handle_ep0_setup` handles standard GET_STATUS, CLEAR_FEATURE, SET_FEATURE, SET_ADDRESS, endpoint halt, remote wakeup, and test mode requests, delegating others to the gadget driver. `usba_control_irq` restarts until no immediately serviceable state remains, sequences TX complete and RX ready status stages, consumes setup packets, and stalls invalid state transitions.

The top-level IRQ handles suspend, wake, resume, DMA interrupts, endpoint interrupts, and bus reset. Reset reinitializes all endpoints, calls gadget reset if needed, determines speed, configures EP0, reenables key interrupts, and optionally preallocates claimed endpoint configs.

## State And Persistence Behavior
State is volatile: endpoint queues, endpoint config words, FIFO sizes/banks, DMA capability flags, EP0 state, devstatus bits, test mode, VBUS previous state, interrupt-enable cache, suspended/clocked flags, and errata bias state. `int_enb_cache` mirrors the hardware interrupt-enable register because the hardware appears to use write-style enable semantics. There is no disk persistence. Debugfs snapshots expose queues, DMA status, EP0 state, and registers when enabled.

## Dependencies And Integration Points
Depends on Linux gadget, DMA mapping, debugfs, GPIO descriptors, clocks, OF matching, syscon/regmap for PMC errata workarounds, runtime wakeup helpers, and Atmel PMC definitions. Compatible-specific endpoint arrays and errata tables cover `atmel,at91sam9rl-udc`, `atmel,at91sam9g45-udc`, `atmel,sama5d3-udc`, and `microchip,sam9x60-udc`.

## Risks
DMA queue error handling is subtle: `queue_dma` maps a request before taking the lock, but if the endpoint is no longer enabled it returns `-ESHUTDOWN` without unmapping the request. `usba_control_irq` assumes a request exists when TX ready is enabled; corrupted EP0 state or spurious bits could dereference a null request. FIFO auto-configuration changes maxpacket limits during endpoint matching, so gadget autoconfig behavior depends on call order. Suspend paths stop clocks and toggle bias; any register access while unclocked or missed bias pulse can break resume. Test mode deliberately reconfigures EP0 and resets endpoints. Interrupt status includes `USBA_HIGH_SPEED` even if not enabled, so reset speed detection relies on top-level status semantics.

## Test Signals
Validate high-speed and full-speed enumeration, EP0 standard and delegated setup requests, remote wakeup, USB test modes, DMA IN/OUT transfers including zero-length packets and 64 KiB boundary behavior, FIFO-mode transfers by disabling DMA-capable paths or using non-DMA endpoints, endpoint halt/clear, dequeue while DMA active, reset during traffic, VBUS insert/remove, suspend/resume with device wakeup, and all compatible endpoint maps. Debugfs queue/register files, DMA timeout errors, `DMA_CH_EN` warnings after completion, EP0 invalid-state stalls, and unbalanced DMA mapping reports are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.h

## Purpose
Defines the Atmel USBA UDC hardware register map, bitfield helpers, endpoint/DMA constants, debug categories, EP0 state enum, endpoint/request/controller structures, errata/config descriptors, and object conversion helpers consumed by `atmel_usba_udc.c`.

## Important APIs, Types, And Functions
The header defines USB controller registers (`USBA_CTRL`, `FNUM`, interrupt registers, endpoint reset, test), endpoint registers (`USBA_EPT_*`), DMA registers (`USBA_DMA_*`), bitfields for control, frame number, interrupt status, endpoint config/control/status, and DMA control/status. `USBA_BF`, `USBA_BFEXT`, and `USBA_BFINS` encode/extract/insert bitfields, while `usba_readl`, `usba_writel`, `usba_ep_readl`, `usba_ep_writel`, `usba_dma_readl`, and `usba_dma_writel` wrap relaxed MMIO.

Key types are `enum usba_ctrl_state`, `struct usba_dma_desc`, `struct usba_fifo_cfg`, `struct usba_ep`, `struct usba_ep_config`, `struct usba_request`, `struct usba_udc_errata`, `struct usba_udc_config`, and `struct usba_udc`. Conversion helpers are `to_usba_ep`, `to_usba_req`, and `to_usba_udc`.

## Control Flow
No complex control flow is implemented in the header. It defines the state machine values that `usba_control_irq` and `handle_ep0_setup` use, the endpoint capabilities that OF-compatible config arrays fill, and the register helpers that every runtime path uses for controller, endpoint, and DMA access. The `ep_is_control` macro separates EP0 from data endpoints in queueing and interrupt paths.

## State And Persistence Behavior
The structures model runtime-only kernel and hardware state. `struct usba_ep` holds register bases, FIFO address, endpoint name, queue, FIFO sizing, hardware index, DMA/isoc capability, direction/type flags, and debugfs state. `struct usba_request` tracks queue node, DMA control word, submitted/last/dma flags. `struct usba_udc` owns locks, MMIO bases, gadget driver, platform device, errata hooks, VBUS GPIO, endpoint array, clocks, bias/clock/suspend status, devstatus, test mode, interrupt-enable cache, debugfs root, and PMC regmap. Nothing here persists beyond device lifetime.

## Dependencies And Integration Points
Depends on Linux GPIO descriptors and USB gadget structures through the including C file. The register helpers assume the controller has separate control, endpoint, DMA, and FIFO regions laid out by `USBA_EPT_BASE`, `USBA_DMA_BASE`, and `USBA_FIFO_BASE`. Errata callbacks integrate with platform PMC regmap handling in the C file.

## Risks
`ep_is_idle` references `EP_STATE_IDLE`, which is not part of the active `enum usba_ctrl_state` and appears to be a stale macro; it is harmless only because it is unused. Relaxed MMIO access means ordering must be provided by surrounding code or hardware semantics where required. Bitfield macros use shifts based on `_SIZE` and `_OFFSET`; incorrect constants silently corrupt register programming. `USBA_NR_DMAS` is fixed at seven while some endpoint arrays contain up to sixteen endpoints, so DMA interrupt dispatch intentionally covers only DMA-capable low endpoints and must stay aligned with hardware. Structure bitfields are lock-protected assumptions, not atomic state.

## Test Signals
Header edits should be validated by building `atmel_usba_udc.c`, probing each compatible platform, checking endpoint register programming, DMA and FIFO transfer paths, EP0 state transitions, debugfs output, suspend/resume, and VBUS handling. Compile failures around `ep_is_idle`, wrong endpoint FIFO addresses, DMA IRQs for nonexistent channels, or invalid endpoint mapping messages after reset indicate contract regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.h -->
