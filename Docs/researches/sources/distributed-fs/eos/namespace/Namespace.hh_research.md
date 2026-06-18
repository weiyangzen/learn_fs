## sources/distributed-fs/eos/namespace/Namespace.hh

Purpose: Defines namespace macros for EOS namespace code.

Important APIs and macros: `EOSNSNAMESPACE_BEGIN` expands to `namespace eos {`, `EOSNSNAMESPACE_END` closes it, and `USE_EOSNSNAMESPACE` imports `eos`.

Control flow: no runtime behavior.

State and persistence: no state. The file only affects source organization and symbol namespace.

Dependencies and integration: included by most namespace interface/support headers to keep namespace declarations uniform.

Risks: macro-based namespace boundaries can hide mismatched braces during review. `USE_EOSNSNAMESPACE` introduces a using-directive and should be avoided in headers outside controlled scope.

Test signals: compile tests for namespace headers and include-order checks.
