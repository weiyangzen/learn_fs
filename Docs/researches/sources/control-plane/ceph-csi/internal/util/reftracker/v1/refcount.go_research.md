<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go

Purpose: defines v1 reftracker version constant and binary encoding for the object body refcount.

APIs and types: private `refCount uint32`, `Version = 1`, and `refCountSize = 4`. `toBytes` writes big-endian uint32. `refCountFromBytes` requires exactly four bytes and parses big-endian uint32.

State and persistence: the encoded refcount is written as the full RADOS object body for v1 trackers.

Dependencies: standard `encoding/binary` and reftracker `UnexpectedReadSize`.

Integration points: `v1.Init`, `v1.Add`, `v1.Remove`, and `readObjectByKeys` use this encoding to maintain total normal refs.

Risks: arithmetic checks in `v1.Add` and `v1.Remove` must protect overflow/underflow because the type is unsigned. Layout changes require new version dispatch.

Test signals: `refcount_test.go` confirms `{0,0,0,0x7B}` for 123 and wrong-size errors.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go -->
