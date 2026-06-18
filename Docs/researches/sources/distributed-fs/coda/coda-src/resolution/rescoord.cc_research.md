<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rescoord.cc

Purpose: coordinator-side directory resolution for simple cases: already inconsistent replicas, equal directories, weak equality, and old-logless directory resolution fallback.

Important APIs/control flow: `CompareDirContents` compares directory data and ACL blobs returned by participants, optionally dumping debug files. `ResolveInc` marks all replicas inconsistent, fetches status and contents, compares status/content, and clears inconsistency when replicas are equal. `IsWeaklyEqual` compares store IDs across version vectors. `WEResPhase1` computes a max VV and multicasts `ForceVV`; `WEResPhase2` sends COP2 update sets. `RegDirResolution` masks unavailable hosts, calls `UpdateRunts`, handles already-inconsistent groups, detects already equal vectors, handles weak equality, and reports whether log resolution is still required. `OldDirResolve` marks conflict when no log-based resolution can solve it.

State/persistence: mutates remote replicas through multicast RPCs (`MarkInc`, `ClearIncon`, `ForceVV`, `COP2`), updates timing probes, and may trigger server probing. Local state is temporary buffers and status arrays.

Dependencies/integration: uses `rescomm` groups, `resforce` runt repair, RPC2 side effects, directory/ACL comparison, and `resstats`/timing globals.

Risks/test signals: ACL equality is noted as imperfect and not fatal. Fixed maximum directory buffer sizing can be exceeded for very large directories. Test weak equality, all/some inconsistent groups, equal status with unequal directory content, incomplete VSG, and old resolution with no logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.cc -->
