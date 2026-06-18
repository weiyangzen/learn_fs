## sources/cloud-native/moby/daemon/builder/dockerfile/buildargs.go

**Purpose:** Tracks Dockerfile `ARG` values, meta args before `FROM`, user-supplied build args, referenced args, builtin proxy args, and warning behavior for unused args.

**Important APIs/types:** `BuildArgs` stores `allowedBuildArgs`, `allowedMetaArgs`, `referencedArgs`, and `argsFromOptions`. Methods include `NewBuildArgs`, `Clone`, `MergeReferencedArgs`, `WarnOnUnusedBuildArgs`, `ResetAllowed`, `AddMetaArg`, `AddArg`, `IsReferencedOrNotBuiltin`, `GetAllAllowed`, `GetAllMeta`, `FilterAllowed`, and internal lookup helpers.

**Control flow:** Lookup prefers user-supplied non-nil option values, then Dockerfile defaults, then meta args for unset regular args. Filtering removes args already present in image env. Unused warnings exclude builtin proxy args unless referenced.

**State and persistence:** State is in-memory for one build and per-stage clones. It influences cache keys and command environments but does not persist directly into the image except through dispatchers.

**Dependencies and integration:** Used by meta-arg processing, `FROM` expansion, `ARG`, `RUN`, and cache-command construction.

**Risks:** Builtin proxy args are intentionally transparent; changing reference logic can alter image history/cache behavior. Nil pointer values represent declared-but-unset args and must be preserved.

**Test signals:** `buildargs_test.go` covers allowed/meta lookup, unused warnings, and builtin reference filtering.
