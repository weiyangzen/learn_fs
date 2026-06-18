# Research: sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h

**Purpose:** Defines the Apple Silicon SMC core API used by child drivers to access firmware keys, register event handlers, and issue atomic shutdown/reboot writes.

**Important APIs and types:** `smc_key`, `SMC_KEY()` and helper key-packing macros encode FourCC keys. `struct apple_smc_key_info` describes key type, size, and flags. `struct apple_smc` stores key bounds, notifier chain, RTKit handle, SRAM/shared memory, command completions, mutex/spinlock, and atomic-mode state. Public functions cover read, write, read/write transaction, key lookup, key info, atomic entry, and atomic writes. `APPLE_SMC_TYPE_OPS()` generates typed helpers for integer types; flag helpers wrap u8 operations.

**Control flow:** Child drivers resolve or know a key, optionally verify it with `apple_smc_key_exists()`, then call the typed or raw accessors. Normal calls serialize through the mutex and completion. Atomic mode switches to the spinlock/pending path and disables normal operations for shutdown-critical writes.

**State and persistence:** Kernel state tracks SMC boot stage, key table limits, message ID, command completion, and atomic-mode flags. Durable state is firmware-held SMC key data, not filesystem state.

**Dependencies and integration:** Integrates with Apple RTKit, SRAM shared memory, Linux completions, mutexes, spinlocks, and blocking notifier chains. Consumers include hwmon, reboot/poweroff, input, and platform feature drivers.

**Risks:** Key endianness is central; using raw integers outside `SMC_KEY()` can silently address the wrong key. Typed helpers treat short positive reads as `-EINVAL`, so backend return lengths must be exact. Atomic mode intentionally blocks all non-atomic API use.

**Test signals:** Unit tests for key packing, typed helper length handling, read/write error propagation, key-index boundary behavior, notifier delivery, and atomic-mode rejection before `apple_smc_enter_atomic()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h -->
