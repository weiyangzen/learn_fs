# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.h

Purpose: Declares the quota configuration persistence helper exported from `glusterd-quota.c`.

Important APIs and types: The only declaration is `glusterd_store_quota_config(glusterd_volinfo_t *volinfo, char *path, char *gfid_str, int opcode, char **op_errstr)`, which rewrites a volume's quota configuration file for enable, upgrade, limit, and remove operations.

Control flow: No executable control flow exists in the header. Callers use this API after validating quota operation context and, when required, resolving the GFID of the target path.

State and persistence: The declared function mutates `quota.conf`, quota configuration version, checksum, and associated store temp files for the supplied volume.

Dependencies and integration points: Depends on `glusterd_volinfo_t` being available from including context. It is an internal glusterd quota persistence contract used by quota operation code and potentially other volume-store paths.

Risks: The small header exposes a powerful persistence mutation API without wrapping the expected preconditions. Callers must pass valid opcode/path/GFID combinations and an initialized quota conf store handle.

Test signals: Compile coverage and quota operations that add/remove GFID records or upgrade `quota.conf` validate this declaration.
