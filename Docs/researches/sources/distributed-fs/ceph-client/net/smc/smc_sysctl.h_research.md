# sources/distributed-fs/ceph-client/net/smc/smc_sysctl.h

Purpose: Declares SMC sysctl namespace lifecycle hooks and provides no-sysctl fallback initialization for key SMC tunables.

Important APIs/types/functions: With `CONFIG_SYSCTL`, `smc_sysctl_net_init()` and `smc_sysctl_net_exit()` are external functions. Without sysctl support, inline `smc_sysctl_net_init()` initializes defaults for autocorking, link-group limits, connection limits, and SMC-R WR queue sizes, while exit is a no-op.

Control flow: SMC net namespace setup calls the init function regardless of configuration. The preprocessor selects either procfs-backed registration or direct default assignment.

State and persistence behavior: State is stored in `net->smc` fields. In no-sysctl builds there is no runtime procfs persistence or user adjustment surface.

Dependencies and integration points: Depends on SMC constants from included code and `struct net`. It is consumed by SMC namespace initialization code and by runtime logic that reads the tunables.

Risks and test signals: Risk is default drift between the full sysctl implementation and the fallback inline path. Build both `CONFIG_SYSCTL=y` and `n`, verify defaults match expected operational values, and run connection setup and WR allocation under no-sysctl builds.
