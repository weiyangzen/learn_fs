# sources/distributed-fs/ipfs-kubo/core/coreunix/add.go

## Purpose
Implements the lower-level UnixFS adder used to import file trees into DAG/MFS, emit add/progress events, and optionally pin the resulting root safely with concurrent GC.

## Important APIs, Types, and Functions
Defines `Link`, `NewAdder`, `Adder`, `mfsRoot`, `SetMfsRoot`, `mkdirOpts`, `add`, `curRootNode`, `PinRoot`, `outputDirs`, `addNode`, `AddAllAndPin`, `addFileNode`, `addSymlink`, `addFile`, `addDir`, `maybePauseForGC`, `outputDagnode`, `getOutput`, `progressReader`, and `progressReader2`.

## Control Flow and State
`NewAdder` creates a buffered DAG and defaults. `AddAllAndPin` takes a pin lock when pinning, recursively adds nodes into an MFS root, flushes/closes the root, emits directory events, syncs async DAG services, and pins the final root. File adds chunk input, build balanced/trickle UnixFS DAGs, commit buffered blocks, and patch nodes into MFS. Directory adds peek for emptiness, optionally skip empty dirs, preserve root metadata, and recurse. During GC requests, `maybePauseForGC` pins the current root, releases/reacquires the pin lock, and tracks a temporary root.

## Dependencies and Integration Points
Depends on Boxo blockstore GC locks, files, chunker, filestore posinfo, merkledag, UnixFS importer, MFS, pinner, CIDs, Kubo config defaults, CoreAPI add events, and tracing. CoreAPI UnixFS add implementations configure and call this adder.

## Risks and Test Signals
Risks include GC races during long adds, MFS memory growth, event ordering, path/name handling for single files vs directories, no-copy posinfo propagation, metadata preservation drift, empty-directory semantics, and progress channel blocking. Tests cover GC live safety, no-copy posinfo, and CoreAPI UnixFS add/get/list behavior.
