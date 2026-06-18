# sources/distributed-fs/ceph-client/net/smc/smc_sysctl.c

Purpose: Registers per-network-namespace `/proc/sys/net/smc` sysctls controlling SMC buffer sizes, SMC-R buffer layout, testlink timing, link-group limits, WR queue limits, handshake limiting, autocorking, and optional BPF handshake control selection.

Important APIs/types/functions: `smc_sysctl_net_init()` clones and retargets the ctl table for non-init namespaces, registers it, and initializes defaults. `smc_sysctl_net_exit()` unregisters and frees namespace-specific tables. When `CONFIG_SMC_HS_CTRL_BPF` is enabled, `smc_net_replace_smc_hs_ctrl()` atomically swaps an RCU-protected controller by name, and `proc_smc_hs_ctrl()` exposes it as a string sysctl.

Control flow: Init namespaces use the static `smc_table`; non-init namespaces kmemdup the table and adjust each `.data` pointer by the `struct net` offset from `init_net`. Optional handshake controllers can be inherited from `init_net` when marked inheritable and module references can be taken. Sysctl handlers enforce min/max constraints on selected integer tunables. Exit unregisters the table, clears BPF handshake control, and frees cloned tables.

State and persistence behavior: State is per `struct net->smc` and visible through procfs sysctl while the namespace exists. BPF handshake controller pointers are RCU protected and module refcounted. Values reset to defaults on namespace creation.

Dependencies and integration points: Depends on sysctl infrastructure, net namespaces, SMC core constants, LLC defaults, and optional SMC handshake BPF registry. TX autocorking and WR allocation consume these values at runtime.

Risks and test signals: Risks include pointer-retargeting mistakes in cloned ctl tables, teardown ordering of BPF controllers, invalid WR limits, and namespace inheritance surprises. Test init and non-init netns sysctl reads/writes, min/max rejection, namespace teardown, BPF controller set/clear/inherit behavior, and runtime effects on autocorking, buffer type, link-group limits, and WR queue sizing.
