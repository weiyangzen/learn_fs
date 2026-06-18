# File Research: sources/block-storage/stratisd/src/engine/types/keys.rs

## Purpose

Defines encryption, unlock, token-slot, and key-description data structures used by Stratis pool encryption metadata and unlock operations.

## Main Types and Behavior

- `SizedKeyMemory` wraps `libcryptsetup_rs::SafeMemHandle` with an explicit size and exposes only the active byte slice.
- `UnlockMechanism` is either `KeyDesc(KeyDescription)` or `ClevisInfo(ClevisInfo)`, with accessors and type predicates.
- `InputEncryptionInfo` stores user-supplied encryption/unlock mechanisms with optional token slots. It supports legacy fixed-token construction, validation against duplicate explicit token slots, and conversion into grouped parts.
- `EncryptionInfo` stores actual token-slot-to-unlock-mechanism mappings. It supports adding, setting, removing, listing, finding free slots, counting free token slots, diffing token-slot presence, JSON conversion, and display formatting.
- `PoolEncryptionInfo` summarizes key/Clevis encryption information across pool devices, preserving inconsistency using `MaybeInconsistent`.
- `KeyDescription` validates kernel keyring descriptions by rejecting semicolons, because semicolons conflict with kernel describe-string parsing.
- `VolumeKeyKeyDescription` reserves a key description namespace for pool volume keys.
- `UnlockMethod`, `OptionalTokenSlotInput`, and `TokenUnlockMethod` model legacy unlock choices, optional explicit token slot assignment, and unlock token selection.

## Integration Points

This file bridges CLI/API encryption arguments, on-disk metadata compatibility, libcryptsetup token slots, pool encryption state, and keyring/Clevis unlock flows. JSON-RPC client/server pool methods pass `InputEncryptionInfo`, `OptionalTokenSlotInput`, `TokenUnlockMethod`, and `KeyDescription`.

## Notable Semantics

Legacy metadata requires fixed token slots for keyring and Clevis. Newer paths allow optional or explicit slots. `PoolEncryptionInfo::from` over multiple `EncryptionInfo` values marks fields inconsistent when devices disagree, preventing callers from silently treating mixed metadata as authoritative.
