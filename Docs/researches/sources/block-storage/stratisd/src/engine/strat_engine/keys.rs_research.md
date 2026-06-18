# File Research: sources/block-storage/stratisd/src/engine/strat_engine/keys.rs

This file implements Stratis kernel keyring operations.

Key responsibilities:
- Accesses the root persistent keyring and process keyring via raw `keyctl` syscalls.
- Searches, reads, adds, updates, lists, and unlinks Stratis keys.
- Stores key contents in `SafeMemHandle`/`SizedKeyMemory`.
- Implements the engine `KeyActions` trait as `StratKeyActions`.

Important behavior:
- Persistent keyring is attached to the session keyring via `KEYCTL_GET_PERSISTENT`.
- Process keyring creation uses `KEYCTL_GET_KEYRING_ID`.
- `set_key_idem()` is idempotent and returns `Created`, `ValueChanged`, or `Identity`.
- New/updated keys trigger notification over an unbounded channel so other processing can react.
- Key listing reads key IDs, describes each key, parses the key description after the final semicolon, and filters to Stratis descriptions.
- Key permissions are set with `KEYCTL_SETPERM` after key insertion.

Tests:
- Test-only `StratKeyActions::set_no_fd()` allows inserting in-memory keys without a file descriptor.
