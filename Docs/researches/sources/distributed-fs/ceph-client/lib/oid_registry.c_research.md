# sources/distributed-fs/ceph-client/lib/oid_registry.c

## Purpose
Implements lookup, ASN.1 wrapper parsing, and string formatting for registered object identifiers used by kernel crypto, key, certificate, and ASN.1 consumers.

## APIs, Control Flow, and State
Exports `look_up_OID()`, `parse_OID()`, and `sprint_oid()`. `look_up_OID()` hashes DER OID octets, then binary-searches generated tables from `oid_registry_data.c`, ordered by hash, length, and reverse byte value. `parse_OID()` validates a minimal ASN.1 `ASN1_OID | length | oid` envelope and returns the registered enum or `OID__NR` for unknown OIDs. `sprint_oid()` decodes the first combined arc and subsequent base-128 continuation arcs into dotted decimal text, returning `-EBADMSG` for malformed encodings and `-ENOBUFS` for short buffers. Persistent state is generated static registry data.

## Dependencies, Integration, Risks, and Tests
Depends on ASN.1 constants, generated OID tables, kernel formatting, and exported GPL symbols. Risks include generated table order/hash mismatches, malformed continuation bytes, buffer truncation, unknown OIDs being represented only as `OID__NR`, and invalid first-arc semantics not deeply validated. Test signals include generated registry self-checks, DER certificate parsing tests, malformed OID fuzzing, dotted string buffer-boundary tests, and lookup tests for every generated OID.
