# subset-b-005501 Research

Grouped source research for USB gadget UDC drivers under `sources/distributed-fs/ceph-client/drivers/usb/gadget/udc`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_udc_core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_udc_core.c

## Purpose

`fsl_udc_core.c` implements the Freescale high-speed USB device-controller driver for the USB DR block found on MPC8349E, MPC8313E, MPC5121E, and related SoCs. It exposes the controller through the Linux USB gadget UDC API, programs endpoint queue heads and device transfer descriptors, handles ep0 Chapter 9 control requests, dispatches interrupts for setup/completion/reset/suspend/port-change events, and binds as a platform driver for `fsl-usb2-udc` and compatible device-tree nodes.

## Important APIs, Types, and Functions

The public integration surface is through `fsl_ep_ops`, `fsl_gadget_ops`, and the `platform_driver` named `fsl-usb2-udc`. Endpoint operations include `fsl_ep_enable()`, `fsl_ep_disable()`, `fsl_alloc_request()`, `fsl_free_request()`, `fsl_ep_queue()`, `fsl_ep_dequeue()`, `fsl_ep_set_halt()`, `fsl_ep_fifo_status()`, and `fsl_ep_fifo_flush()`. Gadget operations include `fsl_get_frame()`, `fsl_wakeup()`, `fsl_vbus_session()`, `fsl_vbus_draw()`, `fsl_pullup()`, `fsl_udc_start()`, and `fsl_udc_stop()`.

Important internal routines are `dr_controller_setup()`, `dr_controller_run()`, `dr_controller_stop()`, `dr_ep_setup()`, `struct_ep_qh_setup()`, `ep0_setup()`, `fsl_build_dtd()`, `fsl_req_to_dtd()`, `fsl_queue_td()`, `fsl_prime_ep()`, `done()`, `nuke()`, `setup_received_irq()`, `tripwire_handler()`, `process_ep_req()`, `dtd_complete_irq()`, `reset_irq()`, and `fsl_udc_irq()`. Probe/remove and PM are handled by `fsl_udc_probe()`, `fsl_udc_remove()`, `fsl_udc_suspend()`, `fsl_udc_resume()`, `fsl_udc_otg_suspend()`, and `fsl_udc_otg_resume()`.

## Control Flow

Probe allocates the singleton `udc_controller`, records platform data, maps the controller registers, calls board/platform init, selects big- or little-endian accessors, validates `DCCPARAMS_DC`, reads the endpoint count, requests the shared IRQ, allocates the endpoint array and aligned coherent dQH table, creates the ep0 status request buffer, initializes hardware when not OTG-gated, initializes `usb_gadget`, configures ep0, creates non-control endpoint objects, creates the dTD DMA pool, and registers the gadget with `usb_add_gadget_udc_release()`.

When a gadget driver binds, `fsl_udc_start()` stores the driver and either registers with the OTG transceiver or starts the device controller by enabling interrupts and setting `USB_CMD_RUN_STOP`. Endpoint enable programs the dQH capability field and endpoint control register according to the descriptor type, direction, max packet size, high-bandwidth multiplier, and zero-length termination policy. Queueing maps the request for DMA, builds one or more dTDs up to `EP_MAX_LENGTH_TRANSFER`, links them, primes the endpoint, and adds the request to the endpoint queue. Completion interrupts walk `endptcomplete`, process dTD status and remaining lengths, and retire completed requests through `done()`.

Ep0 setup interrupts are read through the hardware setup tripwire to avoid racing a new setup packet. Standard `GET_STATUS`, `SET_ADDRESS`, endpoint halt feature, remote-wakeup/test-mode feature, and OTG feature cases are handled locally where possible; other requests are delegated to `driver->setup()`. The ep0 state machine moves through `WAIT_FOR_SETUP`, `DATA_STATE_XMIT`, `DATA_STATE_RECV`, and `WAIT_FOR_OUT_STATUS`, with `ep0_prime_status()` submitting status ZLPs as needed. Reset IRQs clear address and endpoint status, flush all endpoints, notify the gadget stack with either reset or disconnect semantics, restore ep0 setup, and restart the controller for controller resets.

## State and Persistence Behavior

All driver state is in-memory and hardware-register backed. The global `dr_regs`, optional `usb_sys_regs`, and singleton `udc_controller` point at the active device. `struct fsl_udc` stores gadget binding, platform data, endpoint array, IRQ, ep0 setup buffer, spinlock, optional USB PHY, soft-connect/VBUS/stopped flags, remote-wakeup and OTG suspend flags, coherent dQH memory, status request, dTD DMA pool, PHY mode, bus reset flag, current/resume USB states, ep0 state/direction, and pending device address. `struct fsl_ep` tracks the gadget endpoint, request queue, dQH pointer, stopped state, and endpoint name. `struct fsl_req` owns the gadget request plus its dTD chain.

No state is persisted to disk. Externally visible state is controller register state, USB gadget state, optional proc debug output under `driver/fsl_usb2_udc`, and callbacks to gadget drivers and OTG/PHY helpers. DMA descriptors and queue heads are coherent allocations whose lifetime is tied to active requests and the UDC lifetime.

## Dependencies and Integration Points

The driver depends on the Linux USB gadget framework, USB Chapter 9 definitions, platform-device resources, Freescale platform data in `linux/fsl_devices.h`, DMA mapping and DMA pools, optional USB PHY/OTG integration, optional proc debug files, IRQ handling, and SoC-specific system interface registers for PHY, IO, and snooping control. It uses runtime endian accessors on PPC32 because controller registers and descriptors can be big or little endian depending on SoC/platform data.

## Risks and Test Signals

Risk is concentrated in DMA descriptor ownership, endpoint queue manipulation under the spinlock, ep0 state transitions, endian conversion, reset races, OTG host/device role interaction, and timeout loops for controller reset and endpoint flush. `fsl_ep_disable()` clears `EPCTRL_RX_ENABLE | EPCTRL_TX_TYPE` on OUT endpoints, which is suspicious because RX type would be expected; this should be preserved unless separately audited against known behavior. Test signals include platform probe/remove, bind/unbind of several gadget drivers, ep0 enumeration and standard requests, SET_ADDRESS timing, endpoint halt/clear halt, multi-dTD transfers including ZLPs, DMA mapping failures, dequeue of active and queued requests, bus reset while requests are active, suspend/resume and remote wakeup, VBUS/pullup toggling, OTG transceiver paths, high/full/low speed detection, and big-endian descriptor/register platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_udc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_usb2_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_usb2_udc.h

## Purpose

`fsl_usb2_udc.h` is the private hardware and driver-state header for the Freescale USB DR gadget driver. It defines the device/host/system-interface register layouts, controller bit fields, endpoint queue-head and transfer-descriptor formats, alignment constraints, endpoint/request/controller private structures, ep0 state constants, and pipe/endpoint helper macros used by `fsl_udc_core.c`.

## Important APIs, Types, and Functions

The register map types are `struct usb_dr_device`, `struct usb_dr_host`, and `struct usb_sys_interface`. The DMA data structures are `struct ep_queue_head` for dQH entries and `struct ep_td_struct` for dTD entries. Driver-private types are `struct fsl_req`, `struct fsl_ep`, and `struct fsl_udc`. Helper macros include `ep_index()`, `ep_maxpacket()`, `ep_is_in()`, `get_ep_by_pipe()`, `get_pipe_by_windex()`, `get_pipe_by_ep()`, and the inline `get_qh_by_ep()`.

The constants cover USB command/status/interrupt bits, device address and endpoint-list registers, port status/control bits, OTG status/control bits, USB mode bits, endpoint control bits, snoop/system-interface control bits, dQH and dTD bit fields, DMA alignment requirements, endpoint directions, and ep0 transfer states.

## Control Flow

This header has no independent runtime control flow, but it defines the hardware contract that drives the implementation. Probe and controller setup use `usb_dr_device` and `usb_sys_interface` to map register offsets. Endpoint configuration uses endpoint-control bit fields plus `ep_queue_head` capability fields. Request queueing builds `ep_td_struct` chains using the dTD masks, alignment, packet-size, IOC, active, halt, and error bits. Completion walks the same descriptors and maps pipes back to `struct fsl_ep` instances through the helper macros. Ep0 direction is special: `get_qh_by_ep()` chooses between the two ep0 queue heads based on `udc->ep0_dir` because the driver exposes one ep0 object but hardware has separate IN and OUT dQHs.

## State and Persistence Behavior

The header describes volatile kernel and hardware state only. `struct fsl_udc` persists for the lifetime of the platform device and contains the active gadget binding, endpoint array, coherent queue-head allocation, status request, dTD pool, current USB state, ep0 state, endpoint direction, bus reset state, and VBUS/softconnect/OTG flags. `struct fsl_ep` persists per logical endpoint and owns the software queue. `struct fsl_req` persists per submitted request and owns its dTD chain until completion. No durable storage is involved.

## Dependencies and Integration Points

The header depends on `linux/usb/ch9.h` and `linux/usb/gadget.h` for standard USB request, endpoint, gadget, and descriptor definitions. It also depends on Freescale platform enums such as `enum fsl_usb2_phy_modes` supplied through included platform data in the C file. It is tightly coupled to the controller's dQH/dTD DMA format, the gadget framework's endpoint/request model, and platform-data fields for PHY mode, system-interface registers, endian mode, and controller version.

## Risks and Test Signals

Important risks are register-layout drift, wrong bit definitions, endian assumptions for dQH/dTD fields, alignment or DMA-boundary mismatches, and helper macros that depend on ep0 direction or endpoint descriptors being initialized. The `max_pipes` member is used by reset code and must be initialized coherently with `max_ep`; stale or zero values would skip queue reset. Test signals include compile coverage of all macro users, probe on controllers with different endpoint counts and PHY modes, ep0 IN and OUT transfers that exercise `get_qh_by_ep()`, multi-dTD transfers that cross 4 KiB pages, big-endian descriptor platforms, and reset paths that iterate all pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_usb2_udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.c

## Purpose

`goku_udc.c` implements the Toshiba TC86C001 "Goku-S" PCI USB full-speed device-controller driver. It exposes a small fixed-endpoint UDC to the USB gadget framework: ep0 plus three semi-configurable bulk/interrupt endpoints, with optional DMA for ep2 IN and cautious optional DMA for ep1 OUT. The driver manages PCI probing, MMIO register programming, control-request dispatch, PIO/DMA transfer progression, interrupt handling, and gadget bind/unbind.

## Important APIs, Types, and Functions

Endpoint operations are collected in `goku_ep_ops`: `goku_ep_enable()`, `goku_ep_disable()`, `goku_alloc_request()`, `goku_free_request()`, `goku_queue()`, `goku_dequeue()`, `goku_set_halt()`, `goku_fifo_status()`, and `goku_fifo_flush()`. Gadget operations are `goku_get_frame()`, `goku_udc_start()`, `goku_udc_stop()`, and `goku_match_ep()`. PCI integration is through `goku_probe()`, `goku_remove()`, `gadget_release()`, `pci_ids`, and `goku_pci_driver`.

Important internal helpers include `command()`, `ep_reset()`, `write_fifo()`, `read_fifo()`, `pio_advance()`, `start_dma()`, `dma_advance()`, `abort_dma()`, `done()`, `nuke()`, `goku_clear_halt()`, `udc_reinit()`, `udc_reset()`, `ep0_start()`, `udc_enable()`, `stop_activity()`, `ep0_setup()`, and `goku_irq()`. Optional proc debug output is produced by `udc_proc_read()`.

## Control Flow

PCI probe allocates `struct goku_udc`, enables the PCI device, reserves and maps BAR0, resets and reinitializes the controller, requests the shared IRQ, optionally enables bus mastering for DMA, creates debug proc output, and registers the gadget with `usb_add_gadget_udc_release()`. `udc_reinit()` creates four endpoint objects, sets FIFO/mode/status register pointers, initializes request queues, exposes ep1-ep3 for autoconfiguration, and leaves ep0 out of the normal endpoint list. A bound gadget driver calls `goku_udc_start()`, which stores the driver and starts power detection or ep0 enumeration.

Endpoint enable validates fixed endpoint number, transfer type, max packet size, direction, and endpoint invalid state. It chooses PIO or DMA based on endpoint number, direction, and `use_dma`, configures double buffering for ep1/ep2 where useful, writes endpoint mode, resets the endpoint, and marks it active. Queueing validates the request, maps it for DMA when needed, initializes status and actual length, forces ep0 IN ZLP policy, then either starts DMA or advances PIO immediately. If the request cannot complete synchronously, it is appended to the software queue and PIO dataset interrupts are enabled for non-DMA endpoints.

PIO IN writes bytes into the endpoint FIFO until maxpacket or request end and uses EOP to mark short/ZLP completion. PIO OUT reads active packet buffers, handles overflow by discarding excess bytes, completes on short packet or full request, and drains a second double buffer when possible. DMA setup writes start/end registers and `dma_master` bits; completion interrupts compute `actual` from the DMA current register, complete the request, and start the next queued request. Abort paths attempt FIFO disable plus DMA reset, but comments note weak hardware documentation and inconsistent OUT behavior.

The IRQ handler scans enabled interrupt bits under the spinlock, handles system error, power-detect connect/disconnect, suspend/resume callbacks, reset-done logging, ep0 setup/status/data events, DMA completion, and PIO dataset events, then rescans a bounded number of times to catch posted/new events. `ep0_setup()` reads the setup packet from split byte registers, handles selected `CLEAR_FEATURE` cases locally, tracks SET_CONFIGURATION for hardware state updates, delegates most requests to `driver->setup()`, and stalls ep0 on failure.

## State and Persistence Behavior

Driver state is volatile and anchored in `struct goku_udc`: gadget, lock, four endpoints, bound gadget driver, ep0 state, flags for PCI resources and configuration state, MMIO register pointer, interrupt-enable shadow, and IRQ counters. Each `struct goku_ep` tracks endpoint number, DMA flag, direction, stopped state, request queue, register pointers, and IRQ count. Each `struct goku_request` wraps a gadget request and queue node. Hardware-visible state lives in BAR0 registers for power detect, interrupt enable/status, endpoint mode/status/FIFO, dataset bits, EOP, command, and DMA registers. No disk persistence exists.

## Dependencies and Integration Points

The driver integrates with the PCI subsystem, Linux USB gadget framework, USB Chapter 9 descriptors, IRQ handling, optional procfs debug files, DMA mapping via `usb_gadget_map_request()`, and low-level MMIO accessors. It uses `usb_add_gadget_udc_release()` for UDC registration and callback release, and endpoint matching guides gadget autoconfiguration toward ep3 interrupt and ep2 bulk-IN when appropriate.

## Risks and Test Signals

Major risks are hardware quirks around DMA abort, OUT DMA hiding short packets, FIFO clear also clearing halt, ep0 status-stage timing, posted PCI/MMIO writes, and IRQ rescan ordering under concurrent events. The driver intentionally leaves OUT DMA disabled by default because short packets are protocol-significant. Test signals include PCI probe/remove resource cleanup, gadget bind/unbind, full-speed enumeration, ep0 setup requests with delegated and locally handled clear-feature cases, SET_CONFIGURATION state updates, PIO IN/OUT transfers for all endpoints, DMA IN transfers on ep2, optional OUT DMA stress if enabled, dequeue/disable while DMA is active, suspend/resume callbacks, disconnect/reconnect via power-detect IRQ, system-error recovery, endpoint halt/clear halt, fifo flush/status behavior, and proc debug visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.h

## Purpose

`goku_udc.h` defines the Toshiba TC86C001 "Goku-S" PCI BAR0 register layout, interrupt and command bits, DMA master controls, endpoint status/mode fields, standard-request helper bits, fixed FIFO limits, and private software data structures used by `goku_udc.c`.

## Important APIs, Types, and Functions

The central hardware type is packed `struct goku_udc_regs`, covering interrupt registers, DMA registers, power detect, endpoint FIFOs, endpoint mode/status/size registers, setup-packet byte registers, command/status registers, request-mode registers, address/ready fields, and an optional descriptor RAM area. Software types are `struct goku_ep`, `struct goku_request`, `enum ep0state`, and `struct goku_udc`. Utility macros include interrupt groups `INT_DEVWIDE` and `INT_EP0`, dataset masks `DATASET_A/B/AB()`, endpoint status encodings, command encodings, DMA endpoint constants `UDC_MSTWR_ENDPOINT` and `UDC_MSTRD_ENDPOINT`, and logging helpers.

## Control Flow

The header itself has no runtime flow, but it defines how the C file drives the device. Interrupt bits in `int_status` are masked by the software `int_enable` shadow and routed to device-wide, ep0, PIO endpoint, or DMA-completion handling. Endpoint commands are issued by writing `COMMAND_EP(n) | command` to `Command`. PIO paths inspect `DataSet`, `EPxSizeLA/LB`, and FIFO registers. DMA paths program `out_dma_*`, `in_dma_*`, and `dma_master` with the MST read/write enable, reset, timeout, and EOP policies. Ep0 state values constrain when setup, data, status, stall, suspend, and disconnect processing can touch registers.

## State and Persistence Behavior

All state represented here is runtime-only. `struct goku_udc` persists for the lifetime of the PCI device and owns the gadget, endpoint array, driver pointer, ep0 state, resource flags, register mapping, interrupt mask shadow, configuration flags, and statistics. `struct goku_ep` persists for each fixed endpoint and tracks DMA/PIO mode, direction, stopped state, request queue, and register pointers. `struct goku_request` is per-transfer. Hardware state is the MMIO BAR contents and is reset during probe, disconnect, and stop paths.

## Dependencies and Integration Points

This header is private to the Goku UDC driver but assumes Linux USB gadget types and PCI/MMIO usage from the C file. It encodes the controller's fixed four-endpoint model, hardware-assisted subset of standard requests, full-speed FIFO limits, and DMA wiring where master-write maps to ep1 OUT and master-read maps to ep2 IN when `MST_CONNECTION` is clear.

## Risks and Test Signals

Risks include packed register-layout correctness, bit-mask mistakes in interrupt acknowledgement and endpoint commands, mismatch between fixed endpoint numbers and descriptors, DMA direction assumptions tied to `MST_CONNECTION`, and state-machine transitions that allow register access during suspend. Test signals are compile coverage, BAR register dump sanity through proc debug, endpoint enable for 8/16/32/64 maxpacket values, PIO dataset handling with single and double buffering, DMA IN on ep2, power-detect connect/disconnect, command delay adequacy, and ep0 state transitions through setup/data/status/stall/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.c

## Purpose

`gr_udc.c` implements the Aeroflex Gaisler GRUSBDC USB peripheral controller driver for GRLIB systems. It supports DMA-mode GRUSBDC cores with up to 16 IN and 16 OUT endpoints, registers as a platform UDC, maps gadget endpoint requests to GRUSBDC DMA descriptors, handles ep0 standard requests and setup delegation, tracks VBUS/reset/suspend/resume state, and supports optional split IN/OUT interrupt lines.

## Important APIs, Types, and Functions

Endpoint operations are `gr_ep_enable()`, `gr_ep_disable()`, `gr_alloc_request()`, `gr_free_request()`, `gr_queue_ext()`, `gr_dequeue()`, `gr_set_halt()`, `gr_set_wedge()`, `gr_fifo_status()`, and `gr_fifo_flush()` via `gr_ep_ops`. Gadget operations are `gr_get_frame()`, `gr_wakeup()`, `gr_pullup()`, `gr_udc_start()`, and `gr_udc_stop()` via `gr_ops`. Platform integration uses `gr_probe()`, `gr_remove()`, `gr_request_irq()`, `gr_match`, and `gr_driver`.

Important internal paths include DMA descriptor allocation/freeing (`gr_alloc_dma_desc()`, `gr_free_dma_desc_chain()`), request completion (`gr_finish_request()`), DMA start/advance/abort (`gr_start_dma()`, `gr_dma_advance()`, `gr_abort_dma()`), descriptor construction (`gr_setup_out_desc_list()`, `gr_setup_in_desc_list()`), ep0 helpers (`gr_ep0_respond()`, `gr_set_address()`, `gr_device_request()`, `gr_interface_request()`, `gr_endpoint_request()`, `gr_ep0_setup()`, `gr_ep0out_requeue()`), state handlers (`gr_vbus_connected()`, `gr_vbus_disconnected()`, `gr_udc_usbreset()`, `gr_handle_state_changes()`), endpoint IRQ handlers (`gr_handle_in_ep()`, `gr_handle_out_ep()`), and threaded IRQ handlers (`gr_irq()`, `gr_irq_handler()`).

## Control Flow

Probe allocates `struct gr_udc` with devm memory, maps the platform MMIO resource, obtains the primary IRQ and optional separate IN/OUT IRQs, initializes the gadget object and lock, reads the status register to determine endpoint counts and verify DMA mode, creates a DMA pool for hardware descriptors, registers the gadget UDC, initializes endpoints, disables leftover interrupts/pullup, creates debugfs state, and requests threaded IRQs. `gr_udc_init()` initializes ep0 IN/OUT and all available endpoints, allocates ep0 request buffers, allocates per-endpoint coherent tail buffers, enables ep0 hardware, and sets the starting ep0 state to disconnect.

Gadget bind calls `gr_udc_start()`, storing the gadget driver and enabling VBUS detection. VBUS-valid state turns on status, USB reset, VBUS, suspend, and endpoint interrupts plus pullup. USB reset clears address, sets ep0 setup state, updates gadget state and speed, nukes ep0 queues, unstops ep0 endpoints, and requeues the ep0 OUT setup request. Disconnect stops all endpoints, disables pullup/interrupts, reports gadget disconnect, and re-enables VBUS detection.

Request queueing maps the buffer for DMA, builds an IN or OUT descriptor chain, sets request status and actual length, appends to the endpoint queue, and starts DMA if idle. IN descriptors are all enabled immediately and only the last descriptor requests packet-interrupt completion. OUT descriptors are enabled one at a time so the driver can detect short packets and setup packets; the last short segment may use a coherent bounce `tailbuf` because hardware cannot safely receive smaller-than-maxpacket OUT buffers directly. The threaded IRQ scans IN endpoints first, then OUT endpoints, then state changes. IN completion waits until the last descriptor is disabled and endpoint hardware buffers are empty. OUT completion accumulates descriptor lengths, handles setup-packet markers, queues ep0 status ZLP for OUT data stage, or enables the next descriptor and announces descriptor availability.

Ep0 processing uses a permanently requeued OUT request for setup packets. `gr_ep0_setup()` validates the current ep0 state, decodes the setup packet, handles standard device/interface/endpoint requests where possible, delegates the rest to `driver->setup()`, stalls on negative status, updates gadget configured/addressed state on SET_CONFIGURATION/SET_ADDRESS, advances IDATA/ODATA to status states, and requeues ep0 OUT. Test mode is applied in the IN status completion callback.

## State and Persistence Behavior

State is volatile in `struct gr_udc`, endpoint structures, request structures, DMA descriptors, MMIO registers, and debugfs. `struct gr_udc` stores gadget binding, endpoint arrays, DMA pool, device pointer, ep0 requests, register mapping, IRQ numbers, added/irq flags, remote-wakeup and test-mode state, suspended-from state, endpoint counts, endpoint list, and spinlock. Each `struct gr_ep` stores endpoint metadata, register pointer, queue, DMA-start flag, stopped/wedged/callback flags, bytes-per-buffer, and coherent OUT tail buffer. Each `struct gr_request` stores descriptor-chain pointers, even/odd OUT tail accounting, and setup-packet indication. No durable storage is written.

## Dependencies and Integration Points

The driver depends on platform-device resources, Open Firmware match data, big-endian MMIO accessors, USB gadget APIs, DMA mapping and DMA pools, coherent DMA allocations, threaded IRQs, debugfs, and USB Chapter 9 request definitions. Device-tree properties `epobufsizes` and `epibufsizes` optionally set endpoint buffer-size limits; status-register fields also report endpoint counts and DMA/slave mode. It integrates with the gadget framework through `usb_add_gadget_udc()` and with PM-visible USB state through `usb_gadget_set_state()`.

## Risks and Test Signals

High-risk areas are DMA descriptor enable/ownership ordering, OUT bounce-buffer overflow handling, ep0 setup requeue ordering, suspend/resume callbacks under spinlock release/reacquire, multi-IRQ sharing, endpoint halt/wedge semantics, and cleanup of resources allocated after `usb_add_gadget_udc()`. Probe registers the gadget before `gr_udc_init()`, with a comment noting cleanup effects may need attention; this ordering is worth testing. Test signals include DMA-mode probe and rejection of slave-mode cores, endpoint-count discovery, optional separate IRQ lines, bind/unbind, VBUS connect/disconnect, USB reset, high/full speed changes, standard ep0 requests, SET_CONFIGURATION state transitions, remote wakeup and test mode, IN and OUT transfers across multiple descriptors, zero-length IN packets, odd-sized OUT tails and overflow, dequeue of active/nonactive requests, halt/wedge/clear-halt including from-host cases, suspend/resume callbacks, debugfs state dumps, and remove/error unwind after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.h

## Purpose

`gr_udc.h` is the private hardware and state header for the Aeroflex Gaisler GRUSBDC gadget driver. It defines the big-endian AMBA register layout, endpoint/control/status bit fields, DMA descriptor format, endpoint/request/controller private structures, and ep0 state enum used by `gr_udc.c`.

## Important APIs, Types, and Functions

Hardware layout types are `struct gr_epregs` for per-endpoint registers and `struct gr_regs` for OUT endpoint blocks, IN endpoint blocks, global control, and global status. DMA is described by `struct gr_dma_desc`, with hardware-used `ctrl`, `data`, and `next` fields followed by software-only physical and virtual chain pointers. Driver-private types are `struct gr_ep`, `struct gr_request`, `enum gr_ep0state`, and `struct gr_udc`. The helper macro `to_gr_udc()` maps a gadget pointer back to controller state.

Constants describe endpoint control fields for buffer size, packet interrupt, clear buffer/status, max payload, additional transactions, transfer type, halt/disable/valid; DMA control bits for AMBA error, abort, interrupt, interrupt enable, and descriptor availability; endpoint status buffer bits and byte counts; global control bits for interrupts, pullup, remote wakeup, test mode, address, and speed update; and status fields for endpoint counts, DMA mode, USB reset, VBUS, speed, address function, and frame number.

## Control Flow

The header has no independent execution, but it defines the hardware contract for the driver. Probe reads `GR_STATUS_NEPI`, `GR_STATUS_NEPO`, and `GR_STATUS_DM` to discover capabilities. Endpoint init and enable program `epctrl` and `dmactrl` using the bit definitions. Queueing creates `gr_dma_desc` chains and writes descriptor physical addresses to `dmaaddr`; interrupt handling checks descriptor enable bits, endpoint status buffers, DMA error bits, and global status changes. Ep0 control flow is represented by `enum gr_ep0state`, which distinguishes disconnect, setup, IN/OUT data, IN/OUT status, stall, and suspend states.

## State and Persistence Behavior

All structures are runtime-only. `struct gr_udc` persists for the platform device lifetime and owns the gadget, endpoint arrays, descriptor DMA pool, ep0 request objects, register mapping, IRQ numbers, remote-wakeup/test-mode state, endpoint counts, and lock. `struct gr_ep` persists per direction and endpoint number, including queue state and coherent `tailbuf` for OUT odd-tail reception. `struct gr_request` persists per transfer and owns a DMA descriptor chain until completion. The only external projection is hardware MMIO state, gadget state, and optional debugfs output.

## Dependencies and Integration Points

The header is private to GRUSBDC and assumes Linux USB gadget types, DMA APIs, list handling, spinlocks, and platform/of integration supplied by the C file. It encodes the core's DMA-only driver support; the C file rejects slave-mode hardware despite the register union documenting slave-mode fields. It also embeds the maximum 16-IN/16-OUT endpoint topology used for endpoint arrays and name tables.

## Risks and Test Signals

Risks include big-endian register access assumptions, descriptor layout mismatch where hardware only consumes the first three words, bit-field mistakes in max payload and buffer-size calculations, endpoint count bounds, and the use of one `GR_EPSTAT_PT/PR` bit position for direction-specific meanings. Test signals include compile coverage, register dump sanity from debugfs, probe on cores with different endpoint counts and buffer sizes, DMA descriptor pool alignment, ep0 setup and status transitions, OUT odd-tail bounce behavior, and hardware interrupt/error handling for all endpoint directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.h -->
