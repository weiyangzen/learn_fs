<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go

## Purpose

Implements `ipfs dag import`, importing CAR blocks into the local DAG/blockstore, optionally pinning roots, emitting stats, and triggering fast provider announcements.

## Important APIs, Types, and Functions

`dagImport` is the handler. It uses CARv2 `NewBlockReader`, legacy IPLD node decoding, `ipld.Batch`, `cmdutils.CheckBlockSize`, root pinning through `node.Pinning`, and `cmdenv.ExecuteFastProvideRoot`/`ExecuteFastProvideDAG`.

## Control Flow

The handler loads node config and forces an offline API for import-time pinning. It resolves defaults for `--pin-roots`, `--local-only`, and fast-provide flags from CLI or config. If pinning, it takes the blockstore pin/GC lock. It iterates input files, hides `io.Seeker` to force sequential CAR reading, records CAR header roots, validates block sizes, decodes blocks into IPLD nodes, batches them, and commits. After import, it optionally pins each root, emits stats, and either fast-provides the full DAG or root CIDs.

## State and Persistence Behavior

Writes imported blocks to the local DAG/blockstore. Optional root pinning updates pinner state and flushes it. Fast provide publishes provider records to the network. `--local-only` implies no root pinning because partial CARs may not contain complete DAGs.

## Dependencies and Integration Points

Depends on node blockstore, pinner, provider, import config batch limits, CARv2 reader, CoreAPI DAG, config defaults, and command file iterators.

## Risks and Edge Cases

Import is not transactional; partial blocks may persist if later blocks fail. Pinning happens after all files are processed so multi-file DAGs can work, but pin failures are reported per root. Truncated CAR errors include previous/current block context. Fast-provide async errors are logged, not returned.

## Test Signals

No direct tests in this subset. Regression targets include partial CAR import, pin-root conflicts with local-only, batch commit failures, malformed/truncated CAR messages, block-size rejection, stats emission, and fast-provide option resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go -->
