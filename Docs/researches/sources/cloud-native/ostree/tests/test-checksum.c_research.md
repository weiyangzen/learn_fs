# sources/cloud-native/ostree/tests/test-checksum.c

Purpose: tests parsing of static delta name strings into from/to checksums.

Important APIs/functions: `ostree_parse_delta_name`, GLib `g_assert_cmpstr`, `g_assert_null`, and `g_test_add_func`.

Control flow: feeds valid one-ended and two-ended delta names and several invalid forms into the parser. It checks expected `from` and `to` checksum pointers for each case, including null values when parsing should fail or represent an empty-from delta.

State/persistence: no persistent state; all allocations are local strings. Dependencies include libostree checksum/delta parser code and GLib tests.

Integration/risk/test signals: protects CLI and repo code that interprets `FROM-TO` delta identifiers. Risks are limited cases and dependence on fixed checksum constants. The `/ostree_parse_delta_name` GLib test is the signal.
