<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go

## Purpose
Implements the Windows `cimfs` snapshotter, storing committed read-only image layers as CimFS `.cim` files and using VHDX scratch layers for writable containers.

## Important APIs, Types, And Functions
Scratch helpers include `scratchCreationOpt`, `WithNTFSFormat`, `WithSize`, `defaultScratchCreationOptions`, `createDifferencingScratchVHDs`, and `createScratchVHD`. Snapshotter APIs include `NewCimFSSnapshotter`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `createSnapshot`, `createScratchLayer`, and `mounts`.

## Control Flow
Initialization skips unsupported hosts, creates base metadata state, prepares base/differencing scratch VHDs, and creates a shared `cim-layers` directory. Unpack snapshots do not create scratch VHDs and later commit as read-only CIM layers. Non-unpack active snapshots require parents, may create a UVM scratch layer, then copy/expand the scratch template. Mounts include layer CIM path plus parent layer and parent CIM path JSON options.

## State And Persistence
Persistent state includes `metadata.db`, `snapshots/<id>` directories, root-level `blank-base.vhdx` and `blank.vhdx`, shared `snapshots/cim-layers/<id>.cim`, and per-snapshot `sandbox.vhdx`. Usage for committed snapshots adds CimFS usage to base directory usage.

## Dependencies And Integration Points
Uses hcsshim, hcsshim CimFS, compute storage formatting, VHD APIs, VM group ACL helpers, containerd mount flags, and common Windows base snapshotter code.

## Risks And Edge Cases
Committing scratch snapshots to CIM is explicitly unsupported. Parentless scratch snapshots fail. Scratch VHD creation must handle partially existing base/diff files and clean them on failure. Host support and Windows privileges strongly affect behavior.

## Test Signals
`cimfs_test.go` covers mount option parsing through containerd mount helpers; full snapshotter behavior requires Windows integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go -->
