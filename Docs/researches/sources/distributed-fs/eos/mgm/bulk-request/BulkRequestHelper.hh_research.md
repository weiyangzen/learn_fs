## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestHelper.hh

Purpose: declares a small helper for bulk-request IDs. `generateBulkRequestId()` delegates to `common::StringConversion::timebased_uuidstring()`.

Control flow/state: header-only, stateless, and synchronous. It exists to centralize ID generation for `BulkRequestFactory`.

Dependencies: `mgm/Namespace.hh` and `common/StringConversion.hh`. Risks include ID uniqueness and clock/source behavior being entirely delegated, and tests needing deterministic seams if they assert exact IDs. Test signals should assert non-empty unique-looking values and factory propagation, rather than exact string contents.
