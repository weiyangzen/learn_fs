<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest-core.sh -->
## sources/cloud-native/ostree/tests/libtest-core.sh

Purpose: canonical core shell assertion library for OSTree tests.

Important APIs/functions: provides `fatal`, TAP helpers, equality/regex assertions, file/dir/content/mode/whiteout/symlink assertions, `skip`, and an ERR trap that reports the failing command.

Control flow/state: normalizes locale to UTF-8, unsets `LANGUAGE`, exports `G_DEBUG=fatal-warnings`, and increments a TAP counter through `tap_ok()`.

Dependencies/integration: sourced by `libtest.sh` and related shell tests. Its diagnostics are intentionally file-content rich for CI logs.

Risks/test signals: assertion behavior is foundational; any change can affect many tests. Exact regex handling and command trap behavior are central test signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest-core.sh -->
