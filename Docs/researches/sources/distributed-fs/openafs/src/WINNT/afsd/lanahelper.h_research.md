# sources/distributed-fs/openafs/src/WINNT/afsd/lanahelper.h

Purpose: declares the C-callable LANA/NetBIOS helper interface implemented by `lanahelper.cpp`.

Important APIs/types/functions: defines `lana_number_t`, `struct LANAINFO`, invalid value `LANA_INVALID`, maximum NetBIOS name length, and flags `LANA_NETBIOS_NAME_SUFFIX`, `LANA_NETBIOS_NAME_FULL`, `LANA_NETBIOS_NAME_IN`, and `LANA_NETBIOS_NO_RESET`. Exports GUID-name lookup, LANA discovery, loopback checks, UNC server-name generation, and display-string helpers.

Control flow: callers can either use high-level `lana_GetUncServerName`/`lana_GetNetbiosName` or perform explicit discovery with `lana_FindLanaByName`, `lana_FindLoopback`, and `lana_IsLoopback` before passing selected values to `lana_GetUncServerNameEx`.

State/persistence: no state in the header. Ownership is implicit: `lana_GetNameFromGuid` may allocate `*Name`, and `lana_FindLanaByName` returns an allocated array terminated by `LANA_INVALID`.

Dependencies/integration: includes Windows and TCHAR headers and uses `extern "C"` for C/C++ ABI compatibility. Used by AFSD SMB setup and Windows configuration/display components.

Risks: ownership and buffer-size requirements are not encoded in the function signatures. `lana_GetUncServerNameEx` assumes the output buffer can hold at least `MAX_NB_NAME_LENGTH` bytes/chars depending on caller context.

Test signals: compile from both C and C++ consumers, verify Unicode and ANSI builds, and test allocation/free conventions for discovery functions.
