# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.h

Purpose: public header for setup utility functions that manipulate provider order and system environment.

Important APIs/types/functions: declares provider order helpers, system environment read/write helpers, PATH add/remove helpers, and `IsWinNT()` inside `extern "C"` guards with include guard `AFS_SUTIL_H`.

Control flow: callers use these as Boolean-returning utility operations; implementation chooses registry or autoexec behavior.

State/persistence: no header state. Implementations persist registry or autoexec changes.

Dependencies/integration: requires Windows `BOOL` and C string types. Used by setup DLL and forced removal code.

Risks/test signals: APIs return only `BOOL`, losing specific Win32 error details. Compile tests should verify C/C++ consumers and inclusion order.
