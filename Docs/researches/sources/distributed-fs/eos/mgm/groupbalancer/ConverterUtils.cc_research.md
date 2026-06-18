# sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.cc

## Purpose
Implements conversion-tag construction for balancer and drainer transfers by resolving file metadata, optionally filtering paths, returning file size, and formatting a proc conversion path.

## Important APIs, types, and functions
`PrefixFilter::operator()` rejects paths with a configured prefix using `common::startsWith()`. `getFileProcTransferNameAndSize()` prefetches file metadata, retrieves the file from `gOFS->eosFileService`, resolves the namespace URI, locks the file metadata for reading, checks container membership, applies the optional skip filter, writes the file size, and formats `<MgmProcConversionPath>/<fid>:<target_group>#<layoutid>`.

## Control flow
The caller supplies an FID and target group. The helper returns an empty string for metadata lookup failures, files without container ownership, and filtered paths. Successful calls return the proc conversion file name and optionally fill `size`.

## State and persistence
No durable state is written here. It reads namespace metadata under a metadata lock and exposes enough data for later converter scheduling.

## Dependencies and integration points
Uses `gOFS`, `Prefetcher`, `IView`, `IFileMD`, `LayoutId`, `MDLocking`, and EOS logging. `GroupBalancer` uses a prefix filter to avoid moving proc files; `GroupDrainer` uses `NullFilter`.

## Risks and test signals
The fixed 1024-byte buffer may truncate very long proc paths or group names. It returns empty strings for several different failure classes, so callers cannot distinguish filter skips from metadata failures. Tests should cover missing FIDs, container id zero, prefix filtering, size output, layout id formatting, and long target group names.
