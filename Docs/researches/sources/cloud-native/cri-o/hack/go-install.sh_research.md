# sources/cloud-native/cri-o/hack/go-install.sh

## Purpose
Helper to either copy an existing tool binary into a destination or install it with go install.

## Important APIs, Types, and Functions
Arguments DEST_DIR CMD GO_INSTALL_LOCATION; uses command -v, mkdir, cp, and GOBIN=DEST_DIR go install.

## Control Flow
Validates three args; if CMD exists on PATH copy it, otherwise install requested module into destination.

## State and Persistence
Writes DEST_DIR/CMD binary.

## Dependencies
Depends on Go toolchain for missing binaries and shell coreutils.

## Integration Points
Used by build scripts to materialize required Go tools reproducibly while reusing installed tools.

## Risks and Edge Cases
Existing PATH binary may be wrong version; go install is network/module-cache dependent.

## Test Signals
Destination binary existence and version output validate it.
