
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_x86.c

Purpose: supplies x86 register names/masks/IP/SP IDs and converts x86 SDT marker operands into uprobe-compatible register syntax.

Important APIs/types/functions: `sdt_reg_tbl` maps many GAS register spellings (`%rax`, `%eax`, byte regs, `%r8d`, etc.) to uprobe register names. `__perf_sdt_arg_parse_op_x86` accepts optional signed displacement plus one register, rejects scaled/indexed, RIP-symbol, and immediate forms, adds `+0` for bare parenthesized registers, renames registers, and returns a new uprobe operand. `__perf_reg_mask_x86` probes extended interrupt register support with `PERF_REG_EXTENDED_MASK`, adjusting config for hybrid core PMU type. `__perf_reg_name_x86` maps general/segment/control names and XMM register pairs. IP is IP and SP is SP.

Control flow: regex is compiled lazily. SDT parsing rejects operands containing comma or `$`, validates register length, builds an optional prefix, renames the register, allocates the output, and formats it. Interrupt-mask probing opens a disabled precise cycles event and includes extended regs only on success.

State and persistence: static compiled regex and initialization flag. No other state.

Dependencies: regex, x86 arch register definitions, PMU scanning for hybrid type, sys_perf_event_open, kernel perf constants, zalloc, and debug logging.

Integration points: x86 register sampling options, interrupt sample decoding, SDT probe conversion, and hybrid PMU handling.

Risks: SDT conversion intentionally skips common unsupported forms; broadening regex could create invalid uprobe syntax. Hybrid PMU type probing assumes register support is uniform across core PMUs. XMM mapping returns the same display name for paired IDs. Test signals include SDT conversion tests, `--intr-regs=?`, extended register probe tests, hybrid systems, and sample register display.
