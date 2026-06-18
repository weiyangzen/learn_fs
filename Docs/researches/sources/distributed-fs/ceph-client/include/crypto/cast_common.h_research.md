# sources/distributed-fs/ceph-client/include/crypto/cast_common.h

Purpose: shared CAST cipher S-box table declarations.

Important APIs/types/functions: external arrays `cast_s1`, `cast_s2`, `cast_s3`, and `cast_s4`.

Control flow: none in header; CAST5/CAST6 implementations index these tables during key schedule and rounds.

State and persistence: read-only global table data defined elsewhere.

Dependencies and integration points: included by CAST cipher headers/implementations.

Risks: table definitions must be linked exactly once and match the CAST specifications.

Test signals: CAST5/CAST6 KATs and link-time coverage for table providers.
