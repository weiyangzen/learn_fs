# sources/distributed-fs/ceph-client/include/net/netfilter/nf_hooks_lwtunnel.h

Purpose: Declares the sysctl handler that controls lightweight-tunnel netfilter hook behavior when `CONFIG_SYSCTL` is enabled.

Important APIs/types/functions: The only exported contract is `nf_hooks_lwtunnel_sysctl_handler(const struct ctl_table *table, int write, void *buffer, size_t *lenp, loff_t *ppos)`.

Control flow: The handler is called by sysctl read/write dispatch for the corresponding lwtunnel netfilter knob. This header does not implement policy; it exposes the hook point to sysctl table definitions.

State and persistence: Persistent state lives in the sysctl backing variable owned by implementation code, not in this header. The handler must interpret user buffers and update that state consistently.

Dependencies/integration: Depends on `linux/sysctl.h` and `linux/types.h`; integrates with sysctl registration and lwtunnel/netfilter code.

Risks/test signals: Main risks are missing declaration under configuration combinations and incorrect write validation in the implementation. Test with `CONFIG_SYSCTL=y` and disabled variants, sysctl read/write permissions, invalid lengths, and namespace or global scope expectations.
