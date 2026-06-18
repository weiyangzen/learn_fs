<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go

Purpose: provides Linux helpers for RootlessKit detached network namespace handling and tracking threads already executing in container sandbox namespaces.

Important APIs and types: `DetachedNetNS`, `detachedNetNS`, `RunInNetNS`, `MarkInSandboxNS`, `UnmarkInSandboxNS`, `InSandboxNS`, and `sandboxNSThreads`.

Control flow: `detachedNetNS` checks `ROOTLESSKIT_STATE_DIR/netns`. `RunInNetNS` runs the function directly if no namespace path is supplied; otherwise it starts a goroutine, locks its OS thread, opens target and original namespaces, enters target namespace, runs the function, attempts to restore original namespace, and deliberately leaves the thread locked if restoration fails. Mark/unmark track current TID in a sync map.

State and persistence: reads environment and namespace files. Maintains process-global map of TIDs currently marked as sandbox namespace threads.

Dependencies and integration: used by rootless networking and iptables/nft wrapper decisions. Depends on `vishvananda/netns`, runtime thread locking, and Linux TIDs.

Risks: namespace switching is thread-affine; incorrect unlock/restore can taint runtime threads. `DetachedNetNS` caches results with `sync.OnceValues`, so changes to env/files after first call are ignored. Mark/unmark require callers to be on the same locked OS thread.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go -->
