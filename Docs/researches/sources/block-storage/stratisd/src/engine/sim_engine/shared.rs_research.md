# File Research: sources/block-storage/stratisd/src/engine/sim_engine/shared.rs

This file provides simulator-specific shared encryption conversion.

Function:
- `convert_encryption_info()`

Behavior:
- Converts optional `InputEncryptionInfo` into optional modern `EncryptionInfo`.
- Iterates each supplied unlock mechanism and token slot.
- Uses supplied token slot when present, otherwise chooses the next free token slot.
- For key-description mechanisms, optionally checks the simulated key handler to ensure the key exists.
- Adds each unlock mechanism into `EncryptionInfo`.
- Propagates token conflicts or missing-key errors.

Role in architecture:
- This helper lets `SimEngine` and `SimPool` share the same input-to-runtime encryption conversion logic while optionally enforcing simulated keyring presence.
