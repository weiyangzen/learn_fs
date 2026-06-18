# sources/distributed-fs/ceph-client/drivers/media/rc/rc-core-priv.h

Purpose: private rc-core header that connects the public `media/rc-core.h` API to internal raw IR decoding, LIRC, and BPF support. It defines raw handler/client state and shared helpers used by decoders, encoders, `rc-main.c`, and `rc-ir-raw.c`.

Important APIs and types: exported internal lifecycle declarations include `rc_open`, `rc_close`, `ir_raw_event_prepare/register/unregister/free`, `ir_raw_handler_register/unregister`, `ir_raw_load_modules`, and `ir_raw_init`. `struct ir_raw_handler` describes decoder/encoder modules, protocol bitmask, carrier, timeout, and optional per-device registration hooks. `struct ir_raw_event_ctrl` owns each raw device FIFO, worker thread, edge timer, last event timestamp, decoder state structs for configured protocol decoders, and optional BPF program array.

Control flow: rc-core allocates `ir_raw_event_ctrl` for raw devices, decoder modules register `ir_raw_handler` entries, and `rc-ir-raw.c` uses the shared helpers to queue, decode, encode, and tear down raw events. Inline helpers implement timing comparisons, transition checks, duration reduction, normal-event classification, and raw event construction.

State and persistence: state is in-memory only. The `ir_raw_event_ctrl` FIFO buffers up to `MAX_IR_EVENT_SIZE` pulse/space transitions per raw device. Protocol decoder substates persist only while the rc device and decoder modules remain registered. LIRC and BPF members are compiled in conditionally and have no on-disk persistence.

Dependencies and integration points: depends on Linux slab allocation, UAPI BPF declarations, and public rc-core types. It is the internal integration point between rc-core, raw IR protocol decoder modules, LIRC character-device support, and optional BPF LIRC mode2 filters.

Risks and edge cases: the header exposes many private fields to decoder implementations, so structure changes can break multiple modules. Timing helpers use unsigned arithmetic and assume margins smaller than target durations. Conditional decoder state means build configuration changes alter `struct ir_raw_event_ctrl` layout. Stubbed LIRC/BPF functions hide feature absence from callers, so tests must cover both enabled and disabled configs.

Test signals: allmodconfig and minimal-config builds, raw decoder module load/unload, LIRC enabled/disabled builds, BPF_LIRC enabled builds, FIFO overflow behavior, protocol encoder helper tests, and raw handler registration under active devices.
