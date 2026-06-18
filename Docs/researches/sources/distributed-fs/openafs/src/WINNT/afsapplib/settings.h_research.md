# sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.h

## Purpose
Declares registry settings utilities and documents the versioning scheme for persistent binary application state. It is intended for simple global settings structs saved at shutdown and restored on startup.

## Important APIs and Types
The header defines convenience aliases for root registry hives (`HKCR`, `HKCU`, `HKLM`) and byte/version macros (`HIBYTE`, `LOBYTE`, `MAKEVERSION`) when absent. Public functions are `EraseSettings`, `RestoreSettings`, `StoreSettings`, `GetRegValueSize`, `GetBinaryRegValue`, `SetBinaryRegValue`, `GetMultiStringRegValue`, `SetMultiStringRegValue`, and `RegDeltreeKey`.

## State, Dependencies, and Integration
Callers provide a registry parent key, subkey path, value name, structure pointer, size, and version. The documented policy is major-version equality and stored minor-version compatibility for appended fields. Multi-string helpers allocate output buffers that callers must free through the afsapplib string allocator.

## Risks and Test Signals
The header contract strongly depends on append-only structure evolution, but the implementation's size check should be verified against that promise. API users must not store pointers or process-local handles inside persisted structs. Tests should assert version macro encoding, restore failure defaults, registry deletion behavior, and allocation/free ownership for multi-string values.
