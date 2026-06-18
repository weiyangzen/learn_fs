
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_powerpc.c

Purpose: supplies PowerPC register names, IP/SP IDs, interrupt-register mask probing for recent POWER CPUs, and SDT operand conversion.

Important APIs/types/functions: `__perf_sdt_arg_parse_op_powerpc` converts register and displacement forms such as `18`, `%r18`, `48(18)`, and `-48(%r18)` into uprobe `%gprN` syntax, while skipping immediate `iNUM` constants. `__perf_reg_mask_powerpc` returns base mask for user regs; on PowerPC builds it probes PMU extended interrupt registers based on PVR for POWER9, POWER10, and POWER11. `__perf_reg_name_powerpc` maps r0-r31, NIP, MSR, orig_r3, CTR, LINK, XER, CCR, SOFTE, TRAP, DAR, DSISR, SIER/MMCR/PMC/SDAR/SIAR extended names. IP is NIP and SP is R1.

Control flow: SDT regexes are compiled once; operands are matched against register or displacement forms. Interrupt-mask probing reads PVR, chooses the extended mask, opens a disabled precise cycles event with `sample_regs_intr`, and includes the mask only if the kernel accepts it.

State and persistence: static regex objects/flag. No other persistent state.

Dependencies: regex, PowerPC PVR/mfspr utilities, sys_perf_event_open, arch register definitions, kernel perf constants, and debug logging.

Integration points: register sampling on PowerPC, SDT probe conversion, and sample display for extended PMU registers.

Risks: PVR handling is compiled only for native PowerPC; cross-build fallback returns base mask. New POWER generations require updated PVR/mask logic. SDT supports only a subset of operand forms. Test signals include SDT operand conversion tests, register list output, POWER9/10/11 extended interrupt register probe tests, and sample decoding.
