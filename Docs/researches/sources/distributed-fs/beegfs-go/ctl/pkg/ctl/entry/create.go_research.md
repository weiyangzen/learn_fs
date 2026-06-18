# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/create.go

Purpose: creates BeeGFS files and directories with explicit ownership, permissions, stripe pattern, storage pool, metadata placement, and Remote target configuration.

Important APIs/types/functions: `CreateEntryCfg`; `CreateFileCfg`; `CreateDirCfg`; `CreateEntryResult`; `generateAndVerifyMakeFileReq`; `checkPoolForPattern`; `checkAndGetTargets`; `generateAndVerifyMkDirRequest`; `CreateEntry`.

Control flow: `CreateEntry` validates paths, loads mappings and node store, sorts paths so parent directories can reuse a base request, initializes the BeeGFS client from the first parent, resolves each path relative to the mount, fetches parent entry info with original message, generates a base make-file or mkdir request when parent changes, sets the per-entry basename, sends the request to the parent metadata owner, and records response status and raw entry info. File request generation inherits parent stripe/RST config then applies user overrides and validates pool/targets/buddy groups. Directory request generation validates preferred meta nodes or buddy groups depending on parent mirroring.

State and persistence: creates files or directories on BeeGFS metadata servers and may configure RST IDs/cooldown on new files. No local persistence.

Dependencies and integration points: uses config BeeGFS client and node store, `GetEntry`, pool/mapping utilities, BeeMsg make-file/mkdir messages, filesystem unmounted error handling, and BeeGFS entity types.

Risks: base request objects are mutated per path by setting `NewFileName`/`NewDirName`; this is safe sequentially but not shareable. `checkAndGetTargets` returns IDs from a map, losing user-specified order, which may matter for stripe ordering. Error message for parent pool lookup formats `*userCfg.FileCfg.Pool` even when `Pool` is nil, which can panic on that error path. Unmounted mode proceeds only if BeeGFS client returns `ErrUnmounted`, but later path behavior depends on provider semantics.

Test signals: no direct tests. High-value tests would mock mappings/node store for file and dir request generation, pool validation, duplicate target detection, forced cross-pool targets, mirrored directory preferred-node lookup, nil pool error path, and path grouping by parent.
