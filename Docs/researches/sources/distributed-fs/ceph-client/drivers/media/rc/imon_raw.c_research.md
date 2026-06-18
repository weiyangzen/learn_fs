# sources/distributed-fs/ceph-client/drivers/media/rc/imon_raw.c

Purpose: USB raw-IR driver for early SoundGraph iMON IR-only devices. It converts 8-byte interrupt packets into rc-core raw pulse/space events so generic software decoders can decode the remote protocols.

Important APIs, types, and functions: `struct imon` stores the device, interrupt URB, raw rc-core device, 64-bit receive buffer, and physical path. `imon_ir_data()` reads the big-endian packet, ignores `0xff` packet markers, treats the high 40 bits as 250 us bit samples where 1 means space and 0 means pulse, coalesces runs into `ir_raw_event` durations, and marks idle/handles events when packet number 10 arrives. `imon_ir_rx()` handles URB completion and resubmits. `imon_probe()` finds the interrupt IN endpoint, allocates URB/buffer and `RC_DRIVER_IR_RAW` device, sets `RC_MAP_IMON_RSC`, `rx_resolution = 250`, submits the URB, and stores interface data. `imon_disconnect()` kills/frees the URB and buffer.

Control flow: each interrupt packet triggers `imon_ir_rx()`, which calls `imon_ir_data()` on success and then resubmits the same URB. `imon_ir_data()` repeatedly finds the next transition boundary with `fls64()`, alternates pulse/space state, stores filtered raw events, and on the final packet pushes idle state and `ir_raw_event_handle()`.

State and persistence behavior: the only runtime state is the URB, receive buffer, rc-core raw device, and physical path. No key or protocol state is stored in this driver; generic rc-core raw decoders own protocol state.

Dependencies and integration points: depends on USB core, rc-core raw event APIs, and input ID helpers. It binds USB device `04e8:ff30` and exposes an rc-core raw receiver with all software IR decoders allowed.

Risks and edge cases: the packet format assumes ten packets per station transmission and only the first five bytes contain IR samples. Missing packet 10 can delay idle handling. The code allocates the buffer with plain `kmalloc()` and frees it on errors/disconnect; error paths must free both URB and buffer. `usb_unlink_urb()` inside completion for shutdown statuses is conservative but unusual.

Test signals: test with an early iMON Station, verify raw event durations are multiples of 250 us, confirm idle after packet 10, disconnect during active URB, and decode through generic protocols using `ir-keytable`.
