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
