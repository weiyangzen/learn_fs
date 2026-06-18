## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/disassemble.h

Purpose: provides small PowerPC instruction field extractors and DSISR synthesis for fault emulation paths.

Important APIs/types/functions: `get_op()`, `get_xop()`, `get_sprn()`, `get_dcrn()`, `get_tmrn()`, `get_rt()`, `get_rs()`, `get_ra()`, `get_rb()`, `get_rc()`, `get_ws()`, `get_d()`, `get_oc()`, `get_tx_or_sx()`, `IS_XFORM()`, `IS_DSFORM()`, and `make_dsisr()`.

Control flow: helpers shift and mask fixed instruction fields. `make_dsisr()` maps instruction bits into a DSISR-style value, with different bit routing for X-form versus D/DS-form instructions.

State and persistence: stateless computations over a 32-bit instruction word.

Dependencies and integration: depends only on Linux integer types. Used by exception, emulation, alignment, and data-storage interrupt handling code that needs to decode faulting instructions.

Risks and test signals: bit extraction must match the ISA exactly; DSISR synthesis errors break fault handling and emulation. Test signals include alignment/fault emulation tests, instruction decoder unit tests where available, KVM/emulation coverage, and randomized comparison against an authoritative decoder.
