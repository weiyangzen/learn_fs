<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc

## Purpose
Implements URI parsing, encoding/decoding, construction, query manipulation, and debug formatting for libhdfspp.

## Important APIs, Types, And Functions
Core APIs include `URI::parse_from_string`, `encode`, `decode`, `str`, `has_authority`, `build_authority`, scheme/host/port/path/query/fragment getters and setters, `add_path`, `add_query`, `remove_query`, `from_encoded`, `to_encoded`, and `GetDebugString`. Internal helpers copy uriparser ranges, parse ports, path segments, user info, and query lists.

## Control Flow
Parsing delegates to `uriparser2`, copies parsed components into encoded internal fields, parses user info and queries, and throws `uri_parse_error` on failure. Formatting reconstructs a URI from fields, optionally decoding output. Path and query setters encode inputs unless marked already encoded.

## State And Persistence
Each `URI` stores scheme, host, user, password, path vector, query vector, fragment, and `_port` sentinel `-1`. No global or durable state exists.

## Dependencies And Integration Points
Used by configuration parsing, namenode info, options, and filesystem connection code. Depends on `uriparser2`.

## Risks
`parse_user_info` appears to compute username length as `colon_loc - begin - 1`, dropping one character before the colon. `parse_from_string` calls `uriFreeUriMembersA` both inside and after the success block, a potential double-free risk depending on uriparser behavior. `set_path` appends parsed elements without clearing existing path. Port parsing rejects the maximum uint16 value because it uses `< max`.

## Test Signals
Tests should parse and round-trip schemes, authorities, users/passwords, ports, paths, queries, fragments, encoded characters, invalid URIs, repeated `set_path`, query removal, and edge ports 0/65535.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc -->
