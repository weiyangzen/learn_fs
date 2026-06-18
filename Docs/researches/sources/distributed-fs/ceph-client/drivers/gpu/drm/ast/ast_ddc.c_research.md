## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.c

Purpose: bit-banged I2C/DDC adapter for AST analog output EDID reads.

Important type is `struct ast_ddc`, containing the `ast_device`, `i2c_algo_bit_data`, and `i2c_adapter`. Important functions are SDA/SCL setters/getters, pre/post transfer lock hooks, `ast_ddc_release`, and `ast_ddc_create`.

Control flow: adapter creation allocates DRM-managed state, fills bit-banging callbacks, registers an I2C adapter, and attaches a managed cleanup action. Transfers lock `ast->modeset_lock` so DDC indexed-register access cannot race modeset register programming. SDA/SCL setters write inverted bits into VGACR B7 and poll until latched; getters sample repeatedly until five stable reads or a large retry limit.

State persists in the I2C adapter registration and transiently in VGACR B7 pin-control bits. Dependencies are `i2c-algo-bit`, DRM managed allocation/actions, AST indexed register helpers, and the mode lock. Risks include long polling loops on stuck pins, inverted signal semantics, possible EDID read latency due to 20 us bit delay and 2200 us timeout, and shared register contention if callers bypass the lock. Test signals are adapter registration, EDID read success on VGA, correct cleanup on device removal, and no modeset/DDC races under hotplug polling.
