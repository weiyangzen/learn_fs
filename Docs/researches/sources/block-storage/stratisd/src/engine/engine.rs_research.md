# File Research: sources/block-storage/stratisd/src/engine/engine.rs

This file defines the central engine traits and contracts used by both the real Stratis engine and the simulator.

Constants:
- `DEV_PATH = "/dev/stratis"`.
- `MAX_STRATIS_PASS_SIZE = 64` bytes, the maximum pool passphrase size stored in the kernel keyring.

Traits:
- `KeyActions`:
  - abstract keyring operations: set, list, unset.
  - uses idempotent mapping actions to distinguish identity, creation, and value changes.
- `Report`:
  - exposes JSON reports for engine state and selected report types.
- `Filesystem`:
  - common filesystem view: devnode, creation time, mount path, used/size, size limit, origin, merge scheduling.
- `BlockDev`:
  - common block device view: devnode, metadata path, user/hardware info, initialization time, size/new size, metadata version.
- `Pool`:
  - the main pool behavior contract.
  - includes filesystem, blockdev, cache, encryption-token, metadata, grow, size, overprovisioning, merge, volume-key, and online encryption lifecycle APIs.
- `Engine`:
  - async top-level engine contract for pool creation/destruction/rename/unlock/start/stop, event handling, locking, reports, key handler access, and state refresh.
- `StateDiff` and `DumpState`:
  - generic state-diffing contracts for change detection.

Important `Pool` encryption lifecycle methods:
- `start_encrypt_pool()`
- `do_encrypt_pool()`
- `finish_encrypt_pool()`
- `start_reencrypt_pool()`
- `do_reencrypt_pool()`
- `finish_reencrypt_pool()`
- `decrypt_pool_idem_check()`
- `do_decrypt_pool()`
- `finish_decrypt_pool()`
- `last_reencrypt()`

Concurrency contract:
- `Engine::upgrade_pool()` explicitly supports operations that begin under one lock mode, run long work under another, then finalize with write access.

Role in architecture:
- This is the core abstraction boundary. D-Bus code, simulator code, and real engine code all meet at these traits, which define the behavior and idempotence semantics for Stratis operations.
