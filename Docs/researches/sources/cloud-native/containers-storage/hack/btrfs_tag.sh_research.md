<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/btrfs_tag.sh -->
# sources/cloud-native/containers-storage/hack/btrfs_tag.sh

## Purpose
This build helper emits a Go build exclusion tag when Linux btrfs headers are unavailable.

## Important APIs, Types, And Functions
It uses `${GO:-go} env GOOS`, the system C preprocessor, and `#include <btrfs/ioctl.h>`.

## Control Flow
Non-Linux exits successfully with no output. On Linux, it preprocesses a small C snippet; if preprocessing fails, it prints `exclude_graphdriver_btrfs`.

## State And Persistence
No files are modified.

## Dependencies And Integration Points
Build scripts can use the output as a build tag, pairing with `register_btrfs.go`.

## Risks And Test Signals
It assumes `cc` is available. Header detection is compile-time and may not reflect runtime btrfs capability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/btrfs_tag.sh -->
