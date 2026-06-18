# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.h

## Purpose
Declares dynamic-import constants and functions for the NetIDMgr AFS plugin, while temporarily raising `_WIN32_WINNT` to expose NT security APIs.

## Important APIs, Types, And Functions
Defines DLL names `SERVICE_DLL`, `SECUR32_DLL`, and `PSAPIDLL`, declares `AfsAvailable`, `init_imports()`, and `exit_imports()`, and includes delayed-load support headers.

## Control Flow
The preprocessor saves any lower `_WIN32_WINNT`, sets it to `0x0501` before including `ntsecapi.h`, then restores the previous value.

## State And Persistence
No persistent state; it exposes runtime import state through `AfsAvailable`.

## Dependencies And Integration Points
Used by `main.c`, `dynimport.c`, and Kerberos compatibility code. It depends on Windows headers, NetIDMgr `khdefs.h`, Toolhelp, and delay-load headers.

## Risks
Temporarily redefining `_WIN32_WINNT` can surprise include-order-sensitive builds. Consumers must call `init_imports()` before relying on delayed imports.

## Test Signals
Compile with multiple `_WIN32_WINNT` definitions and verify restored macro behavior; load plugin on supported Windows targets.
