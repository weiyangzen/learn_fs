<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_btrfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_btrfs.go

## Purpose
This file conditionally registers the btrfs graphdriver.

## Important APIs, Types, And Functions
It has only a blank import of `github.com/containers/storage/drivers/btrfs`.

## Control Flow
The btrfs driver's `init` runs when this file is included by `linux && !exclude_graphdriver_btrfs`.

## State And Persistence
Only global driver-registry state changes.

## Dependencies And Integration Points
The build tag pairs with `hack/btrfs_tag.sh`, which can emit the exclusion tag when btrfs headers are unavailable.

## Risks And Test Signals
Registration availability depends on build environment and tags, not runtime probing in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_btrfs.go -->
