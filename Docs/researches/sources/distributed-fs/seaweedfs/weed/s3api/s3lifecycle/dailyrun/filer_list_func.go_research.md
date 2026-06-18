# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func.go

Purpose: adapts the filer tree into the bootstrap walker's `ListFunc`. It recursively lists bucket contents, expands versioned object siblings with lifecycle-relevant metadata, emits MPU init records, paginates filer listings, and extracts object tags.

Important APIs/types: `FilerListFunc`, `walkBucketTree`, `versionItem`, `expandVersionsDir`, `lookupNullVersion`, `listAll`, `isVersionsDir`, `isMPUInitDir`, and `extractTags`. `listPageSize` is an atomic test-tunable page size defaulting to 1024.

Control flow: `FilerListFunc` builds a bucket root and calls `walkBucketTree`. Each directory is processed in two passes: first `.versions` directories to expand version siblings and mark bare null versions to skip, then regular files/directories. Version expansion lists child version entries, filters entries with version ids, optionally appends the bare null version, sorts newest-first with version-id tie-breaks, resolves latest by pointer/explicit null/newest fallback, computes successor mod time and noncurrent rank, and emits one `bootstrap.Entry` per version. Regular files become latest entries with tags. MPU init directories at `.uploads/<id>` with destination metadata emit `IsMPUInit` entries.

State and persistence behavior: no direct persistence, but it reads persistent filer metadata and shapes it into walker state. Resume skips entries with logical `Path <= start`; version siblings share one logical path, so a mid-group resume reprocesses the whole group.

Dependencies and integration points: depends on `filer_pb.SeaweedList`, `LookupEntry`, S3 extended metadata constants, lifecycle version helpers, `bootstrap.Entry`, and `util.NewFullPath`. Used by daily-run walker wiring.

Risks: this code must stay consistent with older scheduler/bootstrap listing semantics until that path is removed. The two-pass `.versions` handling is subtle; mistakes can duplicate bare null objects or mark the wrong latest version. `listAll` assumes a nonzero page size; a test setting it to zero could loop incorrectly depending on filer behavior. Lookup errors for null version are treated as absence, not fatal. Pagination correctness depends on sorted exclusive `StartFromFileName`.

Test signals: `filer_list_func_test.go` covers flat files, recursion, tags, MPU init detection/skipping, version pointer/latest rules including stale pointer and explicit null, user folders ending in `.versions`, delete marker propagation, resume start, nil client, and attribute propagation.
