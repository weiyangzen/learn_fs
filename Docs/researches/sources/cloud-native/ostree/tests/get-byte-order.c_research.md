<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/get-byte-order.c -->
## sources/cloud-native/ostree/tests/get-byte-order.c

Purpose: tiny build helper used by shell tests to report host byte order for GLib variant metadata expectations.

Important APIs/functions: includes GLib or platform byte-order macros and prints the numeric byte-order value expected by tests.

Control flow/state: no state; single-process command returns one value to stdout.

Dependencies/integration: built under the test builddir and invoked by `basic-test.sh` when checking endian-sensitive `uint64` metadata display with and without byte-swapping.

Risks/test signals: must match the constants the shell test branches on (`4321` big-endian, `1234` little-endian). Failure makes metadata tests misdiagnose byte-order behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/get-byte-order.c -->
