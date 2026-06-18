<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_aufs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_aufs.go

## Purpose
This file conditionally registers the aufs graphdriver by blank-importing its package.

## Important APIs, Types, And Functions
There are no exported symbols; the blank import triggers the aufs package `init`.

## Control Flow
Registration occurs at package initialization when built with `linux` and without `exclude_graphdriver_aufs`.

## State And Persistence
No state is persisted here, though the imported driver registers into the global graphdriver registry.

## Dependencies And Integration Points
The package is used by consumers that want all available drivers linked by importing `drivers/register`.

## Risks And Test Signals
Build tags are the main behavior. Incorrect tags could unexpectedly include a driver with unavailable prerequisites.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_aufs.go -->
