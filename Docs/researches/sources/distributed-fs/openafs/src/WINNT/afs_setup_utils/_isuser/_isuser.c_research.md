# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/_isuser.c

Purpose: minimal InstallShield user DLL entry point.

Important APIs/types/functions: defines `NOCOMM`, includes `windows.h`, and implements `DllMain(PVOID hmod, ULONG ulReason, PCONTEXT pctx)` returning `TRUE` for all reasons.

Control flow: Windows loader calls `DllMain`; the function performs no initialization, cleanup, or reason dispatch and always allows load/unload.

State/persistence: no state and no persistence.

Dependencies/integration: generated/boilerplate InstallShield source, linked into setup support resources that use `_isuser/resource.h`.

Risks/test signals: no runtime logic to fail. Test signal is DLL load success under the expected InstallShield runtime and matching exported entry point signature for the toolchain.
