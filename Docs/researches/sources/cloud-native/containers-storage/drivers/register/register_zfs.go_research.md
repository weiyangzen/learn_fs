<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_zfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_zfs.go

## Purpose
This file conditionally registers the ZFS graphdriver.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/zfs`.

## Control Flow
ZFS registration runs on Linux, FreeBSD, or Solaris unless `exclude_graphdriver_zfs` is set for Linux/FreeBSD.

## State And Persistence
Only graphdriver registry state changes.

## Dependencies And Integration Points
The registration makes ZFS available to storage configuration that selects it by name.

## Risks And Test Signals
Runtime ZFS prerequisites are checked in `zfs.Init`; this file only controls link-time availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_zfs.go -->
