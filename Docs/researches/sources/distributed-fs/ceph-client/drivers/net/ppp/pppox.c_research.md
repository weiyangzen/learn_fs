# sources/distributed-fs/ceph-client/drivers/net/ppp/pppox.c

Purpose: provides the generic PPPoX socket family dispatcher for PF_PPPOX. It is the registry and common ioctl layer used by protocol-specific modules such as PPPoE and PPTP.

Important APIs and functions: `register_pppox_proto()` and `unregister_pppox_proto()` publish protocol handlers in the global `pppox_protos[]` table. `pppox_create()` validates the requested protocol, requests the module alias if absent, pins the provider module, and calls the provider `create()` callback. `pppox_ioctl()` implements `PPPIOCGCHAN` generically by returning `ppp_channel_index()` and marking the socket `PPPOX_BOUND`, while delegating other ioctls to the protocol-specific handler. `pppox_unbind_sock()` unregisters an attached PPP channel and marks the socket dead. `pppox_compat_ioctl()` adapts compat pointers.

Control flow: module init registers `pppox_proto_family` with `sock_register()`. Socket creation is a two-stage dispatch: PF_PPPOX reaches `pppox_create()`, then protocol-specific code supplies actual socket operations and channel behavior. Ioctls enter through protocol socket ops but commonly call `pppox_ioctl()`, which locks the socket before inspecting or mutating state.

State and persistence: state is limited to the static protocol pointer table and transient socket state bits in `struct pppox_sock`. No synchronization is visible around table updates, so registration ordering is expected to happen during module init/exit while users rely on module refcounts. There is no persistent storage.

Dependencies and integration: depends on the socket family core, module autoload aliases, PPP channel APIs, user-copy helpers, and protocol modules that provide `struct pppox_proto`. It exports the registry and unbind/ioctl helpers for those modules.

Risks and test signals: risks include stale protocol-table access during unregister, incorrect module refcount handling around provider `create()`, and state transitions caused by `PPPIOCGCHAN`. Test signals are PF_PPPOX socket creation before and after provider module autoload, invalid protocol handling, generic channel ioctl behavior, compat ioctl coverage, provider unload/reload, and PPP channel unregister on protocol release paths.
