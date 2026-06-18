<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_vfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_vfs.go

## Purpose
This file always links the VFS graphdriver into the driver registry.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/vfs`.

## Control Flow
Package initialization of VFS registers the `vfs` driver.

## State And Persistence
No persistent state; the global driver registry is populated.

## Dependencies And Integration Points
VFS is the portable fallback driver and is available regardless of Linux-specific graphdrivers.

## Risks And Test Signals
The file is intentionally minimal. Regressions would present as missing `vfs` registration in driver discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_vfs.go -->
