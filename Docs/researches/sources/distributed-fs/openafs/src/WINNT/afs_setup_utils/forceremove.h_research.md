# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.h

Purpose: public C/C++ header for the forced legacy-client removal helper.

Important APIs/types/functions: declares `DWORD Client34Eradicate(BOOL keepConfig)` inside `extern "C"` guards and protects inclusion with `AFS_FORCEREMOVE_H`.

Control flow: callers invoke the single exported removal routine; implementation handles all sequencing.

State/persistence: no header state. The implementation mutates services, registry, filesystem, PATH, and provider order.

Dependencies/integration: depends on Windows `DWORD` and `BOOL` types being defined before inclusion. Used by setup DLL and `afsrm.c`.

Risks/test signals: consumers need to interpret Win32 error codes, not Boolean success. Compile tests should verify C and C++ linkage and inclusion order.
