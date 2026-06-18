<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go

Purpose: protects the reftracker version xattr format and read behavior.

Coverage: `TestVersionBytes` verifies v1 value `1` encodes as `{0,0,0,1}` and wrong-size decode fails. `TestVersionRead` validates successful xattr read and errors for missing object, missing xattr, and wrong-sized xattr content.

Dependencies: fake RADOS and `testify/require`.

Integration: ensures `reftracker.Add`/`Remove` can reliably distinguish absent objects from readable v1 objects.

Risks and gaps: does not test unknown-but-well-formed versions; that is handled by top-level dispatch rather than this package.

Test signal quality: strong for xattr read and binary format.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go -->
