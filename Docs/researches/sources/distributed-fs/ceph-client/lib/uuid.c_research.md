<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/uuid.c -->
# sources/distributed-fs/ceph-client/lib/uuid.c

## Purpose
Unified UUID/GUID helpers for null constants, random version-4 generation, string validation, and parsing with UUID big-endian and GUID little-endian byte ordering.

## APIs, Types, and Functions
Exports `guid_null`, `uuid_null`, `generate_random_uuid()`, `generate_random_guid()`, `guid_gen()`, `uuid_gen()`, `uuid_is_valid()`, `guid_parse()`, and `uuid_parse()`. Internal `guid_index` and `uuid_index` tables define byte placement; `__uuid_gen_common()` sets the DCE variant; `__uuid_parse()` handles canonical string parsing.

## Control Flow, State, and Persistence
Generation fills 16 bytes from `get_random_bytes()`, sets variant bits in byte 8, and sets version bits at UUID byte 6 or GUID byte 7 according to storage order. Validation checks exactly `UUID_STRING_LEN` positions for hyphens at 8/13/18/23 and hex digits elsewhere. Parsing validates first, then uses source indexes for pairs of hex digits and destination endian indexes to populate the 16-byte object. Null constants are static exported zero objects.

## Dependencies and Integration
Depends on random bytes, hex conversion, ctype, errno, UUID type definitions, and symbol exports. It integrates with filesystem IDs, boot IDs, firmware GUIDs, and drivers parsing UUID strings.

## Risks and Test Signals
Risks include validation not checking for a trailing NUL beyond the fixed length, case-insensitive hex acceptance via `isxdigit()`/`hex_to_bin()`, byte-order confusion between GUID and UUID APIs, and random generation depending on RNG readiness semantics. Test signals include version/variant bit checks, GUID/UUID parse byte order, malformed strings, uppercase hex, trailing characters, and null constant equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/uuid.c -->
