## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_linux.go

Purpose: Linux network namespace sandbox implementation for libnetwork. It creates, opens, restores, mutates, and destroys namespace-backed sandboxes and exposes namespace-scoped operations used by interface, neighbor, and route code.

Important APIs/types/functions: `SetBasePath`, `GenerateKey`, `NewSandbox`, `GetSandboxForExternalKey`, `createNetworkNamespace`, `createNamespaceFile`, `Namespace`, `Interfaces`, `InterfaceBySrcName`, `AddAliasIP`, `RemoveAliasIP`, `DisableARPForVIP`, `InvokeFunc`, `Key`, `Destroy`, `RestoreInterfaces`, `RestoreRoutes`, `RestoreGateway`, `IPv6LoEnabled`, `RefreshIPv6LoEnabled`, `ApplyOSTweaks`, and `setIPv6`.

Control flow: sandbox creation bind-mounts a thread's network namespace to a file under the base path, optionally via `unshare.Go(CLONE_NEWNET)`, then opens a namespace-specific netlink handle and brings loopback up. `InvokeFunc` runs callbacks on a locked OS thread inside the sandbox namespace and restores the original namespace. Restore paths reconstruct interface metadata by scanning links and addresses, then send neighbor advertisements.

State and persistence behavior: persistent-ish sandbox identity is the namespace bind mount file. `Namespace` keeps interface metadata, gateways, default-route source names, static routes, IPv6 loopback cache, and netlink handle. Destroy closes the handle, detaches the mount, and removes the namespace file. Sysctls and alias IPs mutate namespace-local kernel state.

Dependencies and integration points: depends on rootless support, unshare, `nlwrap`, global `ns` handles, kernel knobs, netlink/netns, and Linux syscalls. It is the central object used by OSL interface, route, and neighbor modules.

Risks: namespace/thread handling is delicate; failure to restore thread netns can contaminate runtime threads, mitigated by locked goroutine behavior. File bind mounts and unmounts require privileges and cleanup. `Destroy` assumes no running process still uses the namespace. Restore heuristics for interface names can be ambiguous for vxlan/veth and address matches.

Test signals: interface tests exercise namespace creation and AddInterface. Broader sandbox lifecycle, rootless, external-key, restore, IPv6, and sysctl behavior need integration tests with real kernel capabilities.
