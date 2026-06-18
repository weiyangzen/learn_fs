<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go

## Purpose
Implements the Windows `blockcim` snapshotter, storing image layers as block CIMs and creating scratch VHDs for writable container layers.

## Important APIs, Types, And Functions
`BlockCIMSnapshotterConfig` controls layer integrity, VHD footer appending, and unformatted scratch behavior. Main methods implement `snapshots.Snapshotter`: `NewBlockCIMSnapshotter`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`. Helpers include `snapshotInfoFromID`, `getSnapshotBlockCIM`, `createSnapshot`, `createScratchLayer`, `mounts`, `prepareMergedCIM`, and `isScratchSnapshot`.

## Control Flow
Initialization skips when block CIMs are unsupported, creates base snapshotter state, and prepares either formatted differencing scratch VHDs or an unformatted template VHD. Active scratch creation rejects parentless scratch snapshots, handles optional UVM scratch first, creates a scratch VHD, then for multi-parent scratch snapshots serializes merged-CIM preparation with a keyed lock. Mount construction emits `BlockCIM` mounts with parent CIM paths, block type, integrity/footer flags, optional merged CIM path, and source selected by scratch-vs-layer status.

## State And Persistence
Stores metadata in `metadata.db`, snapshot directories under `snapshots/<id>`, `layer.vhd/layer.cim` single-file block CIM data, optional `merged.vhd/merged.cim`, `sandbox.vhdx`, and root-level scratch templates. Removal renames metadata/directory through `preRemove` and deletes the renamed snapshot directory.

## Dependencies And Integration Points
Uses hcsshim CIMFS APIs, OCI WC layer CIM merge package, keyed mutex, containerd mount flags for BlockCIM, Windows base snapshotter helpers, plugin registry, and continuity disk usage.

## Risks And Edge Cases
Only unpack snapshots can be committed as read-only CIM layers; scratch commit is unsupported. Unformatted scratch requires at least 40 GiB when custom-sized. Merge correctness depends on snapshot parent order and committed parent metadata. Merge and mount options must stay aligned with downstream Windows mount handlers.

## Test Signals
No file-local tests in this subset. Coverage is mostly compile/integration on Windows and shared tests for mount flag parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go -->
