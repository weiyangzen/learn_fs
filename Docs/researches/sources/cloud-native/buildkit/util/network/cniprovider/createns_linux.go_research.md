## sources/cloud-native/buildkit/util/network/cniprovider/createns_linux.go

Purpose: Linux network namespace file lifecycle for CNI provider.

Important functions: `cleanOldNamespaces`, `unshareAndMountNetNS`, `createNetNS`, `setNetNS`, `unmountNetNS`, `deleteNetNS`.

Control flow: `cleanOldNamespaces` scans `<root>/net/cni` and asynchronously releases leftover namespaces through CNI remove/unmount/delete. `createNetNS` creates a bind-mount target file, launches a goroutine locked to an OS thread, unshares `CLONE_NEWNET`, bind-mounts `/proc/self/task/<tid>/ns/net`, and returns the path. `setNetNS` mutates OCI spec with a Linux network namespace path. Cleanup ignores `EINVAL`/`ENOENT` unmount and missing files.

State/persistence: creates bind-mounted namespace files under BuildKit root. Dependencies: containerd OCI helper, unix/syscall, BuildKit logger.

Integration points: used by `cniProvider.newNS` and tests. Risks: goroutine intentionally leaves thread locked so runtime terminates it; cleanup is asynchronous and warnings only; root privileges/capabilities are required. Test signals: exercised by `cni_linux_test.go`.
