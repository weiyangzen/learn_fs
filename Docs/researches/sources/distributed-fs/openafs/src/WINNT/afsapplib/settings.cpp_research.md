# sources/distributed-fs/openafs/src/WINNT/afsapplib/settings.cpp

## Purpose
Implements registry convenience functions for versioned binary settings, generic binary values, multi-string values, and recursive key deletion.

## Important APIs and Control Flow
`StoreSettings` allocates a buffer, prefixes the caller's structure with a `WORD` version, and stores it as `REG_BINARY`. `RestoreSettings` obtains the stored size, reads the full value, validates version compatibility by equal major byte and stored minor byte greater than or equal to expected minor, and copies only the expected structure size into the caller's buffer. `EraseSettings` deletes a named value.

`GetRegValueSize`, `GetBinaryRegValue`, and `SetBinaryRegValue` are generic wrappers around `RegOpenKey`/`RegCreateKey`, `RegQueryValueEx`, and `RegSetValueEx`. `GetMultiStringRegValue` loads `REG_MULTI_SZ` data into an allocated string buffer; `SetMultiStringRegValue` computes the double-NUL-terminated byte length and writes it. `RegDeltreeKey` recursively enumerates and deletes subkeys before deleting the requested key.

## State, Dependencies, and Integration
Persistence is the Windows registry under the parent key and base path selected by the caller. The file depends on Win32 registry APIs, `winerror.h`, `TaLocale.h` allocation helpers, and the version macros in `settings.h`. Callers own defaulting behavior when restore fails.

## Risks and Test Signals
Several functions close `hk` instead of `hkFinal` after opening or creating a subkey, which can leak the opened handle and accidentally close the caller-provided parent handle. `GetBinaryRegValue` does not validate that the registry type is `REG_BINARY`. `RestoreSettings` rejects stored data shorter than `sizeof(WORD)+cbStructure`, which conflicts with the header's claim that older/larger minor-version compatibility can ignore trailing fields. String copies and sizes assume trusted registry data. Tests should cover handle lifetime, major/minor restore rules, shorter and longer stored structures, registry type mismatches, multi-string round trips, and recursive deletion on nested trees.
