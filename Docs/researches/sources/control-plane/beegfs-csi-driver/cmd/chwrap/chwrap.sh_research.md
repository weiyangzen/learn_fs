<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh -->
# sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh

## Purpose
`chwrap.sh` builds a tarball containing the `chwrap` binary plus symlinks for host commands that the driver may need inside the container.

## Important APIs, Types, and Functions
This shell script expects three arguments: the source `chwrap` binary, output tar path, and destination directory name. It creates a temporary prefix with `uuidgen`, copies the binary as `$3/chwrap`, symlinks `beegfs`, `beegfs-ctl`, `lsmod`, `modprobe`, `mount`, `touch`, and `umount` to `chwrap`, archives the directory with root owner/group, and removes the temporary tree.

## Control Flow
The script exits immediately on errors (`#!/bin/sh -e`) and rejects missing arguments. It performs create/copy/link/tar/cleanup in sequence.

## State and Persistence
Persistent output is only the requested tarball. Temporary state is created under `/tmp/<uuid>` and removed at the end on the normal path.

## Dependencies and Integration Points
It depends on `uuidgen`, `mkdir`, `cp`, `ln`, `tar`, and `rm`. The Makefile calls it to create `bin/chwrap*.tar`, and the Dockerfile adds that tarball into the image so `/osutils` contains the symlinked commands.

## Risks
If any command fails before cleanup, the temporary directory may remain because there is no trap. The symlink list must stay aligned with driver runtime needs. Argument values are unquoted in a few path positions (`$PREFIX/$3`), so unusual destination names with spaces would be unsafe, though Makefile usage uses `osutils`.

## Test Signals
Signals include invoking the script with a built `chwrap`, inspecting the tar contents and ownership, extracting into a test root, and confirming each symlink resolves to `chwrap`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh -->
