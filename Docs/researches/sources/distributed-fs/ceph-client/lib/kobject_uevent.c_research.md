# sources/distributed-fs/ceph-client/lib/kobject_uevent.c

Purpose: implements userspace event delivery for kobjects through netlink and optional usermode helper execution, including synthetic uevent parsing.

Important APIs/state: global `uevent_seqnum`, optional `uevent_helper`, `kobject_synth_uevent()`, `kobject_uevent_env()`, `kobject_uevent()`, `add_uevent_var()`, per-network-namespace netlink socket setup, and helper sysctl registration. The action string table maps `enum kobject_action` to wire strings.

Control flow: `kobject_uevent_env()` locates the nearest kset, applies suppress/filter/name callbacks, allocates an environment, adds `ACTION`, `DEVPATH`, `SUBSYSTEM`, caller variables, and kset variables, marks add/remove state flags, removes `MODALIAS` for unbind, appends a sequence number, broadcasts to the correct netlink namespace, then optionally invokes the configured helper. Synthetic uevents parse an action, optional UUID, and alphanumeric `KEY=VALUE` arguments into environment variables.

State and persistence: persistent state includes sequence counter, per-net uevent socket list protected by a mutex, per-kobject add/remove sent flags, and optional helper path. Temporary `kobj_uevent_env` buffers hold argv/envp data.

Dependencies and integration: depends on kobject/kset operations, netlink, network namespaces, user namespaces, kmod usermode helpers, sysctl, UUID/ctype parsing, and skb allocation. Device and subsystem code call it after object lifecycle changes.

Risks: environment buffer and envp count limits can return `-ENOMEM`; missing kset or subsystem drops events; net namespace tagging must match kobject namespace ops; helper is filtered for non-init namespaces; synthetic input validation is intentionally strict; netlink `ENOBUFS` is ignored for userspace handling.

Test signals: uevent listener tests, synthetic uevent parser validation, namespace-scoped netlink delivery, helper path/sysctl tests when enabled, add/remove auto-cleanup behavior, and buffer-limit fault injection.
