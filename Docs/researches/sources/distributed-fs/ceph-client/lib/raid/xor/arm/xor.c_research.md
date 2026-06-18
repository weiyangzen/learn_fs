# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor.c

Purpose: implements an ARM 32-bit scalar assembly XOR template named `arm4regs`.

Important APIs and flow: macros `GET_BLOCK_2/4`, `XOR_BLOCK_2/4`, and `PUT_BLOCK_2/4` use `ldmia` and `stmia` with fixed registers. `xor_arm4regs_{2,3}` process four words per iteration; `{4,5}` reduce register pressure by processing two words per iteration. `DO_XOR_BLOCKS()` creates `xor_gen_arm4regs()`.

State and persistence: no persistence; destination memory is updated in place.

Dependencies and integration: registered from `arm/xor_arch.h` alongside generic and optional NEON templates. The code relies on ARM register allocation constraints and inline assembly clobber behavior.

Risks and test signals: risk comes from inline assembly register constraints, `lr`/`ip` use, alignment, and source count dispatch. Signals include ARM KUnit XOR tests, RAID5 parity tests, and boot calibration logs comparing `arm4regs` against generic and NEON routines.
