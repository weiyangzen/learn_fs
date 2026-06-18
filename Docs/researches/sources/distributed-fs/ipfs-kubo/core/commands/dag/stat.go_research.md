<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go

## Purpose

Implements `ipfs dag stat`, traversing one or more DAG roots and reporting per-root and aggregate block/size statistics.

## Important APIs, Types, and Functions

`dagStat` traverses DAGs. `finishCLIStat` filters progressive updates and emits the final summary. It uses `DagStatSummary` and `DagStat` from `dag.go`, `merkledag.NewSession`, and boxo `traverse.Traverse`.

## Control Flow

The handler defaults progressive emission to true unless `--progress` is specified. It resolves each root, rejects path remainders, fetches the root node, appends a per-root stat entry, and traverses DFS with duplicate skipping. For a single root it avoids an extra command-level CID set to reduce memory; for multiple roots it uses a set to count cross-root unique blocks. It emits progress summaries during traversal, computes final unique/shared/ratio values, and emits the final summary.

## State and Persistence Behavior

Read-only. Traversal may fetch DAG blocks via CoreAPI depending on request mode.

## Dependencies and Integration Points

Uses `cmdenv.GetCidEncoder`, `cmdutils.PathOrCidPath`, boxo merkledag sessions/traversal, humanize output, and `e.TypeErr`.

## Risks and Edge Cases

Large DAG traversal can be expensive; the single-root memory optimization avoids duplicating boxo's seen set. Ratio calculation assumes total size is nonzero. CLI progress treats `Ratio == 0` as progress, so unusual final zero-size DAGs need care.

## Test Signals

No direct tests. Important tests include duplicate blocks within and across roots, progress on/off, path remainder rejection, missing blocks, and huge-DAG memory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go -->
