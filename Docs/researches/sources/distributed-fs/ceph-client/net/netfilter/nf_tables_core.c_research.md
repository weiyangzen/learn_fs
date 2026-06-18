# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_core.c

## Purpose
`nf_tables_core.c` is the nftables packet interpreter and core expression/object bootstrap for the Ceph-client Linux source mirror. It executes a packet through a prepared `struct nft_chain` rule blob, dispatches expression evaluators, handles nftables verdicts, emits trace notifications, updates base-chain counters, and registers the built-in expression/object types needed by nftables rules.

## Important APIs, Types, and Functions
The exported hot-path API is `nft_do_chain(struct nft_pktinfo *pkt, void *priv)`. It consumes `struct nft_pktinfo`, `struct nft_chain`, `struct nft_rule_blob`, `struct nft_rule_dp`, `struct nft_expr`, `struct nft_regs`, `struct nft_verdict`, `struct nft_traceinfo`, and the local `struct nft_jumpstack`.

Fast inlined evaluators are `nft_bitwise_fast_eval()`, `nft_cmp_fast_eval()`, `nft_cmp16_fast_eval()`, and `nft_payload_fast_eval()`. Generic expression dispatch goes through `expr_call_ops_eval()`, with retpoline mitigation support via `nf_tables_skip_direct_calls` and known direct-call comparisons for common expression evaluators. Tracing helpers are `nft_trace_packet()`, `nft_trace_copy_nftrace()`, `nft_trace_verdict()`, and `__nft_trace_verdict()`. Counter handling is guarded by `nft_counters_enabled` and implemented in `nft_update_chain_stats()`.

Initialization APIs are `nf_tables_core_module_init()` and `nf_tables_core_module_exit()`, which register and unregister the built-in expression types and stateful object types.

## Control Flow, State, and Persistence
`nft_do_chain()` selects either `chain->blob_gen_0` or `chain->blob_gen_1` using the per-net generation cursor, then walks rule data until the sentinel `is_last` rule. For each rule it resets `regs.verdict.code` to `NFT_CONTINUE`, evaluates expressions in rule order, and stops evaluation when an expression changes the verdict. `NFT_BREAK` means the rule did not match and scanning continues at the next rule; `NFT_CONTINUE` traces the matching rule and continues. Terminal netfilter verdicts return immediately, with `NF_DROP` translated to a drop reason.

`NFT_JUMP` stores the next rule on the bounded jump stack and falls through to `NFT_GOTO`; `NFT_GOTO` switches to the verdict chain and restarts at that chain's selected blob. `NFT_RETURN` or end-of-chain unwinds the jump stack. If no jump remains, the base-chain policy is traced, base-chain stats are optionally updated, and the policy is returned with drop reason wrapping for drop policies.

State is mostly per-packet stack state plus RCU-protected chain blobs. Persistent state includes registered expression/object types, static keys for tracing/counters/retpoline behavior, per-chain percpu stats, and per-net generation-selected rule blobs.

## Dependencies and Integration Points
The interpreter depends on nftables core headers, `nf_tables_trace.c` for `nft_trace_notify()`/`nft_trace_init()`, expression implementations such as payload, cmp, counter, meta, lookup, byteorder, bitwise, dynset, rt, object reference, and conntrack fast get, and the netfilter hook wrappers in the chain type files. Base-chain counter state is updated through `struct nft_base_chain`.

## Risks and Test Signals
Main risks are rule-blob RCU lifetime, expression size iteration, register aliasing, bounded jump-stack overflow, policy/drop reason correctness, and fast-path evaluators staying behaviorally identical to generic ops. Useful tests exercise nested jump/goto/return, `NFT_BREAK` matching, generation switching during rule replacement, trace messages for rule/return/policy paths, counters under load, retpoline direct-call toggling, payload fast failures on fragments or short skbs, and all built-in type registration rollback paths.
