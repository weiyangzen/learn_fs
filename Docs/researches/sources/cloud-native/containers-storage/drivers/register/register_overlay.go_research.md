<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_overlay.go -->
# sources/cloud-native/containers-storage/drivers/register/register_overlay.go

## Purpose
This file conditionally registers the overlay graphdriver.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/overlay`.

## Control Flow
The overlay driver's `init` registers both `overlay` and `overlay2` when built with `linux && !exclude_graphdriver_overlay`.

## State And Persistence
Only in-process graphdriver registry state is affected.

## Dependencies And Integration Points
Consumers import `drivers/register` to make overlay discoverable without explicitly importing the driver package.

## Risks And Test Signals
If the build excludes this file, overlay names will not resolve through the registry even if overlay source exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_overlay.go -->
