# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataFiltering.cc

Purpose: Unit tests for metadata attribute extraction and filter expression evaluation/parsing on `FileMdProto`.
Important APIs/types/functions: `StringEvaluator`, `AttributeExtraction::asString`, `EqualityFileMetadataFilter`, `LogicalMetadataFilter`, `FilterExpressionLexer`, and `FilterExpressionParser`.
Control flow: tests literal/variable evaluation, invalid variables, extraction of IDs, uid/gid, size, layout, flags, names, timestamps, checksum, locations, and unlinked locations; then checks equality, inequality, logical AND/OR, lexical tokenization, mismatched quotes, parentheses, and parser output descriptions.
State/persistence: no backend state; all data is in a local protobuf.
Dependencies/integration: uses generated file metadata protobuf, layout ID helper, inspector filter/extraction classes, and GTest.
Risks: tests compare exact human-readable `describe()` strings, so harmless formatting changes break them; checksum extraction expects a shortened hex representation; parser coverage here is positive/basic and not exhaustive for invalid grammar.
Test signals: good unit-level coverage of inspector filtering behavior used to scan/select metadata by attributes.
