## sources/cloud-native/moby/daemon/libnetwork/ns/init_linux.go

Purpose: initializes and exposes process-wide handles for the initial or detached host network namespace and a default netlink handle with supported netlink families.

Important APIs/types/functions: `NetlinkSocketsTimeout` sets a 3-second socket timeout; `initNamespace` memoizes `initHandles` via `sync.OnceValues`; public accessors are `NsHandle`, `NlHandle`, and test-only `ResetHandles`; support probes include `getSupportedNlFamilies`, `checkXfrmSocket`, and `checkNfSocket`.

Control flow: `initHandles` checks rootless detached netns configuration. If detached, it opens that namespace and creates a netlink handle inside it via `nlwrap.NewHandleAt`; otherwise it uses current namespace and `nlwrap.NewHandle`. It probes XFRM and netfilter support, attempts module loading for conntrack, sets socket timeout, and panics if the default netlink handle cannot be created.

State and persistence behavior: process-global namespace and netlink handles are cached. `ResetHandles` reinitializes them for tests and closes previous handles, explicitly warning it is unsafe with concurrent users.

Dependencies and integration points: depends on `rootless.DetachedNetNS`, libnetwork `modprobe`, `nlwrap`, `netns`, Linux `syscall`, and containerd logging. OSL code uses `ns.NsHandle()` to move links back to the host namespace and `ns.NlHandle()` for host-side operations.

Risks: global handle lifetime is sensitive; closing or resetting while in use can break callers. Panicking on netlink handle creation is intentional but harsh. Module probing may log warnings depending on kernel capabilities. Rootless detached namespace behavior depends on correct thread-safe `nlwrap.NewHandleAt`.

Test signals: no direct tests here in the subset, but OSL tests and rootless networking flows exercise these handles. `ResetHandles` exists specifically to enable clean test state.
