# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.c

Purpose: classifies decoded x86 instructions for Intel PT and BTS consumers. It identifies branch operation kind, branch target encoding, instruction length, relative displacement, and perf IP flag mapping.

Important APIs and types: exports `intel_pt_get_insn()`, `arch_is_uncond_branch()`, `dump_insn()`, `intel_pt_insn_name()`, `intel_pt_insn_desc()`, and `intel_pt_insn_type()`. Internally `intel_pt_insn_decoder()` maps x86 opcode bytes and ModRM extension fields to `INTEL_PT_OP_*` and `INTEL_PT_BR_*`.

Control flow: `intel_pt_get_insn()` calls the kernel x86 `insn_decode()` helper in 32- or 64-bit mode, rejects bad or truncated instructions, then classifies opcodes. Conditional and relative unconditional branches copy the immediate displacement with endian handling. `intel_pt_insn_type()` converts operation classes into `PERF_IP_FLAG_*` combinations used by synthesized branch samples.

State and persistence: no global mutable state except the static `branch_name` table. Each call fills a caller-owned `struct intel_pt_insn` and copies up to 16 bytes of instruction data.

Dependencies and integration: uses `arch/x86/include/asm/insn.h`, perf event/sample headers, and dump instruction helpers. It is called by Intel PT decode walking and Intel BTS branch classification.

Risks: x86 opcode coverage must track new branch-like instructions. AVX/XOP are explicitly treated as non-branch. `dump_insn()` updates `left` incorrectly by subtracting cumulative `n`, which is a possible formatting robustness issue if changed or extended. `branch_name[op]` assumes valid enum input.

Test signals: opcode fixtures for calls, returns, jcc, loops, jumps, syscall/sysret, interrupts, vmlaunch/vmresume, ERETS/ERETU, jmpabs, invalid/truncated bytes, endian displacement handling, and perf flag mapping.
