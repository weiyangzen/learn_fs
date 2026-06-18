# sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_initiator.go

Purpose: Implements node-side NVMe-oF initiator operations using kernel modules, the `nvme` CLI, sysfs/device paths, and mount-awareness for safe connect/disconnect.

Important APIs/types/functions: `NVMeInitiator`, `ConnectRequest`, `nvmeInitiator`, `NewNVMeInitiator`, `LoadKernelModules`, `ConnectSubsystem`, `DisconnectIfLastMount`, `GetNamespaceDeviceByUUID`, `ResolveListeners`, and helpers for `nvme list-subsys`, path matching, controller discovery, and namespace enumeration.

Control flow: Module loading modprobes `nvme_tcp` and validates `/dev/nvme-fabrics`. Connect lists existing subsystems when HostNQN is provided, skips gateways already in `live` or `connecting` state for the same host/subsystem/gateway, then attempts `nvme connect` against each listener with transport, NQN, address, port, controller-loss timeout, host NQN, and optional DH-CHAP secrets. Success requires at least one listener. Device lookup retries `/dev/disk/by-id/nvme-uuid.<uuid>` with dashed and original UUID variants. Disconnect discovers all controllers for a device, verifies no controller has other mounted namespaces from the passed cache, and disconnects every controller only if safe.

State and persistence behavior: Persistent/external state is kernel NVMe controller connections, `/dev` symlinks, and mount table state supplied by caller. The initiator itself is stateless.

Dependencies and integration points: Depends on `nvme` CLI, `findmnt`-derived mount cache from node server, `kmod.Modprobe`, `retry-go`, JSON output formats from `nvme list-subsys` and `nvme list-ns`, and listener resolution helper in `util.go`.

Risks: JSON parsing depends on CLI output stability. Disconnect safety uses cached mounted device paths, so stale or incomplete cache can leave connections lingering or, worse, disconnect when another namespace is actually mounted under an unrecognized path. `ResolveListeners` mutates the input listener slice when replacing `0.0.0.0`. The `connecting` state is treated as good to avoid duplicate connects, which can preserve a broken path until kernel timeout.

Test signals: Unit tests cover list-subsys JSON parsing and `hasPathToGateway` behavior, including `connecting` paths. No tests invoke real `nvme` commands except through broader integration environments.
