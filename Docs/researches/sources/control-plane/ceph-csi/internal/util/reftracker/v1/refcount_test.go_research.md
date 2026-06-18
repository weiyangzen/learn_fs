<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go

Purpose: checks v1 refcount serialization.

Coverage: encodes `refCount(123)` as a four-byte big-endian value and decodes it back. Rejects a three-byte slice.

Dependencies: `testify/require`.

Integration: protects the RADOS object body format used by all v1 tracker reads/writes.

Risks and gaps: no boundary tests for `0`, `math.MaxUint32`, overflow arithmetic, or empty input; overflow is covered indirectly in v1 add tests through a max refcount fixture.

Test signal quality: narrow but valuable for the binary format.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go -->
