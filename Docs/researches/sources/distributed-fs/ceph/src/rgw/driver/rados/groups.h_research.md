# sources/distributed-fs/ceph/src/rgw/driver/rados/groups.h

Purpose: Declares account group-list helper APIs and the encoded metadata payload stored with each cls_user account resource.

Important APIs/types/functions: `add()`, `remove()`, and `list()` manipulate group resources on a supplied `rgw_raw_obj`. `resource_metadata` encodes/decodes `group_id`, dumps JSON, and has test instances; `WRITE_CLASS_ENCODER` registers encoding helpers.

Control flow: Callers provide marker/path-prefix/max for paginated listing and receive ids plus `next_marker`.

State/persistence: The metadata schema is versioned with `ENCODE_START(1, 1)` and stores only `group_id`; the cls_user resource itself stores name/path.

Dependencies/integration: Uses librados forward declarations, Ceph encoding, SAL forward declarations, `DoutPrefixProvider`, and `RGWGroupInfo`.

Risks: Schema currently stores minimal metadata; future list consumers needing more fields require versioned changes. Remove-by-name inherits rename consistency risks.

Test signals: Encoder round-trip, JSON dump, generated test instances, and API consumers preserving pagination markers.
