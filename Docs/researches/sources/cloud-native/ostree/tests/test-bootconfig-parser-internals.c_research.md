# sources/cloud-native/ostree/tests/test-bootconfig-parser-internals.c

Purpose: tests internal bootconfig parser helpers by including `ostree-bootconfig-parser.c` directly.

Important APIs/functions: `parse_bootloader_tries`, `OstreeBootconfigParser`, `ostree_bootconfig_parser_set/get`, `_ostree_bootconfig_parser_get_extra_keys_variant`, `_ostree_bootconfig_parser_set_extra_keys_from_variant`, `parse_at`, and `write_at`.

Control flow: validates valid and invalid boot counting suffix parsing, verifies standard BLS keys are excluded from extra-key variants, preserves extension/custom keys, roundtrips extra keys through variants, and parses/writes a BLS file while keeping extension keys.

State/persistence: mostly in-memory parser objects; one test writes temporary BLS files and rereads them. Dependencies include GLib and private source inclusion, so it tracks internal implementation closely.

Integration/risk/test signals: protects boot counting and BLS extension metadata preservation. Risks are tight coupling to private functions and standard-key list changes. GLib test paths under `/bootconfig-parser/...` signal success.
