# sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.c

## Purpose
Provides extended Windows registry helpers for OpenAFS installers/configuration tools. It opens canonical registry paths, reads values with optional allocation, enumerates subkeys into multistrings, recursively deletes keys, deletes named key/value entries, and duplicates entire registry key trees.

## Important APIs, Types, And Functions
Exported functions are `IsWow64`, `RegOpenKeyAlt`, `RegQueryValueAlt`, `RegEnumKeyAlt`, `RegDeleteKeyAlt`, `RegDeleteEntryAlt`, and `RegDupKeyAlt`. Private helpers `CopyKey`, `CopyValues`, and `CopySubkeys` implement recursive duplication. `IsWow64` dynamically resolves `IsWow64Process` and caches the result. `RegOpenKeyAlt` can parse a full path beginning with predefined key names such as `HKEY_LOCAL_MACHINE`, and on WoW64 adds `KEY_WOW64_64KEY` to access the 64-bit registry view.

## Control Flow
Open operations optionally create keys through `RegCreateKeyEx` or open existing keys through `RegOpenKeyEx`. Query operations either fill a caller-supplied buffer or first probe with a DWORD-sized read, allocate the required size, and read again when needed. Enumeration calls `RegQueryInfoKey` for count/name size, allocates one double-NUL-terminated multistring, and fills it with `RegEnumKeyEx`. Recursive delete first tries `RegDeleteKey`, falls back to enumerating/deleting children if needed, then retries the delete. Duplication deletes the target key, copies source values, and recursively copies subkeys.

## State And Persistence
All meaningful state is Windows registry state. The helper can create, delete, overwrite, and duplicate HKLM/HKCU/HKCR/HKU/etc. subtrees. Allocated buffers returned by query/enumeration must be freed by callers. The WoW64 detection result is cached in static variables.

## Dependencies And Integration Points
The file uses Win32 registry APIs, `windows.h`, `roken`, and constants/types from `afsreg.h`. It is used by `afssw.c`, `syscfg.c`, `vptab.c`, and the test tools to hide path parsing, allocation, recursive delete, and 64-bit registry view selection.

## Risks And Test Signals
This checkout shows a duplicated `RegDeleteKeyAlt(HKEY key,` declaration line before the real signature, which is a compile risk. Runtime risks include destructive recursive deletion, target replacement in `RegDupKeyAlt`, allocation-size assumptions for multistrings, path parsing that accepts prefix-length matches, and `FreeLibrary` being called on a module handle returned by `GetModuleHandle`. Test signals include building the library, duplicating/deleting nested test keys, reading DWORD/string/multistring values, and verifying 32-bit process behavior on 64-bit Windows.
