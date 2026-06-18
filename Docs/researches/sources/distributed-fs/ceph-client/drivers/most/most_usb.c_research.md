# sources/distributed-fs/ceph-client/drivers/most/most_usb.c

## Purpose

`most_usb.c` is the USB hardware dependent module for MOST. It binds supported SMSC/Microchip USB INIC bridge devices, exposes each USB endpoint as a MOST channel, implements MBO enqueueing over bulk URBs, handles endpoint stall recovery, provides DMA allocation hooks, and optionally exposes a DCI sysfs device for direct register communication on newer INIC devices.

## Important APIs, Types, and Functions

`struct most_dev` is the per-USB-interface object. It embeds a `struct most_interface`, arrays of channel capabilities/configuration, endpoint addresses, per-channel spinlocks, health flags, padding flags, clear-halt work items, per-channel URB anchors, an I/O mutex, link-status timer/work, and an optional netinfo callback. `struct most_dci_obj` backs the sysfs `dci` child device and stores the USB device plus the arbitrary register address used by `arb_value`.

The MOST interface methods are `hdm_configure_channel`, `hdm_request_netinfo`, `hdm_enqueue`, `hdm_poison_channel`, `hdm_dma_alloc`, and `hdm_dma_free`. USB lifecycle entry points are `hdm_probe`, `hdm_disconnect`, `hdm_suspend`, and `hdm_resume` through `struct usb_driver hdm_usb`. URB completions are `hdm_write_completion` and `hdm_read_completion`. DCI helpers are `drci_rd_reg`, `drci_wr_reg`, `start_sync_ep`, `value_show`, and `value_store`.

## Control Flow

Probe allocates `most_dev`, derives the channel count from endpoint descriptors, initializes locks/timer/work, fills `most_interface` callbacks and identity fields, allocates channel arrays, and maps every endpoint to a `most_channel_capability`. Capabilities advertise control, async, isochronous, and synchronous data types with direction inferred from endpoint direction and maximum buffer/count constants. The interface is registered with MOST core. For selected OS81118/OS81119/OS81210 products, probe also registers a `dci` child device with sysfs attributes for read-only and writable DRCI registers.

Channel configuration validates buffer count and size, decides whether INIC USB padding is active, computes streaming frame size from `subbuffer_size`, `packets_per_xact`, and data type, may trim `buffer_size` to a whole number of frames, stores `extra_len` for RX padded transfers, initializes clear-halt work, and starts sync endpoints for async channels.

MBO enqueue allocates one URB, serializes against disconnect with `io_mutex`, optionally pads TX streaming buffers, chooses bulk send or receive pipe based on direction, uses coherent DMA via `URB_NO_TRANSFER_DMA_MAP`, anchors the URB in the channel anchor, and submits it. Completion updates MBO status and processed length under the channel spinlock, schedules clear-halt work on `-EPIPE`, reports close on `-ENODEV`/`-EPROTO`, removes RX padding when needed, invokes `mbo->complete`, and frees the URB.

## State and Persistence Behavior

State is entirely live kernel/device state. `mdev->conf` stores the last MOST channel configuration. `padding_active` and `is_channel_healthy` are per-channel runtime flags. Anchored URBs are the in-flight persistence boundary during normal operation; suspend, poison, disconnect, and clear-halt recovery kill anchors to return ownership to MOST core. The link status timer reschedules every two seconds once requested and invokes deferred work to read MAC/link registers and call `on_netinfo`.

Disconnect nulls `usb_device` under `io_mutex`, cancels timer/work, unregisters the DCI child if present, and deregisters the MOST interface; release callbacks free dynamically allocated arrays and device objects.

## Dependencies and Integration Points

The driver sits between Linux USB core and MOST core. It depends on `linux/usb.h` for device matching, control messages, URB handling, anchors, DMA-coherent buffers, suspend/resume, and sysfs device registration. It uses MOST channel types and MBO APIs from `linux/most.h`. DCI sysfs attributes issue vendor USB control transfers to INIC register addresses such as NI state, packet bandwidth, MEP filter/hash registers, EUI-48 registers, arbitrary address/value, and sync endpoint trigger.

## Risks and Edge Cases

The driver assumes endpoints are all bulk-style MOST pipes and caps channels at `MAX_NUM_ENDPOINTS`. Probe returns directly on `most_register_interface` failure without following the local error labels, leaving cleanup to device release only if the device was registered; this path should be reviewed if ownership rules change. `hdm_enqueue` uses `GFP_KERNEL` even though its comment says it could in some cases be interrupt context. Padding math depends on nonzero `subbuffer_size` and valid `packets_per_xact`; misconfiguration returns `-EINVAL` or adjusts buffer size.

URB completion treats `-ESHUTDOWN` as success, which is intentional for teardown but can mask actual transfer truncation during shutdown. Clear-halt recovery stops enqueueing, kills anchors, clears the failed pipe, may also clear the async TX peer for async RX stalls, marks the channel healthy, and resumes enqueueing; tests need to ensure no new URB is submitted on a poisoned channel during this window.

## Test Signals

Build tests require USB, MOST, and this HDM enabled. Runtime signals include probe logs for supported VID/PID pairs, `most_register_interface` success, channel capability enumeration matching endpoint descriptors, successful `configure` and `enqueue` for TX/RX, URB completion status propagation, DCI sysfs reads/writes returning expected register values, netinfo callbacks every two seconds after request, suspend/resume killing and resuming enqueue queues, and disconnect with no use-after-free. Fault-injection tests should cover `-EPIPE`, `-ENODEV`, padding misconfiguration, USB submit failure, and clear-halt recovery.
