
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_aarch64.c

Purpose: supplies Arm64 register sampling masks, register names, instruction-pointer/stack-pointer IDs, and SDT argument conversion.

Important APIs/types/functions: `__perf_sdt_arg_parse_op_arm64` supports SDT operands `x0`-`x31` and `[sp]`/`[sp, NUM]`, converting them to uprobe-style `%xN` or `+offset(%sp)`. `__perf_reg_mask_arm64` returns the base mask and conditionally includes `PERF_REG_ARM64_VG` when SVE is advertised and accepted by a probe `perf_event_open`. `__perf_reg_name_arm64` maps x0-x29, sp, lr, pc, and vg. `__perf_reg_ip_arm64` and `__perf_reg_sp_arm64` return PC/SP IDs.

Control flow: regexes are compiled once lazily. SDT parsing matches register or stack forms and skips unsupported operands. Register-mask probing builds a disabled cycles event with requested user regs and falls back when the kernel rejects extended registers.

State and persistence: static regex objects and an initialized flag persist. No other state.

Dependencies: regex, auxv `AT_HWCAP`, sys_perf_event_open, Arm64 perf register definitions, kernel perf constants, and debug logging.

Integration points: used by perf register option parsing, sample decoding, and SDT probe argument setup on Arm64.

Risks: SVE VG availability depends on both hardware and kernel attr support. Regex supports only a subset of possible SDT operand syntax. Test signals include register name/mask tests, SVE-capable kernel probing, and SDT conversion cases for x registers and stack offsets.
