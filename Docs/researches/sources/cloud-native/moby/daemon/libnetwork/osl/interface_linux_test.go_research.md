## sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux_test.go

Purpose: Linux tests for OSL interface name generation and concurrent interface addition.

Important APIs/types/functions: `TestGenerateIfaceName` validates gap-filling suffix generation; `TestAddInterfaceInParallel` creates a named netns and dummy links, then concurrently calls `Namespace.AddInterface` with `WithCreatedInContainer(true)`.

Control flow: the parallel test locks the OS thread, creates a named namespace, creates a namespaced netlink handle, adds ten dummy interfaces, launches ten goroutines through `sync.WaitGroup.Go`, then lists links and expects `eth0` through `eth9`.

State and persistence behavior: creates real Linux named network namespaces and dummy netlink devices, then deletes/closes the namespace through defers. It mutates kernel network state and requires permissions/capabilities suitable for netns operations.

Dependencies and integration points: uses `netns`, `netlink`, `nlwrap`, `sliceutil`, `runtime.LockOSThread`, and gotest assertions. It directly exercises `Namespace.AddInterface`, `generateIfaceName`, and namespace handle behavior.

Risks: environment-sensitive and likely requires root or CAP_NET_ADMIN. The final `nlwrap.LinkList()` call lists the current namespace, so correctness depends on thread namespace context and the handle setup. It does not test address/route/sysctl setup.

Test signals: strong targeted signal that interface naming is concurrency-safe and fills numeric gaps without duplicate names.
