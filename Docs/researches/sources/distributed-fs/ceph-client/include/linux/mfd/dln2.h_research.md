# sources/distributed-fs/ceph-client/include/linux/mfd/dln2.h

Purpose: This header defines the shared interface for Diolan DLN-2 USB MFD subdrivers. It gives subdrivers a command encoding macro, per-subdevice platform data, event callback registration, and synchronous command transfer helpers.

Important APIs, types, and functions: `DLN2_CMD(cmd, id)` combines a command opcode with a module ID. `struct dln2_platform_data` carries the internal subdriver handle and port number. `dln2_event_cb_t` is an interrupt-context callback receiving the platform device, echo, payload pointer, and payload length. Exported functions are `dln2_register_event_cb`, `dln2_unregister_event_cb`, and `dln2_transfer`. Inline helpers `dln2_transfer_rx` and `dln2_transfer_tx` specialize transfers with only receive or transmit payloads.

Control flow, state, and persistence: Subdrivers register callbacks for DLN-2 events, issue command transfers through the parent USB transport, and receive event payloads in interrupt context. State is held by the parent driver, command handles, pending transfers, callback registrations, and per-port platform data; the payload pointer is explicitly valid only for the callback duration.

Dependencies and integration points: It integrates with platform-device MFD children for I2C, SPI, GPIO, and other DLN-2 functions. The implementation depends on the DLN-2 USB transport and parent event demultiplexer.

Risks and test signals: Risks include sleeping or doing heavy work in event callbacks, using the event data after return, not initializing `ibuf_len` before `dln2_transfer`, and command ID collisions. Test signals include USB disconnect during transfer, callback registration/unregistration races, oversized payload handling, per-port command routing, and interrupt-context lockdep coverage.
