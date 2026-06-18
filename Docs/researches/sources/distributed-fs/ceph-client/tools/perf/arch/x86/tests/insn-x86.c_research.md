# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86.c

Purpose: This file implements the runtime perf test for x86 instruction decoding and Intel PT instruction classification. It consumes the generated instruction byte tables from `insn-x86-dat-32.c` and `insn-x86-dat-64.c`, decodes each instruction in the kernel x86 instruction decoder, and cross-checks Intel PT's higher-level operation and branch categorization.

Important APIs, types, and functions: `struct test_data` stores the bytes, expected decoded length, expected relative target, expected Intel PT op string, expected branch string, and assembler rendering. `get_op()` maps strings such as `call`, `ret`, `jcc`, `syscall`, `vmentry`, `erets`, and `eretu` to `enum intel_pt_insn_op` values. `get_branch()` maps `indirect`, `conditional`, and `unconditional` strings to Intel PT branch classes. `test_data_item()` performs one decode and comparison. `test_data_set()` iterates a sentinel-terminated array. `test__insn_x86()` is the exported test-suite entry point.

Control flow: `test__insn_x86()` runs the 32-bit data set with `INSN_MODE_32`, then the 64-bit data set with `INSN_MODE_64`. For each item, `insn_decode()` validates instruction length, then `intel_pt_get_insn()` validates the Intel PT operation, branch type, and relative displacement. The loop continues through all entries even if one item fails, preserving multiple debug messages before returning failure.

State and persistence: State is local to the test invocation. The static arrays are generated at build time and included into the binary. No external files are read at runtime, and no persistent state is written. The sentinel item with `expected_length == 0` terminates each array.

Dependencies and integration points: The test depends on `arch/x86/include/asm/insn.h` for `struct insn` and `insn_decode()`, `intel-pt-decoder/intel-pt-insn-decoder.h` for `intel_pt_get_insn()`, and perf test infrastructure headers for result conventions and debug logging. It is registered through the x86 arch test suite (`arch-tests.c`) under "x86 instruction decoder - new instructions". It also depends on the generator pipeline documented in the source-data file.

Risks: String-to-enum maps must stay synchronized with Intel PT decoder enum additions; new operation classes require updates here or generated expectations will fail with `-1`. The test assumes generated data files match the current source corpus and current decoder behavior. Unsupported instruction bytes or mode-specific decode changes can cause length or relative-address mismatches.

Test signals: `perf test -v "x86 instruction decoder - new instructions"` shows per-instruction "Decoded ok" or detailed failure messages for length, op, branch, or `rel`. Build failures can indicate stale generated files or missing enum support for a new expected op.
