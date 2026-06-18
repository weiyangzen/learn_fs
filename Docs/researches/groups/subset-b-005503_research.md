# subset-b-005503 Research

Grouped source research for USB gadget UDC controller drivers under `sources/distributed-fs/ceph-client/drivers/usb/gadget/udc`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.c

## Purpose

`net2280.c` is the Linux USB gadget UDC driver for PLX/NetChip NET2280/NET2282 PCI and PLX USB2380/USB3380/USB3382 PCIe device controllers. It binds PCI devices, maps controller register BARs, exposes a `usb_gadget`, implements `usb_ep_ops` for endpoint enable/disable/request queueing/dequeueing/stall/fifo operations, handles control endpoint setup traffic, dispatches DMA/PIO/USB-state interrupts, and registers/unregisters with the gadget core through `usb_add_gadget()` and `usb_del_gadget()`.

The file supports both older high/full-speed NET228x chips and newer USB338x SuperSpeed-capable parts. Much of the implementation is hardware-family branching and errata handling: NET2280 rev1 workarounds for FIFO and DMA races, USB338x enhanced endpoint naming, SuperSpeed U1/U2/LTM feature handling, sequence-number reset, and the Defect 7374 workaround around first SuperSpeed control reads.

## Important APIs, Types, and Functions

The driver implements `net2280_ep_ops`: `net2280_enable()`, `net2280_disable()`, `net2280_alloc_request()`, `net2280_free_request()`, `net2280_queue()`, `net2280_dequeue()`, `net2280_set_halt()`, `net2280_set_wedge()`, `net2280_fifo_status()`, and `net2280_fifo_flush()`. These are the gadget-function-facing endpoint operations. Request state is represented by `struct net2280_request`, while endpoint and device state are defined in `net2280.h`.

The `usb_gadget_ops` table `net2280_ops` provides `net2280_get_frame()`, `net2280_wakeup()`, `net2280_set_selfpowered()`, `net2280_pullup()`, `net2280_start()`, `net2280_stop()`, `net2280_async_callbacks()`, and `net2280_match_ep()`. `net2280_match_ep()` biases interrupt endpoints toward PIO endpoints so DMA-capable endpoints remain available for bulk/isoc traffic, and USB338x enhanced mode can match endpoint names like `ep1in`, `ep2out`, and so on.

Core transfer helpers include `write_fifo()` and `read_fifo()` for PIO, `fill_dma_desc()`, `start_queue()`, `start_dma()`, `queue_dma()`, `scan_dma_completions()`, `restart_dma()`, `abort_dma()`, `nuke()`, and `done()`. `done()` unmaps DMA when needed, temporarily drops `dev->lock`, and gives requests back through `usb_gadget_giveback_request()`.

Hardware setup and lifecycle helpers include `usb_reset_228x()`, `usb_reset_338x()`, `usb_reinit_228x()`, `usb_reinit_338x()`, `set_fifo_mode()`, `ep_reset_228x()`, `ep_reset_338x()`, `ep0_start_228x()`, `ep0_start_338x()`, and `stop_activity()`. Interrupt entry and dispatch are handled by `net2280_irq()`, `handle_stat0_irqs()`, `handle_stat0_irqs_superspeed()`, `handle_ep_small()`, `usb338x_handle_ep_intr()`, and `handle_stat1_irqs()`.

PCI integration is through `net2280_probe()`, `net2280_remove()`, `net2280_shutdown()`, the `pci_ids[]` table, and `net2280_pci_driver`. Debug integration is optional under `CONFIG_USB_GADGET_DEBUG_FILES`, exposing `function`, `registers`, and `queues` device attributes.

## Control Flow

Probe allocates `struct net2280`, initializes the embedded gadget, enables the PCI device, claims and maps BAR0, derives register block pointers, detects legacy versus PCIe/USB338x behavior from `pci_device_id.driver_data`, detects USB338x enhanced mode, then calls `usb_reset()` and `usb_reinit()`. It requests an IRQ, creates a DMA pool for endpoint descriptors, allocates one dummy descriptor for each DMA endpoint, enables PCI DMA memory-read/write optimizations where applicable, reads chip revision through an indexed register, creates the debug `registers` file, and registers the gadget with the UDC core.

Gadget binding enters `net2280_start()`. The function requires a gadget driver with at least high-speed support and a setup callback, records the driver, creates optional debug attributes, marks LEDs active, applies the USB338x Defect 7374 pre-workaround if needed, and starts EP0. Pullup control later toggles `USB_DETECT_ENABLE`; disabling pullup calls `stop_activity()` to reset hardware and complete pending requests.

Endpoint enable validates descriptors, rejects unavailable endpoint numbers, enforces max-packet limits for legacy small FIFOs and bulk speeds, programs speed-dependent max packet registers, flushes FIFO state, configures endpoint type/direction/address/burst, NAKs OUT endpoints until reads are queued, clears PCIe sequence numbers, and enables either per-packet PIO interrupts or DMA completion interrupts. Endpoint disable nukes pending requests and resets the hardware endpoint.

Request queueing validates the request, maps DMA buffers for DMA endpoints, sets `-EINPROGRESS`, and either starts the transfer immediately or links it behind the active request. PIO IN writes one packet into the FIFO; PIO OUT may immediately drain buffered data and then clears NAK to accept more. DMA starts with a scatter/gather descriptor chain and a dummy tail descriptor; additional requests swap and link descriptor dummies. DMA ZLP requests are explicitly rejected rather than falling back to PIO.

EP0 setup interrupts are handled in `handle_stat0_irqs()`. On the first setup packet after connect it determines speed, updates EP0 max packet limits, clears old EP0 requests, reads the setup registers, and configures token-level EP0 interrupts. Some standard endpoint status and halt requests are handled locally; most class/vendor/configuration/interface requests are delegated to the gadget driver when async callbacks are enabled. SuperSpeed setup handling goes through `handle_stat0_irqs_superspeed()` to manage U1, U2, LTM, remote wakeup, and SuperSpeed status semantics.

Interrupt handling splits status register 1 from status register 0. `handle_stat1_irqs()` handles VBUS disconnect/root reset, suspend/resume callbacks, DMA completion, and fatal PCI DMA errors. `handle_stat0_irqs()` handles setup and endpoint PIO/small-transfer interrupts. `handle_ep_small()` advances EP0 and non-DMA endpoint queues per packet and also manually completes short OUT DMA transfers that cannot rely on a normal DMA interrupt. Removal unregisters the gadget, destroys DMA resources, frees IRQ/MSI, unmaps registers, releases the PCI region, disables the PCI device, removes debug files, and drops the gadget reference.

## State and Persistence Behavior

State is runtime-only in kernel memory and controller registers. Device-level state includes `dev->driver`, `enabled`, `softconnect`, `got_irq`, `region`, `added`, SuperSpeed feature bits (`u1_enable`, `u2_enable`, `ltm_enable`, `wakeup_enable`), `addressed_state`, `async_callbacks`, `bug7734_patched`, `chiprev`, `enhanced_mode`, `n_ep`, quirk flags, BAR register pointers, and the DMA descriptor pool. Endpoint state includes descriptor binding, hardware register pointers, optional DMA channel, dummy descriptor, FIFO size, request queue, direction/type bits, stopped/wedged flags, short-OUT overflow state, and interrupt counters.

Requests persist only while queued or owned by the gadget driver. DMA request state includes a per-request hardware descriptor, DMA address, mapped flag, and descriptor-valid flag. The driver does not write durable storage; externally visible state is projected through USB enumeration, PCI device state, UDC registration, optional debug attributes, LEDs/GPIOs, and controller registers. Module parameters `fifo_mode` and `enable_suspend` affect runtime behavior but are not persisted by this file.

## Dependencies and Integration Points

The file depends on the Linux PCI core, DMA mapping and DMA pools, MMIO accessors, interrupt APIs, USB Chapter 9 definitions, the USB gadget/UDC core, PLX NET2280 and USB338x register definitions from `<linux/usb/net2280.h>` and `<linux/usb/usb338x.h>`, and local state/helpers from `net2280.h`. It integrates upward with gadget function drivers through endpoint operations, setup callbacks, disconnect/suspend/resume callbacks, pullup control, remote wakeup, and UDC async-callback policy.

Hardware integration is through BAR0 register blocks for main, USB, PCI, DMA, dedicated endpoint, configurable endpoint, link-layer, protocol-layer, and USB338x extension registers. PCI IDs cover legacy vendor `0x17cc` NET2280/2282 and PLX USB2380/3380/3382 devices. The debug attributes are useful integration points for user-space inspection during gadget bring-up.

## Risks and Test Signals

High-risk areas are lock and callback ordering, DMA descriptor ownership, and silicon-specific behavior. `done()` and setup/disconnect/suspend paths drop `dev->lock` around gadget-driver callbacks, so request queues and endpoint stopped state must remain consistent across reentrant submissions or dequeues. DMA completion scanning depends on descriptor `VALID_BIT` visibility and memory barriers; queue patching in `net2280_dequeue()` must stop and restart DMA without losing descriptor state. PIO and DMA OUT paths carry explicit overflow handling and errata-driven FIFO flushing.

Legacy NET2280 paths are sensitive to rev1 errata around NAK/OUT FIFO races, short OUT DMA, DMA polling/autostart, and endpoint number 13 avoidance. USB338x paths are sensitive to enhanced-mode endpoint mapping, SuperSpeed feature requests, sequence-number resets on halt clear, interrupt bit mapping via `ep_bit[]`, and the Defect 7374 FSM kept in the scratch register. The probe error path is also delicate because `net2280_probe()` calls `net2280_remove()` and then frees `dev` on failure.

Useful test signals include PCI probe/remove for every ID table family, MSI failure fallback, gadget bind/unbind, pullup on/off, high/full/SuperSpeed enumeration, EP0 standard request handling, delegated class/vendor setup requests, SET/CLEAR_FEATURE endpoint halt with active and idle queues, U1/U2/LTM enable and status for USB338x, DMA bulk IN/OUT including short OUT packets and overflow, PIO interrupt endpoints, DMA ZLP rejection behavior, request dequeue while active and queued, disconnect and root reset while transfers are active, suspend/resume callbacks with `enable_suspend` both false and true, debug `registers`/`queues` output under load, and injected PCI/DMA error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.h

## Purpose

`net2280.h` is the private header for the PLX/NetChip NET2280/NET2282 and USB338x gadget UDC driver. It defines controller quirk flags, selected indexed register constants, EP0 max-packet constants, Defect 7374 FSM state encodings, DMA descriptor layout, endpoint/request/device runtime structures, and small inline helpers for indexed register access, EP0 status handshakes, halt control, LEDs, logging, FIFO byte counts, OUT NAK control, and speed-dependent endpoint max-packet programming.

## Important APIs, Types, and Functions

`get_idx_reg()` and `set_idx_reg()` access indirect indexed registers through `idxaddr` and `idxdata`; callers are expected to hold the device lock. `struct net2280_dma` is the 16-byte-aligned scatter/gather descriptor consumed by the controller. `struct net2280_ep` wraps `struct usb_ep` with hardware register pointers, DMA channel pointer, dummy DMA descriptor, queue, endpoint descriptor, FIFO size, direction/type flags, stopped/wedged state, control-response state, and interrupt counters.

`struct net2280_request` wraps `struct usb_request` with a hardware DMA descriptor, descriptor DMA address, queue node, and mapped/valid flags. `struct net2280` wraps `struct usb_gadget` with the controller-wide spinlock, up to nine endpoints, the currently bound gadget driver, runtime flags, chip revision, enhanced-mode state, quirk bits, PCI device pointer, MMIO register block pointers, and a DMA pool for request descriptors.

Inline helpers include `allow_status()` and `allow_status_338x()` for EP0 status-phase unblocking, `set_halt()` and `clear_halt()` for endpoint stall/toggle control, RDK LED helpers under `USE_RDK_LEDS`, logging macros, `set_fifo_bytecount()`, `start_out_naking()`, `stop_out_naking()`, and `set_max_speed()`. The quirk flags `PLX_LEGACY`, `PLX_2280`, `PLX_SUPERSPEED`, and `PLX_PCIE` drive most family-specific logic in `net2280.c`.

## Control Flow

The header has no standalone module flow, but its helpers are in the hot path. Probe and reinit fill `struct net2280` and `struct net2280_ep`, then endpoint enable/queue/IRQ code uses these structures to reach the correct MMIO blocks. EP0 setup handling calls `allow_status()` or `allow_status_338x()` after local status responses or zero-length status stages. Halt helpers are called from gadget endpoint operations and control-request handling. OUT NAK helpers gate when the controller may accept OUT packets relative to queued reads.

The Defect 7374 definitions encode a small state machine in the controller `SCRATCH` indexed register. `net2280.c` seeds it before the first control read and updates it after SuperSpeed or non-SuperSpeed detection so the USB338x data-endpoint workaround is only applied when needed.

## State and Persistence Behavior

All structures are runtime state. `struct net2280` persists for the PCI device lifetime and is released through the gadget device release callback. `struct net2280_ep` persists inside the device object, while `struct net2280_request` persists per allocated USB request. The header stores no file-backed state. The only quasi-persistent hardware state described here is controller register state, including the indexed `SCRATCH` field used for Defect 7374 until chip power is lost.

The bitfields in endpoint and device structures compact many booleans that are mutated under `dev->lock`. The header comments make the locking assumption explicit for indexed register helpers because writes through `idxaddr`/`idxdata` are globally shared for the controller.

## Dependencies and Integration Points

The header depends on kernel USB gadget types, PCI-facing register definitions from `<linux/usb/net2280.h>` and `<linux/usb/usb338x.h>`, MMIO accessors, DMA address types, list heads, and GPIO/register bit definitions supplied by the included hardware headers. It is the structure boundary between the UDC implementation, the USB gadget core, PCI device state, DMA pools, and PLX/USB338x register maps.

## Risks and Test Signals

Risks include register access races if indexed helpers are called without the device lock, bitfield assumptions that diverge from hardware state, writing the wrong endpoint configuration field for legacy versus PCIe vendors in `set_fifo_bytecount()`, and incorrect speed-index calculations in `set_max_speed()` for enhanced mode. Halt and NAK helpers directly manipulate EP0 and endpoint response registers, so small changes can break Chapter 9 status-stage timing or OUT transfer flow control.

Useful test signals include compile coverage for all quirk combinations, endpoint enable at full/high/SuperSpeed to exercise `set_max_speed()`, EP0 status stages on legacy and USB338x chips, endpoint halt clear/set and wedge behavior, OUT request queueing that toggles NAK state, Defect 7374 FSM transitions across cold boot and reconnect, and debug inspection of endpoint flags versus register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/net2280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.c

## Purpose

`omap_udc.c` is the full-speed USB device controller driver for OMAP1-era SoCs with optional OTG support. It exposes the OMAP UDC as a Linux USB gadget controller, configures the controller's limited 2 KiB FIFO RAM before enumeration, implements endpoint operations for PIO and optional OMAP DMA transfers, handles EP0 Chapter 9 control traffic, processes device-state, DMA, PIO, and ISO interrupts, manages pullup/VBUS/OTG interactions, and registers as the `omap_udc` platform driver.

Unlike many gadget controllers, this hardware requires endpoint/FIFO layout to be selected before D+ pullup and enumeration. The module parameter `fifo_mode` selects a fixed endpoint map, and `use_dma` controls whether bulk endpoints attempt to claim OMAP DMA channels.

## Important APIs, Types, and Functions

The endpoint operation table `omap_ep_ops` provides `omap_ep_enable()`, `omap_ep_disable()`, `omap_alloc_request()`, `omap_free_request()`, `omap_ep_queue()`, `omap_ep_dequeue()`, and `omap_ep_set_halt()`. Endpoint and request state live in `struct omap_ep` and `struct omap_req` from `omap_udc.h`, and controller state lives in the global `struct omap_udc *udc`.

The gadget operation table `omap_gadget_ops` provides `omap_get_frame()`, `omap_wakeup()`, `omap_set_selfpowered()`, `omap_vbus_session()`, `omap_vbus_draw()`, `omap_pullup()`, `omap_udc_start()`, and `omap_udc_stop()`. These connect the gadget core to frame reads, remote wakeup/SRP, self-powered status, external transceiver VBUS notifications, current draw reporting, and soft-connect control.

PIO helpers are `use_ep()`, `deselect_ep()`, `write_packet()`, `write_fifo()`, `read_packet()`, and `read_fifo()`. DMA helpers are `dma_src_len()`, `dma_dest_len()`, `next_in_dma()`, `finish_in_dma()`, `next_out_dma()`, `finish_out_dma()`, `dma_irq()`, `dma_error()`, `dma_channel_claim()`, and `dma_channel_release()`. Queue and teardown helpers include `done()`, `nuke()`, and `udc_quiesce()`.

Control and IRQ handling centers on `ep0_irq()`, `devstate_irq()`, `omap_udc_irq()`, `omap_udc_pio_irq()`, `omap_udc_iso_irq()`, and `pio_out_timer()`. Setup/probe paths include `omap_ep_setup()`, `omap_udc_setup()`, `omap_udc_probe()`, `omap_udc_remove()`, `omap_udc_suspend()`, and `omap_udc_resume()`. Optional debug output is exposed through `/proc/driver/udc` via `proc_udc_show()` when gadget debug files are enabled.

## Control Flow

Platform probe claims the memory resource, enables clocks on OMAP16xx long enough to inspect and initialize the controller, validates HMC/transceiver mode, obtains an external USB2 PHY when required, then calls `omap_udc_setup()`. Setup clears previous hardware state, allocates `struct omap_udc`, initializes the gadget, sets full-speed max speed and `quirk_ep_out_aligned_size`, creates EP0 just after the SETUP buffer, disables all other endpoints, then builds a fixed endpoint list according to `fifo_mode`. It writes endpoint RX/TX configuration registers and finally locks the configuration with `UDC_CFG_LOCK | UDC_SELF_PWR`.

Probe disables pullup, sets OTG capability from platform data, chooses the correct clear-halt sequence based on UDC revision, requests the general, PIO, and optional ISO IRQs, parks clocks if applicable, creates the proc debug file, and registers the gadget through `usb_add_gadget_udc_release()`. The release callback disables pullup, releases the transceiver and clocks, removes the proc file, completes pending remove synchronization, and frees `udc`.

Gadget start resets endpoint runtime state, halts non-ISO endpoints, records the gadget driver, enables clocks temporarily, clears pending IRQs, binds to an OTG transceiver when present, otherwise toggles pullup based on `softconnect` and VBUS, and fakes VBUS on boards without sensing. Stop unbinds from the transceiver or disables pullup, quiesces all endpoints, clears the driver pointer, and gates clocks again.

Endpoint enable validates descriptor address/type/maxpacket against the preconfigured endpoint, rejects unsupported ISO periods, clears halt/toggle state, optionally links ISO endpoints into the SOF-serviced list, tries to claim a DMA channel for bulk endpoints, and primes PIO OUT FIFOs when DMA is not used. `omap_ep_queue()` validates requests, rejects partial OUT reads on DMA endpoints, maps DMA buffers, initializes request progress, and immediately starts DMA or PIO if the endpoint is idle. EP0 queueing has special handling for pending setup requests, zero-length data/status stages, and `SET_CONFIGURATION` timing.

The general IRQ first handles device-state changes, then EP0 setup/data/status traffic, then DMA completion. `devstate_irq()` reacts to attach, disconnect, USB reset, suspend/resume, and OTG flag changes, notifying gadget callbacks outside the lock where needed. `ep0_irq()` handles SETUP by reading four 16-bit words, locally processing selected SET/CLEAR_FEATURE and GET_STATUS cases that gadget drivers do not see cleanly, updating configuration state early for SET_CONFIGURATION, and delegating most requests to the gadget driver's setup callback. The PIO IRQ services non-ISO IN/OUT endpoints, while the ISO IRQ walks the ISO list on SOF and services queued non-DMA ISO requests.

## State and Persistence Behavior

State is in-memory and register-backed only. `struct omap_udc` stores gadget state, the bound driver, spinlock, 32 endpoint slots split by endpoint number and direction, last device status, clear-halt command bits, optional transceiver, ISO endpoint list, softconnect/VBUS/EP0 flags, remove completion, OMAP clocks, and clock-request state. `struct omap_ep` stores the preconfigured endpoint name/address/type, request queue, ISO list node, maxpacket, double-buffer flag, stopped/FIFO flags, DMA assignment, IRQ count, and a timer used to recover from lost PIO OUT IRQs. `struct omap_req` stores request queue linkage, DMA byte count, and mapped state.

The driver does not persist data to disk. Module parameters `fifo_mode` and `use_dma` are boot/module-time policy. Hardware-visible state includes endpoint FIFO allocation registers, `UDC_SYSCON1/2`, IRQ enable/source registers, DMA channel configuration, VBUS/pullup state, OTG controller bits, and PHY power/suspend state. The global `udc` pointer means the driver is structured around a single controller instance.

## Dependencies and Integration Points

The file depends on the USB gadget core, USB OTG and PHY APIs, OMAP DMA APIs, OMAP1 platform data, OMAP1 SoC/USB/IO helpers, clock APIs, procfs/seq_file debug support, platform-driver resource management, and machine-type helpers for boards without VBUS sensing. It integrates with board/platform data through `struct omap_usb_config`, platform resources ordered as memory plus IRQs, HMC mode registers, external transceiver registration, and OMAP16xx device/host clock names `usb_dc_ck` and `usb_hhc_ck`.

Upward integration with gadget drivers is through the UDC gadget and endpoint APIs. Downward integration is direct 16-bit/32-bit access to UDC, OTG, ULPD, and OMAP DMA registers, with special handling for OMAP15xx versus OMAP16xx/1710 differences.

## Risks and Test Signals

High-risk areas include the single global controller pointer, endpoint configuration before enumeration, lock dropping around gadget callbacks, DMA channel release/reclaim side effects, and PIO OUT lost-IRQ recovery. `omap_ep_queue()` and `ep0_irq()` coordinate EP0 pending/setup/configuration flags closely; regressions can stall enumeration or allow non-control endpoints to run before configuration state is stable. DMA OUT rejects partial-packet reads, and DMA cancellation uses channel release/reclaim as a request-cancel mechanism, both of which can surprise gadget functions.

Hardware-specific risk is high around OMAP15xx versus OMAP16xx behavior: double buffering is disabled on 15xx, DMA position accounting differs, HMC and VBUS controls differ, and board variants without VBUS sensing keep the 48 MHz clock behavior different from normal boards. ISO support is compiled in but has limited error reporting; comments show places where ISO frame errors are detected but not completed to the gadget driver.

Useful test signals include probe/remove with valid and invalid HMC modes, all supported `fifo_mode` layouts, gadget bind/unbind, VBUS session on/off with and without external PHY, boards without VBUS sense, pullup toggling, full-speed enumeration, EP0 SET_CONFIGURATION success and failure, standard endpoint halt set/clear/get-status cases, delegated class/vendor setup requests, PIO bulk/interrupt IN and OUT, PIO OUT timer recovery, DMA bulk IN/OUT including multi-transfer requests and dequeue of an active DMA request, partial OUT DMA rejection, ISO IN/OUT SOF servicing, suspend/resume with active sessions, remote wakeup/SRP, `/proc/driver/udc` debug output, and clock enable/disable balance on OMAP16xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.h

## Purpose

`omap_udc.h` is the private register and state header for the OMAP full-speed USB device controller driver. It defines the UDC register offsets, bit fields for endpoint selection/control/status, device status, IRQ and DMA control, endpoint RX/TX FIFO configuration, private request/endpoint/controller structures, debug macros, and OMAP1 VBUS/HMC helper macros used by `omap_udc.c`.

## Important APIs, Types, and Functions

The header maps controller registers such as `UDC_EP_NUM`, `UDC_DATA`, `UDC_CTRL`, `UDC_STAT_FLG`, `UDC_SYSCON1`, `UDC_SYSCON2`, `UDC_DEVSTAT`, `UDC_IRQ_EN`, `UDC_DMA_IRQ_EN`, `UDC_IRQ_SRC`, `UDC_EPN_STAT`, `UDC_DMAN_STAT`, `UDC_RXDMA_CFG`, `UDC_TXDMA_CFG`, `UDC_TXDMA(chan)`, `UDC_RXDMA(chan)`, `UDC_EP_RX(endpoint)`, and `UDC_EP_TX(endpoint)`. Their bit definitions express endpoint selection, FIFO enable/clear/halt/toggle, ACK/NAK/stall/FIFO status, device attach/reset/suspend/configuration state, endpoint and DMA IRQ bits, and FIFO buffer configuration.

`struct omap_req` wraps `struct usb_request` with queue linkage, current DMA segment byte count, and a mapped flag. `struct omap_ep` wraps `struct usb_ep` with queue/list state, endpoint name, hardware maxpacket/address/type, double-buffer and stopped flags, FIFO/ACK tracking, DMA channel and logical channel IDs, DMA counter, back-pointer to `struct omap_udc`, and the PIO OUT recovery timer. `struct omap_udc` wraps `struct usb_gadget` with the bound driver, spinlock, 32 endpoint slots, device status, clear-halt command, transceiver pointer, ISO list, softconnect/VBUS/EP0 flags, remove completion, clocks, and clock-request state.

Debug macros `ERR`, `WARNING`, `INFO`, `DBG`, and optional `VDBG` standardize logging. VBUS/HMC macros (`VBUS_W2FC_1510`, `VBUS_CTRL_1510`, `VBUS_MODE_1510`, `HMC_1510`, `HMC_1610`, `HMC`) abstract board and SoC register differences used during probe and VBUS handling.

## Control Flow

This header has no standalone execution, but it defines the register contract used by every path in `omap_udc.c`. `use_ep()` selects endpoints by writing `UDC_EP_NUM`, PIO reads and writes use `UDC_DATA`, endpoint operations use `UDC_CTRL` and `UDC_STAT_FLG`, EP0 and state IRQs use `UDC_IRQ_SRC`, and DMA paths program `UDC_RXDMA_CFG`, `UDC_TXDMA_CFG`, and per-channel DMA control registers. Probe-time endpoint layout uses `UDC_EP_RX()` and `UDC_EP_TX()` before `UDC_CFG_LOCK` is set.

The structure layout also dictates runtime lookup: OUT endpoints occupy `udc->ep[endpoint_number]`, IN endpoints occupy `udc->ep[16 + endpoint_number]`, and EP0 is `udc->ep[0]`. That convention is used by request queueing, IRQ decoding, DMA completion, and setup request endpoint-halt handling.

## State and Persistence Behavior

All state is runtime-only. Register definitions describe volatile hardware state; structure fields describe in-memory state for the currently registered platform device. The header does not define persistent storage. State visible outside the driver is reflected through USB gadget registration, USB bus attach/configuration state, endpoint FIFOs, DMA programming, clocks, PHY/OTG state, and optional proc debug output.

The fixed-size `ep[32]` array is a notable state convention: it supports 16 endpoint numbers in each direction by offsetting IN endpoints by 16. Endpoint names are bounded to 14 bytes, and FIFO allocation assumes the controller's 2 KiB packet RAM.

## Dependencies and Integration Points

The header assumes OMAP-specific symbols such as `UDC_BASE`, `MOD_CONF_CTRL_0`, `OTG_SYSCON_2`, `omap_readl()`, and CPU/machine helpers are available through the source file's OMAP includes. It integrates local driver state with the USB gadget API, Linux timers and lists, USB PHY/OTG types, clocks, completions, and OMAP1 platform/SoC register access.

## Risks and Test Signals

Risks include incorrect register-bit definitions, endpoint direction index mistakes in the split `ep[32]` array, FIFO allocation overflow beyond 2 KiB, endpoint name truncation, and mismatched `UDC_CLR_HALT` behavior across UDC revisions. DMA channel macros number channels 1-3, so off-by-one mistakes can corrupt DMA IRQ enables or endpoint/channel routing.

Useful test signals include compile coverage on OMAP15xx and OMAP16xx configurations, probe-time register programming for every `fifo_mode`, endpoint lookup for IN and OUT endpoint numbers, DMA IRQ enable/disable bit calculations for channels 1-3, EP0 and non-EP0 halt/clear paths, device-status change decoding, VBUS/HMC detection on supported boards, and proc/debug output matching actual endpoint/register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.h -->
