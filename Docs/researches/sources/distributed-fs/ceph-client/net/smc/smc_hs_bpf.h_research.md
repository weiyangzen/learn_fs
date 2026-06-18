# sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.h

## Purpose
`smc_hs_bpf.h` declares the handshake-control lookup and conditional BPF struct_ops initialization hook for SMC handshake customization.

## Important APIs, Types, and Functions
The header exposes `smc_hs_ctrl_find_by_name(const char *name)` and `bpf_smc_hs_ctrl_init()`. The lookup comment documents that `name` must be a C string and callers must hold `rcu_read_lock()`. When `CONFIG_SMC_HS_CTRL_BPF` is disabled, `bpf_smc_hs_ctrl_init()` is an inline no-op returning 0.

## Control Flow
SMC initialization can call `bpf_smc_hs_ctrl_init()` without config-specific branches. Handshake code can search for a named `struct smc_hs_ctrl`, but the implementation expects the caller to provide RCU read-side protection.

## State and Persistence
The header owns no state. It defines access to an implementation-managed RCU list when BPF support is enabled.

## Dependencies and Integration Points
It includes `net/smc.h` for `struct smc_hs_ctrl` and is implemented by `smc_hs_bpf.c`. It is an integration seam between core SMC handshake code and optional BPF struct_ops support.

## Risks
The most important risk is misuse of the RCU contract. A caller that stores the returned pointer after leaving the read-side critical section can race unregister. The no-op init path also means feature availability must be checked by registration/lookup behavior, not by init success alone.

## Test Signals
Build both enabled and disabled BPF configurations. Confirm callers compile without conditional code, lookup returns NULL for absent names, and RCU usage is covered by lockdep or targeted concurrency tests.
