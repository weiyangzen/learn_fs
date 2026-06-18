# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_matchall.c

## Purpose
This file implements TC matchall offload for Spectrum flow blocks. It supports block-wide mirror and sample actions, binds them to every port currently attached to a flow block, maintains priority constraints relative to flower rules, and supplies generation-specific sampling implementations.

## Important APIs, Types, And Functions
Public entry points are `mlxsw_sp_mall_replace()`, `mlxsw_sp_mall_destroy()`, `mlxsw_sp_mall_port_bind()`, `mlxsw_sp_mall_port_unbind()`, and `mlxsw_sp_mall_prio_get()`. Internal helpers manage entry lookup, SPAN mirror add/delete, sample trigger parameter set/unset, per-port rule add/delete, priority min/max recomputation, and Spectrum-1/Spectrum-2 sample ops. `mlxsw_sp1_mall_ops` programs MPSC sampling and supports ingress only; `mlxsw_sp2_mall_ops` uses a CPU SPAN session and supports ingress/egress triggers.

## Control Flow
Replace validates one action, chain 0, non-mixed binding, and `ETH_P_ALL`, then checks flower priority ordering. It allocates a mall entry from the TC cookie/action, applies the action to each bound port, rolls back already-bound ports on failure, increments rule/blocker counters, links the entry, and updates min/max priorities. Destroy unlinks by cookie, decrements counters, removes the action from bound ports, and frees via RCU because sampled RX packets can still reference the entry. Port bind/unbind replay or remove all mall entries for a single port.

## State And Persistence
State is stored in the flow block's `mall.list`, min/max priority fields, rule count, and ingress/egress blocker counters. Per-entry state includes cookie, priority, ingress flag, mirror target/SPAN ID, or sample params/SPAN ID. Hardware state includes SPAN agents, analyzed-port refs, sample trigger parameters, MPSC register state, and Spectrum-2 CPU SPAN bindings.

## Dependencies And Integration Points
The file depends on flow-offload action parsing, Spectrum flow-block binding lists, SPAN infrastructure, psample trigger parameter management, and hardware registers MPSC for Spectrum-1. It coordinates with `spectrum_flower.c` through bidirectional priority checks.

## Risks And Edge Cases
Matchall and flower priority constraints differ for ingress and egress and must remain symmetric. Rollback relies on list iterator position after a failed per-port add. RCU free is required for in-flight sampled packets. Spectrum-1 sampling rejects egress and out-of-range MPSC rates. The checked-out source shows a duplicated priority-comparison line in the egress flower conflict branch, a compile-risk signal in this tree.

## Test Signals
Exercise matchall mirror/sample add/delete, port bind/unbind replay, rollback by injecting SPAN/sample failures, flower priority conflicts, Spectrum-1 ingress-only sampling rejection, Spectrum-2 CPU sampling, RCU teardown under sampled traffic, and mixed ingress/egress binding rejection.
