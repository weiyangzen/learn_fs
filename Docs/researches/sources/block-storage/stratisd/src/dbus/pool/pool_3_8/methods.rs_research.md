# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/methods.rs

Purpose: Implements token-slot aware r8 encryption methods.

Methods:
- `bind_clevis_method`
- `bind_keyring_method`
- `rebind_clevis_method`
- `rebind_keyring_method`
- `unbind_clevis_method`
- `unbind_keyring_method`

Key behavior:
- Accepts optional token-slot tuples for bind/rebind/unbind operations.
- For omitted token slots, chooses `Legacy` for metadata version V1 and `None` for metadata version V2.
- Tracks free token slots before and after modifications.
- Tracks the lowest legacy token slot and whether encryption info is the newer per-token representation.
- Emits Clevis/keyring property signals only when the externally visible property should change.
- Emits free-token-slots signals when token slot availability changes.

Failure handling:
- Bad Clevis JSON, missing pool, engine errors, and task join errors convert to D-Bus error tuples.
- Rebinding keyring with no source returns a specific D-Bus error string.
