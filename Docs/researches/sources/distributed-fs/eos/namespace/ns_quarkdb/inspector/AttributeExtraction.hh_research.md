## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.hh

Purpose: Declares the inspector helper for extracting file metadata attributes into strings.

Important API: `AttributeExtraction::asString(const FileMdProto&, const std::string& attr, std::string& out)` returns whether the attribute name is supported and writes the string representation to `out`. The class is purely static and has no owned state.

Dependencies and integration: depends on EOS namespace macros and the `FileMdProto` protobuf. It is consumed by file metadata filters and any inspector code that needs uniform string representations for metadata fields.

Risks and test signals: the API distinguishes unsupported attribute names from supported-but-empty values, so callers should inspect the boolean rather than just `out`. Tests should verify this contract for missing xattrs and unknown field names.
