# sources/distributed-fs/ceph-client/arch/arm/mm/abort-macro.S

Purpose: provides shared assembly macros for early abort handlers that must classify Thumb `LDRSB` and ARM `LDRD` correctly despite nonstandard use of load/write indicator bits.

Important APIs/types/functions: defines `.macro do_thumb_abort, fsr, pc, psr, tmp` and `.macro teq_ldrd, tmp, insn`. `do_thumb_abort` reads the aborted Thumb instruction, masks opcode bits, recognizes `LDRSB`, adjusts the effective load bit, marks write faults in FSR, and branches to `do_DataAbort`. `teq_ldrd` tests the ARM `LDRD` encoding pattern.

Control flow: included abort handlers call `do_thumb_abort` before ARM-state instruction decode. If PSR is not Thumb, the macro falls through at `not_thumb`; otherwise it completes handling by branching to the common abort path. `teq_ldrd` sets condition flags for caller branches.

State and persistence: no runtime state; this is compile-time macro text. It operates on caller-supplied registers and condition flags.

Dependencies and integration points: included by ARMv4T, ARMv5T, ARMv5TJ, and ARMv6 abort handlers. Depends on `PSR_T_BIT`, `uaccess_disable`, and `do_DataAbort`.

Risks: macro register arguments must not conflict with caller live registers. Wrong decode masks would misclassify read faults as writes or vice versa, causing incorrect permission signals.

Test signals: assemble all including abort handlers, run Thumb `LDRSB` and ARM `LDRD` abort tests, and inspect generated code for correct fallthrough and branch behavior.
