<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h

## Purpose
Declares the public LSMT file interfaces and constructors for OverlayBD layered image files.

## Important APIs, Types, And Functions
Defines constants `MAX_STACK_LAYERS`, `ALIGNMENT`, and `ALIGNMENT4K`; interfaces `IFileRO` and `IFileRW`; argument structs `CommitArgs`, `LayerInfo`, and `WarpFileArgs`; and exported C constructors/openers/mergers/stackers including `create_file_rw`, `open_file_rw`, `open_file_ro`, `open_files_ro`, `create_warpfile`, `open_warpfile_*`, `merge_files_ro`, `stack_files`, `open_file_index`, `open_files_with_merged_index`, and `is_lsmt`.

## Control Flow
Callers create or open RW layers, write aligned data/discards, optionally stack with RO layers, then seal or commit. RO callers open one or many sealed files and use `pread`, `seek_data`, `flatten`, and index access.

## State And Persistence
The header describes persistent layer inputs: data file, index file, sparse metadata, target/remote file, virtual size, UUIDs, parent UUID, and user tag. Runtime ownership can be transferred through `ownership` flags.

## Dependencies And Integration Points
Extends Photon virtual file interfaces and uses UUID plus LSMT memory index APIs. It is the stable C/C++ integration surface for LSMT layer files.

## Risks And Test Signals
Manual ownership and raw `IFile*` arrays make lifetime discipline important. `CommitArgs::user_tag` is capped by implementation at 256 bytes. `RemoteData` and `GetType` ioctl request values are part of the integration contract. Source size reviewed: 195 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h -->
