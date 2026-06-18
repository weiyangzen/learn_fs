
# sources/distributed-fs/openafs/src/uss/uss_acl.h

Purpose: `uss_acl.h` declares the ACL and quota interface consumed by template actions, volume creation, and final account cleanup.

Important APIs: `uss_acl_SetAccess(char *a_access, int a_clear, int a_negative)` sets an ACL from a path plus user/right pairs, optionally clearing existing entries and optionally targeting the negative ACL list. `uss_acl_SetDiskQuota(char *a_path, int a_q)` updates the max quota of the volume mounted at `a_path`. `uss_acl_CleanUp(void)` restores final ACLs for directories chained in `uss_currentDir`.

Control flow and integration: the header is included by `uss_vol.c` and `uss_procs.c` to temporarily grant the account creator full control during setup, then by `uss.c` to call cleanup after template parsing. It intentionally hides the internal ACL list representation from callers.

State and persistence: no storage is defined here, but all functions operate on global `uss_common` state or persistent AFS metadata through `uss_fs`.

Risks and test signals: callers must format `a_access` exactly as expected; the type does not encode path/user/right boundaries. Tests should verify callers pass clear/negative flags correctly, especially final cleanup and volume-home creation.
