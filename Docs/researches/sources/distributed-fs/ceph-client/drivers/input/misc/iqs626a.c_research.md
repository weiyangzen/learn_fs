# sources/distributed-fs/ceph-client/drivers/input/misc/iqs626a.c

Purpose: I2C input driver for Azoteq IQS626A, exposing a keypad-style device for capacitive/inductive/Hall events and an optional trackpad device for coordinates or gesture keycodes.

Important APIs/types/functions: `struct iqs626_private` owns the client, regmap, cached `struct iqs626_sys_reg`, ATI completion, keypad/trackpad devices, touchscreen properties, configured key maps, gesture codes, and suspend mode. Packed register structs mirror the device layout. Descriptor tables `iqs626_events[]` and `iqs626_channels[]` drive validation and reporting. Key routines are `iqs626_parse_prop`, `iqs626_parse_channel`, `iqs626_parse_events`, `iqs626_parse_trackpad`, `iqs626_input_init`, `iqs626_report`, IRQ handling, probe, suspend, and resume.

Control flow: probe allocates state, initializes regmap, validates product `0x51`, reads the system register block, folds firmware-node properties into the cached register image, writes it back, creates input devices, requests IRQ, waits for ATI completion, then registers the keypad. IRQ reads flags, restores cached configuration after SHOW_RESET, ignores active ATI, derives Hall direction from differential output, reports configured key/switch events, completes ATI, and reports trackpad coordinates or momentary gestures.

State/persistence: no durable storage. The cached `sys_reg` is runtime-authoritative and replayed after self-reset. `ati_done` gates initial keypad registration. Suspend/resume optionally force device power modes by disabling IRQs, updating power-mode bits, and polling completion.

Dependencies/integration: I2C, regmap, OF compatible `azoteq,iqs626a`, child firmware nodes for channels, input, touchscreen helpers, and RDY IRQ timing delays.

Risks: register packing and property bounds are the main regression surface. Trackpad coordinate-versus-gesture mode depends on event-mask semantics. IRQ read failures return `IRQ_NONE`; reset recovery depends on a valid cached block.

Test signals: product mismatch, invalid properties, ATI timeout, reset replay, keypad/Hall events, trackpad ABS or gesture events, suspend/resume power transitions, and child-node coverage for all channel classes.
