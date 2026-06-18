<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode.h

Purpose: declares the shared decode-table ABI for ARM probes and defines inline helpers for PC writes, interworking, writeback detection, decode entry construction, checker/action types, and instruction decode result codes.

Important APIs and types: exports `arm_probes_decode_init()`, `probes_condition_checks`, `probes_simulate_nop`, `probes_emulate_none`, and `probes_decode_insn()`. Core types include `enum decode_type`, `enum decode_reg_type`, `union decode_item`, `union decode_action`, `struct decode_header`, `struct decode_table`, `struct decode_custom`, `struct decode_simulate`, `struct decode_emulate`, `struct decode_or`, `struct decode_reject`, and `struct decode_checker`. The `REGS()` macro encodes five register-field policies into table metadata.

Control flow: table users build arrays of `union decode_item` with macros such as `DECODE_TABLE`, `DECODE_CUSTOM`, `DECODE_SIMULATEX`, `DECODE_EMULATEX`, `DECODE_OR`, `DECODE_REJECT`, and `DECODE_END`. The runtime decoder consumes those arrays and interprets each header by type. `bx_write_pc()`, `load_write_pc()`, and `alu_write_pc()` centralize ARM/Thumb interworking semantics after simulated or emulated instructions write PC.

State and persistence: the header chooses compile-time constants for `str_pc_offset`, `load_write_pc_interworks`, and `alu_write_pc_interworks` when the configured architecture makes them invariant, otherwise it declares runtime variables and init probes in `decode.c`.

Dependencies and integration: includes Linux type definitions, `asm/probes.h`, `asm/ptrace.h`, and `asm/kprobes.h`. Decode tables in `decode-arm.h` and `decode-thumb.h`, kprobe actions, and checker modules all depend on these definitions.

Risks: table layout is binary-encoded through macros and struct size assumptions; adding a decode type requires updating size tables in both `decode.c` and `test-core.c`. Register policy aliases `NOPCX` and `NOSPPCX` exist partly for coverage semantics, so collapsing them can reduce test precision. PC-write helper behavior varies by architecture and must match ARM ARM interworking rules.

Test signals: table consistency and coverage tests inspect these structures directly. Supported/rejected instruction cases verify that `REG_TYPE_*` policies reject SP/PC/writeback combinations as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.h -->
