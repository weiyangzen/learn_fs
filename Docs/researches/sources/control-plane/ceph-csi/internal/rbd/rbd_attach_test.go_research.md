<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go

## Purpose
`rbd_attach_test.go` unit-tests parsing of mounter-specific map and unmap options.

## Important APIs, Types, And Functions
The only test is `TestParseMapOptions`, which calls `parseMapOptions`.

## Control Flow
The table covers old unlabeled format, new `krbd:` and `nbd:` labels, omitted `krbd:` label, NBD-only options, option values that themselves contain `:`, and unknown mounter labels.

## State And Persistence
No state persists; tests are pure string parsing.

## Dependencies And Integration Points
The test depends on standard `testing` and `strings`. It protects `NodeServer.getMapOptions` input semantics and StorageClass option compatibility.

## Risks
It does not validate command-line argument rendering or interaction with actual `rbd`/`rbd-nbd` commands. The error assertion only checks substring when an error exists, so unexpected nil error in an expected-error case would not be caught as directly as it could be.

## Test Signals
Good regression signal for delimiter handling and backward compatibility; weak signal for attach/unmap behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go -->
