# sources/distributed-fs/ceph-client/include/linux/mtd/xip.h

Purpose: provides MTD execute-in-place support primitives for code paths that must keep servicing interrupts and timing delays while flash is temporarily not in array/read mode during writes or erases.

Important APIs and types: when `CONFIG_MTD_XIP` is enabled it includes architecture primitives from `asm/mtd-xip.h`. `__xipram` marks flash-state-changing functions for RAM placement under `CONFIG_XIP_KERNEL`; otherwise it compiles away. Required architecture macros are `xip_irqpending()`, `xip_currtime()`, `xip_elapsed_since(x)`, and `xip_iprefetch()`, with optional `xip_cpu_idle()`. Missing primitives degrade to zero/no-op definitions with compile-time warnings.

Control flow: flash algorithms that cannot execute from flash use `__xipram` and periodically call the architecture-provided IRQ/time/prefetch/idle hooks while waiting for hardware operations. If an architecture does not define the hooks, support compiles but responsiveness during flash write/erase is intentionally limited.

State and persistence: no persistent state is owned by this header. Runtime behavior is direct hardware polling and timing through architecture hooks while the underlying MTD device is outside normal read-array mode.

Dependencies and integration points: depends on compiler attributes and architecture-specific MTD XIP support. It connects generic MTD flash code, XIP-kernel placement, interrupt responsiveness, and platform timer/idle primitives.

Risks and test signals: risks include executing unavailable flash-resident code while flash is not readable, inaccurate elapsed-time conversions, overflow in platform timers, lost interrupt responsiveness when primitives are missing, and misplacing `__xipram` functions. Test with XIP kernel builds, flash erase/write under interrupt load, platforms with and without `xip_iprefetch()`/`xip_cpu_idle()`, and compile warnings for missing architecture hooks.
