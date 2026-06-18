# sources/distributed-fs/lustre-release/lnet/utils/wirecheck.c

## Purpose
`wirecheck.c` generates C source containing compile-time `BUILD_BUG_ON()` assertions for LNet wire constants and structure layouts.

## Important APIs, Types, and Functions
The `CHECK_*` macros print assertions for constants, sizes, offsets, member sizes, and flexible-array placement. `check_lnet_handle_wire()`, `check_lnet_magicversion()`, `check_lnet_hdr_nid4()`, `check_lnet_ni_status()`, and `check_lnet_ping_info()` enumerate covered protocol structures. `system_string()` captures `uname` and compiler metadata.

## Control Flow
`main()` captures host/toolchain strings, prints the prologue of `lnet_assert_wire_constants()`, emits constant and struct assertions, and closes the generated function.

## State and Persistence Behavior
The tool persists nothing; stdout is the generated artifact. It forks shell commands and aborts on unexpected failures.

## Dependencies and Integration Points
It depends on `linux/lnet/lnet-types.h`, POSIX process/pipe APIs, `uname`, `gcc`, and the downstream build that compiles the generated assertions.

## Risks and Edge Cases
The environment capture is GCC-specific and abort-heavy, the fallback `strnlen` is only safe for currently newline-terminated `fgets()` strings, and protocol coverage must be manually extended for new wire structures or fields.

## Test Signals
Run and compile the generated output, perturb known fields to verify assertion failures, and test supported nonstandard toolchain environments if applicable.
