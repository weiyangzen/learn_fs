<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/template.go -->
# sources/cloud-native/containers-storage/drivers/template.go

## Purpose
`template.go` provides a naive implementation of create-from-template for graphdrivers that can create, remove, diff, and apply layers but lack a specialized clone/template path.

## Important APIs, Types, And Functions
`TemplateDriver` combines `DiffDriver`, `CreateReadWrite`, `Create`, and `Remove`. `NaiveCreateFromTemplate` creates the destination layer, diffs the template against the requested parent, and applies that diff to the new layer.

## Control Flow
The function chooses read-write or read-only creation, removes the new layer if creation of the diff or apply fails, defers closing the diff reader, then calls `ApplyDiff` with template mappings and mount label from `CreateOpts`.

## State And Persistence
It creates a new layer through the supplied driver and may delete it on errors. The actual persistent layout is driver-specific.

## Dependencies And Integration Points
It is a graphdriver-level helper for drivers without native template support. It depends on idtools mappings and logrus for cleanup errors.

## Risks And Test Signals
The implementation assumes `opts` is non-nil when reading `opts.MountLabel` and `opts.ignoreChownErrors`; callers must satisfy that contract. It can be expensive because it streams a full diff instead of using filesystem-native cloning.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/template.go -->
