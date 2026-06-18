# sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.h

## Purpose
`cm_performance.h` exposes the data structure and public entry points for the optional cache-manager performance collector implemented in `cm_performance.c`.

## Important APIs and types
- `cm_fid_stats_t` records one FID, its file type, file length, summary flags, valid buffer count, and hash-chain link.
- `CM_FIDSTATS_FLAG_HAVE_SCACHE`, `CM_FIDSTATS_FLAG_HAVE_VOLUME`, `CM_FIDSTATS_FLAG_RO`, `CM_FIDSTATS_FLAG_PURERO`, and `CM_FIDSTATS_FLAG_CALLBACK` describe the observed cache/volume/callback state.
- `cm_PerformanceTuningInit()`, `cm_PerformanceTuningCheck()`, and `cm_PerformancePrintReport()` are the externally visible lifecycle and reporting functions.

## Control flow and state behavior
The header defines no state by itself. Its struct is intentionally compact and hash-chain-friendly, and its flags are used as denormalized observations collected from scache, volume, and buffer scans. The header assumes `cm_fid_t` and `osi_hyper_t` are already visible through the surrounding cache-manager include graph.

## Dependencies and integration points
It is tightly coupled to `cm_scache.h` for `cm_fid_t` and file type constants, and to cache-manager global accounting in `cm_data`. Consumers should include it only in the Windows afsd cache-manager context.

## Risks and edge cases
The struct lacks ownership fields or allocation metadata because implementation records are never freed. Any future attempt to support unloading, reset, or concurrent collection would need an explicit allocator and locking model.

## Test signals
Compile-time tests should ensure the header is included in contexts where `cm_fid_t` and `osi_hyper_t` are defined. Runtime tests belong with `cm_performance.c`: flag combinations, buffer counts, and reporting paths.
