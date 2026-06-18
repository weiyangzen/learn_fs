# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares `RGWKMIPTransceiver` operations, C-style input/output fields, completion state, and abstract `RGWKMIPManager`. Transceivers submit create/locate/get/get-attributes/list-attributes/destroy requests and receive unique ids, id lists, or key bytes. Persistence is on the KMIP server; local outputs are owned by the transceiver. It integrates with `RGWKMIPManagerImpl` and RGW crypt code. Risks include manual memory ownership, raw `name`/`unique_id` pointers, and declared operations that may be unsupported by the implementation. Tests should mock manager submission and verify operation inputs, outputs, cleanup, and error propagation.
