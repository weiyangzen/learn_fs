# sources/cloud-native/cri-o/server/sandbox_network_linux.go

Purpose: Linux-specific validation and cleanup of network namespace paths.

Important APIs and functions: `validateNetworkNamespace` opens the namespace with CNI `ns.GetNS` and closes it; `cleanupNetns` removes the path via `os.RemoveAll`.

Control flow: validation converts `GetNS` failures into contextual errors. Cleanup logs success or warning.

State and persistence: reads netns path validity and may delete netns filesystem entries.

Dependencies and integration: used by `networkStop` before/after CNI teardown; depends on containernetworking plugins `ns` package.

Risks: `RemoveAll` on a bad netns path is powerful, so path provenance from sandbox state must be trusted.

Test signals: no direct tests in this subset.
