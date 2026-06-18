<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go

## Purpose
`rbd_attach.go` maps and unmaps RBD images on a node through either krbd (`rbd device`) or `rbd-nbd`, including map/unmap option parsing, NBD feature discovery, mapped-device lookup, retry-before-map in-use checks, encrypted-device close handling, and NBD client log cleanup.

## Important APIs, Types, And Functions
Important constants define mounters, access types, default NBD `try-netlink`, `reattach-timeout`, and `io-timeout` behavior. `rbdDeviceInfo` models JSON output from `rbd device list` and `rbd-nbd list-mapped`. `detachRBDImageArgs` carries unmap mode, encryption, and log strategy. Key functions are `SetRbdNbdToolFeatures`, `parseMapOptions`, `NodeServer.getMapOptions`, `getDeviceList`, `findDeviceMappingImage`, `waitForPath`, `attachRBDImage`, `createPath`, `waitForrbdImage`, `detachRBDDevice`, and `detachRBDImageOrDeviceSpec`.

## Control Flow
On startup `SetRbdNbdToolFeatures` modprobes `nbd`, checks kernel cookie support, and checks `rbd-nbd --help` for cookie support. During staging, `getMapOptions` splits semicolon-delimited krbd/nbd options, applies the right side for the chosen mounter, and appends read-affinity map options for krbd. `attachRBDImage` first checks existing mappings, waits for image watchers to clear if absent, then builds and executes a map command. `createPath` chooses `rbd` or `rbd-nbd`, adds Ceph credentials, namespace execution, read-only flags, and default NBD options. On connection timeout it tries to unmap the image spec. Unmap closes encrypted mapper devices first, chooses krbd or nbd CLI syntax, treats missing image-spec mappings as success, and performs asynchronous NBD log cleanup.

## State And Persistence
Runtime state includes global `hasNBD` and `hasNBDCookieSupport`, kernel support detection, process execution output, and node device mappings. Persistent effects are mapped `/dev/rbd*` or `/dev/nbd*` devices, NBD log files, and encrypted mapper closure. This file reads no cluster OMAP directly but uses `isInUse` watchers via `rbdVolume`.

## Dependencies And Integration Points
It depends on `util.ExecCommand`, `ExecuteCommandWithNSEnter`, kernel version helpers, kmod, retry-go, go-ceph metadata through `isInUse`, and stash/log helpers from `rbd_util.go`. It is called from node staging, unstage, expansion, and healer flows.

## Risks
Command-line option composition is security- and correctness-sensitive because user options are passed to external CLIs. The missing-mapping success check applies only when unmapping by image spec, not device path. Global NBD feature flags are mutable package state. `waitForrbdImage` may fail legitimate multi-node filesystem use while intentionally bypassing watcher checks for multi-node block. Async log cleanup errors are only logged. In `flattenRbdImage` callers, map may race with in-progress flatten tasks.

## Test Signals
`rbd_attach_test.go` covers map option parsing, including old format, new krbd/nbd format, embedded colons, and unknown mounter errors. There is no unit coverage for command construction, NBD feature discovery, namespace execution, in-use retry, timeout cleanup, or encrypted unmap.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go -->
