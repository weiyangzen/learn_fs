# sources/distributed-fs/ceph-client/arch/s390/kernel/reipl.S

Purpose: provides the low-level `store_status` routine used around restart/re-IPL paths to store the current CPU status into lowcore and then branch to a caller-provided function.

Important APIs/symbols: defines `store_status` as `SYM_CODE_START(store_status)` and a local BSS `clkcmp` scratch word. It uses lowcore save-area offsets from `asm/asm-offsets.h` and branch thunk support from `asm/nospec-insn.h`.

Control flow: caller passes a function pointer in `%r2` and an argument in `%r3`. The routine stores GPRs, obtains the lowcore pointer, stores control registers, access registers, floating-point registers, FPC, CPU timer, prefix register, seven bytes of clock comparator, and a PSW image. It records the callback address in the saved PSW area, moves the argument into `%r2`, and branches through `%r9` with `BR_EX`.

State and persistence: writes architectural register state into the current CPU lowcore save areas. This is machine restart/status state rather than filesystem persistence.

Dependencies and integration points: depends on lowcore layout, s390 register-save instructions, restart/re-IPL callers, nospec branch thunk generation, and code that later consumes stored status from lowcore.

Risks: offsets and register ordering must match lowcore definitions exactly. The routine runs in a sensitive restart context and cannot rely on normal C calling conventions beyond the documented register inputs. Clock comparator handling intentionally copies seven bytes; changing it can break architectural status layout.

Test signals: restart/re-IPL and dump flows should see complete stored status, callback invocation should receive the original parameter in `%r2`, and saved lowcore register areas should match hardware state during crash/restart validation.
