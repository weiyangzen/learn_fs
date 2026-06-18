# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr_version.h

## Purpose

`netidmgr_version.h` centralizes NetIDMgr version constants and Windows version-resource macros. It lets modules and resource scripts agree on product version, API version, compatibility floor, file type, and special NetIDMgr string-resource keys.

## Important APIs, types, and functions

The key macros are `KH_VERSION_MAJOR`, `KH_VERSION_MINOR`, `KH_VERSION_PATCH`, `KH_VERSION_AUX`, `KH_VERSION_API`, `KH_VERSION_API_MINCOMPAT`, `KH_VERSION_LIST`, and string forms such as `KH_VERSION_STRING` and `KH_VERSION_STRINGW`. Windows resource fields include `KH_VER_FILEFLAGMASK`, `KH_VER_FILEFLAGS`, `KH_VER_FILEOS`, `KH_VER_FILETYPEDLL`, and `KH_VER_FILETYPEAPP`. NetIDMgr metadata keys are `NIMV_MODULE`, `NIMV_PLUGINS`, `NIMV_APIVER`, and `NIMV_SUPPORT`.

## Control flow

The file has only preprocessor control flow via `__NETIDMGR_VERSION_H`. Version values are compile-time constants.

## State and persistence behavior

No runtime state is created. The constants become persistent only when embedded into binaries or resources, where they govern plugin/API compatibility checks and version display.

## Dependencies and integration points

It includes `windows.h` for version-resource constants such as `VOS_NT_WINDOWS32`, `VFT_DLL`, and `VFT_APP`. The AFS plugin uses NetIDMgr API compatibility in `afscred.h`; when `KH_VERSION_API < 7`, it loads older UI APIs dynamically.

## Risks and edge cases

Incorrect version constants can break plugin loading or cause resource metadata to advertise the wrong compatibility. The API minimum equals the API version here, which means consumers requiring older compatibility must update these constants deliberately.

## Test signals

Inspect built resource metadata, plugin load logs, and compatibility paths. Builds against API versions below 7 should exercise the dynamic function-pointer fallback declared in `afscred.h`.
