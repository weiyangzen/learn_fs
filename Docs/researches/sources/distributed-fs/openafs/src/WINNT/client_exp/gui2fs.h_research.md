## sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.h

Purpose: Declares the GUI shell extension's callable AFS operation layer, turning Explorer and dialog commands into typed C++ functions.

Important APIs/types: Exposes file/cache operations, ACL operations, mount point/symlink operations, volume info setters/getters, server/cell/token lookup, path classification, owner/group lookup, and Unix mode bit access. The `WHICH_CELLS` enum controls server-status scope.

Control flow/state: The header has no runtime state; it defines the contract implemented in `gui2fs.cpp`. Default parameters decide whether path-sensitive queries follow mount points/symlinks.

Dependencies/integration: Requires `CVolInfo`, MFC `CString`/`CStringArray`, and Win32/MFC `BOOL`/`LONG` types. Included by shell extension command handlers and multiple dialogs.

Risks/tests: Any prototype mismatch breaks many Explorer commands. Compile tests should include all consumers, and behavioral tests should cover default `bFollow` values and multi-file array operations.
