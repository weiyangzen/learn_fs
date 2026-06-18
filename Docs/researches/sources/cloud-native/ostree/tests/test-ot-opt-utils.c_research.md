<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-opt-utils.c -->
# sources/cloud-native/ostree/tests/test-ot-opt-utils.c

## Purpose
`test-ot-opt-utils.c` unit-tests option utility error reporting.

## Important APIs, Types, And Functions
It uses a custom `printerr` capture string and tests `ot_util_usage_error` from `ot-opt-utils.h`.

## Control Flow
The test redirects or captures printerr output, calls `ot_util_usage_error` with invalid usage input, and asserts the generated error text and return/error state match expectations.

## State And Persistence
State is limited to an in-memory `GString *printerr_str` and `GError` values. No files are written.

## Dependencies And Integration Points
This validates helper behavior used by CLI option parsing paths to report usage failures consistently.

## Risks And Test Signals
The test is wording-sensitive but intentionally so for CLI diagnostics. Passing signals include a populated usage error, expected stderr text, and no unexpected GLib assertion failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-opt-utils.c -->
