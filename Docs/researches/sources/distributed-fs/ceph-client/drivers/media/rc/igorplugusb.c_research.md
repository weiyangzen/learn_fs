<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c

Purpose: USB raw IR receiver driver for IgorPlugUSB-compatible devices. It polls a vendor control endpoint, decodes the device's small pulse/space buffer, and feeds rc-core raw IR decoders.

Important APIs and functions: `struct igorplugusb` stores the rc device, USB control URB/request, polling timer, input buffer, and physical path. Core functions are `igorplugusb_cmd`, `igorplugusb_timer`, `igorplugusb_callback`, `igorplugusb_irdata`, `igorplugusb_probe`, and `igorplugusb_disconnect`.

Control flow: probe validates a single control-IN endpoint, allocates request/URB/buffer, initializes a polling timer, builds a vendor IN control request, allocates and registers an `RC_DRIVER_IR_RAW` device with limited allowed protocols, stores driver data, and sends `SET_INFRABUFFER_EMPTY`. Timer callbacks submit `GET_INFRACODE`. URB completion either decodes received IR data, schedules the next poll after 50 ms, or clears the hardware buffer after errors. Decoding handles circular overwrite indicated by the overflow byte, converts byte samples to 85-us pulse/space durations, adds a trailing timeout space, and calls `ir_raw_event_handle`.

State and persistence: runtime state is the URB, timer, buffer, and rc-core device. Device firmware buffer is explicitly cleared after reads or errors. No settings are persisted.

Dependencies and integration points: depends on USB core/control URBs, timers, and rc-core raw APIs. USB IDs include Atmel `03eb:0002` and Fit PC2 `03eb:21fe`; default keymap is Hauppauge.

Risks: hardware stores only 36 pulses/spaces, so long protocols are disabled and overflow loses data. Polling every 50 ms can miss bursts if the device overwrites its buffer repeatedly. Error cleanup must coordinate poisoned URBs and timer deletion; the code uses poison/unpoison around teardown.

Test signals: USB probe for both IDs, polling cadence, overflow handling, raw event durations at 85-us resolution, disabled protocol mask behavior, disconnect during active polling, and error URB statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c -->
