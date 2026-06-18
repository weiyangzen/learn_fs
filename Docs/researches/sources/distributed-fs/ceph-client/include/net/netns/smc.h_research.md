# sources/distributed-fs/ceph-client/include/net/netns/smc.h

Purpose: Defines per-network-namespace SMC protocol state.

Important APIs/types/functions: `struct netns_smc` stores per-cpu SMC stats, `mutex_fback_rsn`, fallback reason stats, `limit_smc_hs`, optional sysctl header, optional BPF handshake-control pointer, and sysctls for autocorking, buffer type, testlink time, send/receive memory, max links/connections per link group, and SMCR send/receive work requests.

Control flow: SMC init allocates stats and sysctls. Protocol paths update per-cpu stats, protect fallback reason updates with the mutex, consult handshake limits/BPF control, and read namespace sysctls for link group and buffer behavior.

State and persistence: Runtime per-net stats, fallback reason state, handshake-control pointer, and sysctl values.

Dependencies/integration: Depends on SMC core, sysctl/proc integration, socket lifecycle, and namespace teardown.

Risks/test signals: Test per-net sysctls, fallback reason locking, BPF handshake control RCU lifetime, stats cleanup, handshake limit enforcement, disabled config behavior, and namespace isolation.
