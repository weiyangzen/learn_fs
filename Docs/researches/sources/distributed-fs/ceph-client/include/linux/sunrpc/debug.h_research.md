# sources/distributed-fs/ceph-client/include/linux/sunrpc/debug.h

Purpose: provides SUNRPC debug masks, conditional debug printing macros, sysctl hooks, and debugfs registration APIs.

Important APIs and types: global masks are `rpc_debug`, `nfs_debug`, `nfsd_debug`, and `nlm_debug`. `dprintk()` and `dprintk_rcu()` expand through `dfprintk()` and `dfprintk_rcu()` using a local `FACILITY`. Debug-enabled builds use `ifdebug()` and either `trace_printk()` or `printk()`. APIs register sysctl, initialize/exit debugfs, and attach client/transport debugfs directories.

Control flow: when `CONFIG_SUNRPC_DEBUG` is enabled, debug masks gate printing and RCU-safe printing acquires an RCU read lock. Disabled builds compile calls to `no_printk()` for format checking without output.

State and persistence: debug masks and debugfs dentries are runtime diagnostic state. No persistent data is stored.

Dependencies and integration points: depends on UAPI debug bit definitions and optional debugfs/trace support. It is included by `sunrpc/types.h` and used throughout SUNRPC.

Risks and test signals: risks include format side effects hidden by disabled debug, trace_printk overhead, missing RCU protection around pointer formatting, and stale debugfs directories. Test with debug config matrices, dynamic mask changes, debugfs mount/unmount, and RCU debug.
