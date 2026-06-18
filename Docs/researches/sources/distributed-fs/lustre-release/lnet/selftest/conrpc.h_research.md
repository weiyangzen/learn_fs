# sources/distributed-fs/lustre-release/lnet/selftest/conrpc.h

## Purpose
Declares the console RPC transaction interface implemented by `conrpc.c` and used by `console.c`.

## Important APIs And Types
Defines timeout constants, `LST_VALIDATE_TIMEOUT()`, `LST_PING_INTERVAL`, `struct lstcon_rpc`, `struct lstcon_rpc_trans`, transaction opcodes (`LST_TRANS_*`), and callback typedefs `lstcon_rpc_cond_func_t` and `lstcon_rpc_readent_func_t`.

## Control Flow
The exposed contract is prepare typed RPCs or build a transaction from a node list, post/wait the transaction, interpret or summarize results, then destroy the transaction. Pinger start/stop and RPC cleanup hooks are also exported.

## State And Persistence
The header defines in-memory transaction and RPC state only. Transactions link into `console_session.ses_trans_list`; RPC wrappers are transient, pooled, or embedded in nodes.

## Dependencies And Integration Points
Includes LNet lib types, `rpc.h`, and `selftest.h`, and forward-declares console structs to avoid circular dependencies.

## Risks
New transaction opcodes must preserve the `LST_TRANS_PRIVATE` conflict rules. Timeout clamping may surprise callers expecting sub-minimum waits. User-entry callbacks must copy to user safely.

## Test Signals
Validate duplicate private transaction rejection, timeout clamping, pinger lifecycle, and clean transaction add/post/destroy behavior.
