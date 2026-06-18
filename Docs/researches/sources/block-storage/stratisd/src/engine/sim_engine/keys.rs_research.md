# File Research: sources/block-storage/stratisd/src/engine/sim_engine/keys.rs

This file implements simulated keyring operations through `SimKeyActions`.

State:
- A `Mutex<HashMap<KeyDescription, Vec<u8>>>` stores key material in memory.

Internal behavior:
- `contains_key()` checks whether a key description exists.
- `read()` clones stored key bytes into `SafeMemHandle` and returns `SizedKeyMemory`.

`KeyActions` implementation:
- `set()`:
  - reads key material from a file descriptor using shared `read_key_shared()`;
  - returns identity when same key material already exists;
  - updates and returns value-changed when description exists with different bytes;
  - inserts and returns created when absent.
- `list()` returns all stored key descriptions.
- `unset()` removes a key or returns identity if absent.

Security/behavioral note:
- This is not a secure persistent keyring. It is a simulator implementation, but it still reuses the real passphrase size/FD reading logic to match engine behavior.

Role in architecture:
- Provides the simulator’s `KeyActions` implementation so encrypted pool creation can validate key descriptions without kernel keyring access.
