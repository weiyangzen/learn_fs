## sources/cloud-native/moby/daemon/libnetwork/nlwrap/nlwrap_linux.go

Purpose: Linux netlink wrapper that makes selected vishvananda/netlink operations more robust against interrupted dumps and namespace thread contamination. It provides a drop-in-ish `Handle` wrapper plus package-level helpers for calls that libnetwork commonly uses.

Important APIs/types/functions: `Handle` embeds `*netlink.Handle`; constructors `NewHandle` and `NewHandleAt`; lifecycle `Close`; retry helpers `retryOnIntr` and `discardErrDumpInterrupted`; wrapped operations include `AddrList`, `ConntrackDeleteFilters`, `ConntrackTableList`, `LinkByName`, `LinkList`, `LinkSubscribeWithOptions`, `RouteList`, `XfrmPolicyList`, and `XfrmStateList`.

Control flow: wrapped calls retry up to `maxAttempts` when `netlink.ErrDumpInterrupted` is returned, then log and discard that error to preserve older netlink behavior that returned possibly inconsistent results. `NewHandleAt` and namespaced `LinkSubscribeWithOptions` create sockets on a locked OS thread, restore the original namespace when possible, and intentionally keep the goroutine locked if restoration fails so the Go runtime does not reuse a tainted thread.

State and persistence behavior: no persistent state. It creates netlink sockets and temporary goroutines/threads. Handles must be closed by callers. The thread-lock behavior is defensive process state management around Linux network namespaces.

Dependencies and integration points: wraps `github.com/vishvananda/netlink` and `netns`, uses `runtime.LockOSThread`, `containerd/log`, and `pkg/errors`. OSL namespace and interface code depend on these wrappers for safer namespace operations.

Risks: after repeated `ErrDumpInterrupted`, callers receive data that may be inconsistent, trading strictness for compatibility. Namespace restoration failure behavior is subtle and must not unlock contaminated threads. `LinkSubscribeWithOptions` requires callers to close `done` to stop netlink goroutines cleanly.

Test signals: no direct tests in this subset. Indirect coverage comes from namespace/interface tests and any libnetwork integration tests running in real namespaces. Rootless namespace contamination is a key scenario that should have focused regression coverage elsewhere.
