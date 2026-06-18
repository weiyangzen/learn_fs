<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go

Purpose: handles reftracker object layout version xattr encoding and reading.

APIs: `XattrName` is `csi.ceph.com/rt-version`; `SizeBytes` is four. `ToBytes` and `FromBytes` encode/decode big-endian uint32. `Read` reads the xattr through `IOContextW.GetXattr`, validates returned byte count, and parses the value.

State and persistence: version is stored as a RADOS object xattr, separate from the object body and omap.

Dependencies: standard `encoding/binary`, reftracker errors, and RADOS wrapper interface.

Integration points: top-level `reftracker.Add`/`Remove` use `Read` to dispatch to v1 or fail unknown versions.

Risks: missing xattr, wrong length, or object not found bubble to callers; top-level code treats only object not found specially. Short reads are detected both by returned size and parser length.

Test signals: `version_test.go` covers encoding, decoding, missing object, missing xattr, and wrong-sized version data using fake RADOS.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go -->
