# sources/distributed-fs/ceph-client/drivers/pcmcia/o2micro.h

Purpose: Provides O2Micro-specific PCI/ExCA register definitions and inline Yenta override helpers for read prefetch/write burst tuning.

Important APIs and functions: Defines O2Micro config registers such as `O2_MUX_CONTROL`, `O2_MODE_A` through `O2_MODE_E`, `O2_RESERVED1`, and `O2_RESERVED2`. `o2micro_override()` reads/writes reserved performance bits based on bridge device id and the `o2_speedup` parameter. `o2micro_restore_state()` reapplies the override after restore.

Control flow: For function 0, override reads 0x94 and 0xD4, defaults older bridge ids to speedup off and newer bridges on, allows `o2_speedup=on/off/default`, then sets or clears read-prefetch/write-burst bits in both registers.

State and persistence: State is in O2Micro bridge PCI config/ExCA registers. The helper has no owned data beyond using `struct yenta_socket` and the global parameter supplied by the including driver.

Dependencies and integration points: Depends on Yenta socket helpers such as `config_readb()` and `config_writeb()`, PCI device IDs, `o2_speedup`, and Linux device logging. It is included directly into the Yenta bridge implementation.

Risks: It writes reserved registers intentionally based on vendor guidance. Some old bridge/card combinations fail with speedups enabled, while others need them for performance or correctness. The global parameter parsing must remain compatible with module options.

Test signals: Yenta probe on O2Micro bridges across listed old and newer IDs, verify parameter overrides, suspend/resume restore, and card stability/performance with RME Hammerfall-like CardBus devices.
