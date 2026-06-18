# Research: sources/distributed-fs/ipfs-kubo/core/commands/add.go

Purpose: Implements the user-facing `ipfs add` command, translating CLI/config import settings into CoreAPI UnixFS add options, emitting progress/events, optional MFS linking, pinning, and fast provide behavior.

Important APIs/types/functions: `ErrDepthLimitExceeded`, `AddEvent`, many option-name constants, `AddCmd` with `PreRun`, `Run`, and CLI `PostRun`. The command uses `options.Unixfs.*`, `cmdenv.ExecuteFastProvideRoot`, and `cmdenv.ExecuteFastProvideDAG`.

Control flow, state, and persistence: `PreRun` defaults progress to terminal stderr unless quiet/silent. `Run` obtains CoreAPI, node, and repo config; resolves each CLI option with config defaults from `Import`; validates inline limit, pin name, incompatible flags, hash function, metadata/raw-leaf conflicts, and MFS constraints. It wraps input files when requested, builds UnixFS add options, and iterates entries. For each entry it starts an add goroutine, streams CoreAPI add events into emitted `AddEvent`s with encoded CIDs, names, byte counts, mode, and mtime, then waits for the add error. Optional `--to-files` validates MFS destination, fetches the added DAG node, and writes it into MFS. After all entries, it optionally fast-provides the DAG or root CID unless only-hash disabled storage. Persistent effects include blockstore writes, pin records, MFS updates, and provider announcements.

Dependencies and integration points: Integrates config import/provide defaults, command environment, Boxo files/UnixFS/MFS/path, multihash, CID encoding, verifcid, progress bar, CoreAPI, blockstore/provider, and routing/provider subsystems.

Risks and test signals: This command has many CID-affecting options; config or default changes can break deterministic CIDs. `lastRootCid` and `fileAddedToMFS` are mutated by goroutines, though each add goroutine is drained before the next entry. MFS `toFilesStr` is mutated when empty. Fast-provide depends on provider availability and may be skipped/async. Progress size discovery races with output by design. Direct tests are not in this subset, so integration tests elsewhere are important.
