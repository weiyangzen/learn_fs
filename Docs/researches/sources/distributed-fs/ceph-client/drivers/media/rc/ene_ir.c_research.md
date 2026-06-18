<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c

Purpose: PNP driver for ENE KB3926-series consumer IR receivers/transceivers. It directly programs ENE embedded-controller registers to receive raw IR samples, optionally detect carrier/learning input, transmit IR, and support wake from suspend.

Important APIs and functions: module parameters are `sample_period`, `learning_mode_force`, `debug`, and `txsim`. Register helpers are `ene_read_reg`, `ene_write_reg`, mask helpers, and `ene_hw_detect`. RX paths include buffer setup/restoration, pointer tracking, carrier sensing, input selection, `ene_rx_setup`, enable/disable/reset, and ISR sample extraction. TX paths include carrier/transmitter setup, `ene_tx_enable`, `ene_tx_sample`, simulated TX timer, and `ene_transmit`. rc-core callbacks include open/close, `s_idle`, wideband receiver, carrier report, TX mask/carrier/duty, and transmit. Lifecycle is `ene_probe`, `ene_remove`, suspend/resume/shutdown.

Control flow: probe validates PNP I/O and IRQ resources, detects hardware revision/features and firmware buffer layout, sets default RX/TX settings, configures hardware, registers an rc raw device, requests I/O region and shared IRQ. Open enables RX firmware/IRQ and input path. ISR acknowledges ENE IRQ status, feeds TX samples on TX interrupts, reads RX ring-buffer samples, converts space/pulse duration using sample period or fan-input resolution, reports optional carrier events, and calls `ir_raw_event_handle`. TX primes two hardware output slots, then interrupt/timer callbacks continue feeding chunks until completion or timeout.

State and persistence: `struct ene_device` tracks PNP resources, hardware feature flags, ring-buffer addresses and pointers, saved config register, TX buffer/progress/completion/timer, TX carrier/duty/mask, RX learning/carrier/period state, and whether RX is enabled. Hardware register configuration is reuploaded on resume and restored on remove where extra firmware buffers were modified.

Dependencies and integration points: depends on PNP, I/O port access, shared IRQs, timers/completions, spinlocks, and rc-core raw IR APIs. Header `ene_ir.h` provides register map and state structure. It integrates with wakeup-capable PNP devices matching `ENE0100`, `ENE0200`, `ENE0201`, and `ENE0202`.

Risks: heavy direct hardware manipulation under spinlocks makes register ordering important. Probe registers the rc device before requesting I/O/IRQ, so error paths must unregister carefully. `txsim` can force TX capability on unsupported hardware and is explicitly dangerous. Carrier/duty setting uses `BUG_ON` for invalid duty values inside carrier programming. Extra-buffer validation failures degrade to legacy buffering and may reduce RX reliability.

Test signals: PNP probe on B/C/D revisions, RX sample decoding with and without extra buffers/fan input, learning mode and carrier reports, TX mask/carrier/duty/transmit completion, suspend/resume wake behavior, shutdown wake enable, and stress tests for ISR ring-buffer wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c -->
