# sources/distributed-fs/ceph/src/rgw/rgw_token.h

## Purpose
`rgw_token.h` defines `rgw::RGWToken`, a small credential token model with binary encoding, JSON encoding/decoding, and base64 JSON output.

## Important APIs, Types, and Functions
`token_type` supports none, AD, Keystone, and LDAP. `to_type()`/`from_type()` convert names. `valid()` checks type/id/key presence. Constructors build empty, explicit, or JSON-decoded tokens. `encode()`/`decode()` implement Ceph binary format. `dump()`, `encode_json()`, `decode_json()`, and `encode_json_base64()` provide Formatter/JSON support. `operator<<` prints token fields.

## Control Flow
JSON construction parses a top-level object, decodes nested `RGW_TOKEN`, and fills type/id/key. Binary encoding stores a name marker, version, type string, id, and key.

## State and Persistence Behavior
The token stores secret material in clear text in memory and encoded JSON/binary. It is a durable/interchange format for integration tokens.

## Dependencies and Integration Points
Depends on Ceph JSON/Formatter, encoding macros, Boost case-insensitive comparison, and RGW base64 helpers. Used by `radosgw-token` and external auth integrations.

## Risks
No version validation is performed on JSON decode. `operator<<` prints the secret key. JSON parse errors are not checked before decode. `encode_json()` opens an outer `RGW_TOKEN` section and then encodes another `RGW_TOKEN`, so consumers must expect that nested shape.

## Test Signals
Cover JSON and binary round trips, type conversions, invalid JSON, empty fields, base64 output, and redaction expectations for logging.
