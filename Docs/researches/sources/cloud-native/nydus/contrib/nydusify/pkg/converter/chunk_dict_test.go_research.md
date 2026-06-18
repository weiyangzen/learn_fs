# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict_test.go

Purpose: tests chunk dictionary argument parsing.

Important APIs and flow: success cases cover registry refs with tags and local absolute paths. Failure cases cover too few fields, invalid format, and invalid source, asserting specific error text.

State and persistence: pure in-memory.

Dependencies and integration: protects converter CLI/config parsing for chunk dictionary references.

Risks and test signals: adequate for current grammar. It does not cover Windows-style paths or future formats/sources.
