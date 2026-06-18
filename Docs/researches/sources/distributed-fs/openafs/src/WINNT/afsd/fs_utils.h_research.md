# sources/distributed-fs/openafs/src/WINNT/afsd/fs_utils.h

Purpose: declares the Windows AFSD utility surface exported by `fs_utils.c` and related host utility functions. It gives command modules access to pioctl constants, PRSFS rights, NT error mappings, path helpers, AFS membership checks, command-line conversion, diagnostics, and mount-root globals.

Important APIs/types/functions: prototypes include `fs_utils_InitMountRoot`, `fs_StripDriveLetter`, `fs_ExtractDriveLetter`, `fs_GetFullPath`, `fs_GetParent`, `fs_InAFS`, `fs_IsFreelanceRoot`, `fs_NetbiosName`, `fs_IsAdmin`, `fs_MakeUtf8Cmdline`, `fs_FreeUtf8CmdLine`, `fs_Die`, `fs_filetypestr`, and `fs_SetProcessName`. It also declares `hostutil_GetNameByINet`, `hostutil_GetHostByName`, `util_GetInt32`, `NETBIOSNAMESZ`, and the global mount-root string pointers.

Control flow: consumers include this header to normalize user input before issuing pioctls and to present consistent diagnostics after failures. The duplicated `fs_utils_InitMountRoot` prototype is harmless but signals historical accretion.

State/persistence: exposes mutable process-global `cm_mount_root`, `cm_slash_mount_root`, and `cm_back_slash_mount_root`; callers must treat them as initialized by `fs_utils_InitMountRoot` and not as immutable compile-time constants.

Dependencies/integration: includes SMB ioctl constants, PRSFS rights, NT pioctl definitions, Winsock host types outside MFC, and OpenAFS NT errmap definitions. The header is a bridge between Windows command code and OpenAFS cache-manager APIs.

Risks: exported globals make initialization ordering important. Callers may assume returned strings are thread-safe or owned by the caller when some are static/global. The header lacks SAL or ownership annotations for buffers and returned argv storage.

Test signals: compile consumers with and without `_MFC_VER`, verify all command modules see pioctl/right constants, and test initialization before use of mount-root globals.
