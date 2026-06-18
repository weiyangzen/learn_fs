# sources/distributed-fs/ceph-client/include/math-emu/soft-fp.h

Purpose: Top-level GNU soft-fp configuration header. It defines guard/round/sticky work bits, rounding mode constants, exception bookkeeping defaults, classification constants, includes word-operation helpers, and exposes integer typedefs expected by `longlong.h`.

Important APIs/types/functions: `FP_DECL_EX`, `FP_INIT_ROUNDMODE`, `FP_HANDLE_EXCEPTIONS`, `FP_SET_EXCEPTION`, `FP_CLEAR_EXCEPTIONS`, `FP_CUR_EXCEPTIONS`, `_FP_ROUND_*`, `FP_CLS_*`, and `_FP_CLS_COMBINE` are the core public support macros. Rounding modes are nearest-even, toward zero, toward +inf, and toward -inf. Exception constants default to zero unless the architecture overrides them.

Control flow: Callers typically declare exceptions, initialize rounding mode, unpack operands with a format header, invoke arithmetic macros, pack the result, then handle exceptions. `_FP_ROUND` checks low work bits for inexactness and dispatches to the configured rounding strategy.

State and persistence: The only state is local `_fex` exception accumulation and macro-selected `FP_ROUNDMODE`; no global storage is introduced. `FP_INHIBIT_RESULTS` lets a target avoid writing results when traps are pending.

Dependencies and integration: Requires `<asm/sfp-machine.h>` for `_FP_W_TYPE`, `_FP_W_TYPE_SIZE`, and architecture policy; includes endian support, `op-1/2/4/8.h`, `op-common.h`, and `stdlib/longlong.h`. It integrates architecture math emulation with generic fraction primitives.

Risks and test signals: Risks include architecture overrides with incompatible exception bits, absent endian macros, and rounding mistakes in guard/sticky propagation. Test all rounding modes, trap/inhibit policies, denormal-zero policies, and builds on 32-bit and 64-bit word-size targets.
