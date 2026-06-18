# sources/distributed-fs/beegfs-go/common/beegfs/entry_test.go

## Purpose
This Go test file verifies selected behavior in BeeGFS entry and feature flag types.

## Important Tests
`TestIsFile` asserts that directories are not files and regular files and sockets are files. `TestFeatureFlags` starts with zero flags, verifies buddy-mirrored and inlined bits are false, sets buddy-mirrored and checks boolean plus integer form, then sets inlined and verifies both bits.

## Dependencies and Integration
The tests use `stretchr/testify/assert` and directly exercise `entry.go`.

## Signals and Gaps
The tests document intended file classification and flag mutation. They do not cover string output, stripe pattern names, `FileState` packing, data-state extraction, or access flag modification helpers.
