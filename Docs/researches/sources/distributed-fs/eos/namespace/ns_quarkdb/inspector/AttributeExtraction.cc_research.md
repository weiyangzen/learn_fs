## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.cc

Purpose: Implements string extraction of selected `FileMdProto` fields for inspector filtering and output logic.

Important APIs and control flow: `AttributeExtraction::asString()` clears output, then handles `xattr.<name>` specially by looking up the protobuf xattr map and returning true even if the attribute is absent. It supports built-in fields `fid`, `pid`, `uid`, `gid`, `size`, `layout_id`, octal `flags`, `name`, `link_name`, formatted `ctime`, `mtime`, checksum string `xs`, comma-separated `locations`, comma-separated `unlink_locations`, and formatted `stime`. Unknown attribute names return false.

State and dependencies: stateless helper functions convert flags to octal and serialize repeated location vectors. Time formatting delegates to `Printing::parseTimespec()` and `timespecToTimestamp()`. Checksum extraction delegates to `appendChecksumOnStringProtobuf()`. It uses `common::startsWith()`.

Integration points: `StringEvaluator` in `FileMetadataFilter.cc` calls this when evaluating non-literal variables in filter expressions.

Risks and test signals: absent xattrs produce an empty string but are still considered valid, enabling comparisons against empty values. `serializeLocations()` uses `int` against `vec.size()`, which is acceptable for normal protobuf repeated fields but not ideal for very large vectors. Tests should cover every supported attribute, unknown variables, missing xattrs, time byte parsing, checksum formatting, and list serialization.
