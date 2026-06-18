# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/uri.h

## Purpose
`URI` is libhdfs++'s URI parser/builder with encode/decode support for HDFS configuration and user paths.

## Important APIs, Control Flow, and State
`URI::parse_from_string` throws `uri_parse_error` on malformed input. Static `encode`/`decode` transform strings. Accessors and mutators cover scheme, host, optional port, path, path elements, query string, query elements, fragment, and full `str` output, with encoded-input/output flags. `Query` stores key/value pairs. Private helpers track authority, build encoded authority/path, parse paths, and store port as a signed internal field to represent absence.

## Dependencies and Integration Points
`Options::defaultFS`, `NamenodeInfo`, config parsing, tools, and connection logic use `URI`. It likely integrates with uriparser2 internally.

## Risks and Test Signals
Encoding semantics and optional port handling are central. Tests should cover empty URI, scheme-only, host/port, default port fallback, IPv6 if supported, encoded paths, query/fragment round trips, bad percent encodings, path element mutation, and ostream output.
