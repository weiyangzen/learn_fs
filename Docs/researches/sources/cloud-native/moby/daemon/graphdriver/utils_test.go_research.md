# sources/cloud-native/moby/daemon/graphdriver/utils_test.go

Purpose: unit tests for storage-option key/value parsing.

Important APIs and control flow: `TestParseKeyValueOpt` checks invalid inputs `""` and `"key"` return exact error strings, then checks valid inputs with whitespace and additional `=` characters return the expected trimmed key/value pairs.

State, dependencies, and risks: no external state. The tests assert exact error text, which protects CLI/API compatibility but can make wording changes test-breaking. They do not cover empty key/value cases such as `"=value"` or `"key="`, leaving that validation to driver-specific parsers.
