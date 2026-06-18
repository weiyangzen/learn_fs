# sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.c

## Purpose
`smc_hs_bpf.c` adds BPF `struct_ops` support for SMC handshake control. It allows validated BPF-provided `struct smc_hs_ctrl` instances to be registered by name and later found by handshake code under RCU.

## Important APIs, Types, and Functions
The file maintains `smc_hs_ctrl_list` protected by `smc_hs_ctrl_list_lock` and read via RCU. `smc_hs_ctrl_reg()` rejects duplicate names and adds controls with `list_add_tail_rcu()`. `smc_hs_ctrl_unreg()` deletes with `list_del_rcu()` and waits for `synchronize_rcu()`. `smc_hs_ctrl_find_by_name()` is the exported lookup helper. BPF integration is provided by `bpf_smc_hs_ctrl_ops`, `smc_bpf_hs_ctrl_reg()`, `smc_bpf_hs_ctrl_unreg()`, `smc_bpf_hs_ctrl_init_member()`, and `bpf_smc_hs_ctrl_init()`.

## Control Flow
At SMC initialization, `bpf_smc_hs_ctrl_init()` registers the `smc_hs_ctrl` struct_ops type. A BPF struct_ops registration is copied and validated member-by-member; only `name` and `flags` receive special initialization, with flags masked by `SMC_HS_CTRL_ALL_FLAGS`. Registration refuses bpf_link-backed attach (`-EOPNOTSUPP`) and inserts the object into the global RCU list. Consumers call `smc_hs_ctrl_find_by_name()` while holding `rcu_read_lock()`.

## State and Persistence
State is the in-memory RCU list of registered handshake controllers. The code uses static CFI stub callbacks that return success-like values, making indirect-call validation safe before BPF implementations are attached. No persistent storage exists.

## Dependencies and Integration Points
The implementation depends on BPF verifier, BTF, BPF struct_ops, RCU list APIs, and `net/smc.h` for `struct smc_hs_ctrl`. It is compiled only when `CONFIG_SMC_HS_CTRL_BPF` is enabled, with a no-op inline init in the header otherwise. Handshake code can look up named controls without depending on BPF details.

## Risks
The lookup contract requires callers to hold `rcu_read_lock()`; violating that can race unregister. Duplicate-name prevention is under a spinlock but lookup itself is RCU, so all list updates must keep the unregister synchronize point. Member initialization currently accepts only name and flags specially; future `struct smc_hs_ctrl` fields need explicit verifier/copy semantics. Returning `-EOPNOTSUPP` for link-backed registrations should match expected user-space attach behavior.

## Test Signals
Test with `CONFIG_SMC_HS_CTRL_BPF=y`, register a valid struct_ops controller, reject duplicate names and invalid flags, unregister while concurrent lookups run, and confirm SMC init succeeds with and without the config. BPF verifier tests should check name-copy failure, flag masks, and allowed helper prototypes.
