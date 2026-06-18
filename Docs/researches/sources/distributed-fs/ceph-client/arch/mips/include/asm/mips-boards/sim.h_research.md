# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sim.h

Purpose: Simulator control hook for MIPS board simulation environments.

Important APIs/types/functions: Defines simulator command codes `STATS_ON`, `STATS_OFF`, `STATS_CLEAR`, `STATS_DUMP`, `TRACE_ON`, and `TRACE_OFF`. The `simcfg(code)` macro emits inline assembly that loads the command code into `$4`, emits magic word `0x39`, and declares `$4` clobbered.

Control flow, state, and persistence: `simcfg` is a direct simulator escape instruction. Persistent effects are external to Linux, in the simulator’s statistics/trace state.

Dependencies and integration: Used by simulation-specific board/test code. It assumes a simulator that interprets the magic instruction; on real hardware this would be invalid or meaningless.

Risks and test signals: Use outside the intended simulator can fault. Test only under supported simulators by toggling stats/trace and verifying expected simulator output without corrupting register state.
