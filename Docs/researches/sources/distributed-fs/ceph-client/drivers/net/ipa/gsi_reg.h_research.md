# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_reg.h

Purpose: Defines the GSI register ID namespace, register field IDs, hardware enum values, IRQ bit definitions, error codes, and register API declarations used by `gsi.c` and `gsi_reg.c`.

Important APIs/types: `enum gsi_reg_id` enumerates all GSI registers used by the driver. Field ID enums describe per-register fields such as channel context, event context, QOS, command opcodes, hardware parameters, interrupt masks/status, error logs, and scratch results. Hardware enums cover channel/event states, channel protocol types, prefetch modes, command opcodes, generic command results, interrupt types, global/general IRQ bits, and error types/codes. Extern `gsi_regs_v*` declarations provide version-specific register tables.

Control flow and integration: Implementation code never hard-codes most bit positions; it requests a `struct reg` and uses `reg_encode()`, `reg_decode()`, `reg_bit()`, and offsets. Version-specific register tables plug into this common ID/field contract. `gsi_reg_init()` and `gsi_reg()` are the public register helpers for the GSI implementation.

State and persistence: Header-only constants and declarations. Runtime state is in `struct regs` selected by `gsi_reg.c` and in hardware registers written by `gsi.c`.

Dependencies: Includes Linux bit helpers and forward-declares platform/GSI structs. Depends on generic register abstraction in `reg.h` and on version table definitions in the IPA register data files.

Risks: Field ID mismatches against version-specific `struct reg` definitions can encode wrong bits with no type-system protection. Comments mark version-gated fields such as `GENERIC_PARAMS`, `HW_PARAM_4`, `CH_ERINDEX`, `DB_IN_BYTES`, and `LOW_LATENCY_EN`; changes must be cross-checked with `gsi_reg_id_valid()` and channel programming.

Test signals: Build coverage across all version register tables, runtime probe on each supported IPA version, and logs free of invalid-register WARNs. Hardware tests should include command start/stop/reset, event processing, flow control, and error interrupt decode paths.
