
# sources/distributed-fs/ceph-client/net/netfilter/nf_hooks_lwtunnel.c

Purpose: Provides sysctl-controlled enablement for netfilter hooks in lightweight tunnel paths.

Important APIs and functions: `nf_hooks_lwtunnel_sysctl_handler()` reads or writes the `nf_hooks_lwtunnel` sysctl. Internal helpers `nf_hooks_lwtunnel_get()` and `nf_hooks_lwtunnel_set()` access the static key `nf_hooks_lwtunnel_enabled`. `netfilter_lwtunnel_init()` and `netfilter_lwtunnel_fini()` register/unregister per-net sysctl tables when `CONFIG_SYSCTL` is enabled.

Control flow: Reads report whether the static key is active. Writes pass through `proc_dointvec_minmax()` with 0/1 bounds. Enabling turns on the static branch; disabling after enable returns `-EBUSY`, making the feature effectively one-way for the boot/module lifetime.

State and persistence: State is the global static branch plus per-net sysctl table registrations. There is no durable persistence.

Dependencies and integration: Depends on `CONFIG_LWTUNNEL`, `CONFIG_SYSCTL`, static key declared in lwtunnel headers, and `net->nf.nf_lwtnl_dir_header` storage. Prototypes are exposed via `nf_internals.h`.

Risks: The one-way enable behavior must be visible to userspace; tests should assert that enabling succeeds, disabling after enable fails with `EBUSY`, per-net sysctl tables allocate/free correctly, and builds without sysctl return no-op init/fini.
