# sources/distributed-fs/openafs/src/WINNT/client_creds/settings.cpp

Purpose: generic registry-backed storage helpers for versioned binary settings and recursive key deletion.

Important APIs/functions: `RestoreSettings`, `StoreSettings`, `EraseSettings`, `GetBinaryRegValue`, `GetRegValueSize`, `SetBinaryRegValue`, and `RegDeltreeKey`.

Control flow: `StoreSettings` prepends a `WORD` version to a structure and writes it as `REG_BINARY`. `RestoreSettings` reads the stored blob, checks that major versions match and stored minor version is at least expected, then copies the expected structure bytes. `RegDeltreeKey` recursively deletes child keys before deleting the requested key.

State/persistence: directly reads/writes/deletes registry values beneath caller-provided roots and subkeys. Uses 64-bit registry view flags when `IsWow64()` indicates they are needed.

Dependencies/integration: uses OpenAFS allocation helpers, Win32 registry APIs, and version macros from `settings.h`.

Risks: `GetBinaryRegValue` calls `RegCloseKey(hk)` instead of `hkFinal`, which can close the caller's root handle and leak the opened subkey. It also does not verify `REG_BINARY`. Recursive delete can fail on permissions or open handles.

Test signals: store/restore across version combinations, invalid/truncated blobs, registry view selection, erase missing value, recursive delete trees, and handle-leak/regression tests around `GetBinaryRegValue`.
