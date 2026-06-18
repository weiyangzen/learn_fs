# sources/distributed-fs/ceph-client/drivers/media/rc/rc-loopback.c

Purpose: provides a virtual rc-core loopback device for debugging. It accepts transmitted raw IR durations through rc-core TX callbacks and feeds them back into the raw receive pipeline without physical hardware.

Important APIs and functions: `struct loopback_dev` stores loopback configuration. rc-core callbacks include `loop_set_tx_mask`, `loop_set_tx_carrier`, `loop_set_tx_duty_cycle`, `loop_set_rx_carrier_range`, `loop_tx_ir`, `loop_set_idle`, `loop_set_wideband_receiver`, `loop_set_carrier_report`, and `loop_set_wakeup_filter`. Module lifecycle is `loop_init` and `loop_exit`.

Control flow: module init allocates an `RC_DRIVER_IR_RAW` device with both RX and TX capabilities, all IR decoder protocols, all encoder wake protocols, timeout/filter callbacks, and default carrier/mask values. `loop_tx_ir` rejects delivery when TX carrier or mask is incompatible with current RX settings; otherwise it converts alternating TX durations into raw pulse/space events, optionally emits carrier reports, appends a timeout-length silence, and wakes raw decoders. Wakeup filter setting encodes the requested wake scancode as raw IR and loops it back into the receiver.

State and persistence: a single static `loopdev` holds the virtual device and settings. State persists only while the module is loaded. No hardware or filesystem persistence is involved.

Dependencies and integration points: depends on rc-core raw RX/TX APIs and the protocol encoder registry. It integrates with sysfs/LIRC test workflows, carrier-report paths, wakeup filter encoding, and raw decoder modules.

Risks and edge cases: `loop_set_tx_mask` returns `2` for invalid masks rather than a negative errno, which is unusual. Carrier, mask, and wideband settings are not locked independently, relying on rc-core callback serialization. The overflow simulation only triggers for pulses longer than 50 ms. Wake filter loopback accepts partial encodings on `-ENOBUFS`, which is useful for debugging but can surprise strict tests.

Test signals: module load creates one `rc` device, `ir-ctl` transmit loops into decoders, carrier range and mask mismatch suppress events, carrier report emission, wakeup filter encoding through sysfs, overflow simulation with long pulses, and module unload cleanup.
