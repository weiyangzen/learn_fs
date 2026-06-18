# sources/cloud-native/cri-o/internal/config/nsmgr/types_linux.go

Purpose: implements the Linux namespace object model and namespace path validation/opening.

Important APIs/types/functions: `supportedNamespacesForPinning`, `PodNamespacesConfig`, `PodNamespaceConfig`, internal `namespace`, `NS` interface wrapper around CNI `NetNS`, `Path`, `Type`, `Remove`, and `GetNamespace`.

Control flow: `supportedNamespacesForPinning` lists net, ipc, uts, user, and pid. `Remove` locks, closes the namespace handle if open, marks it closed, checks the path, detaches any mount while ignoring `EINVAL`, and removes the path. `GetNamespace` calls `nspkg.GetNS`; on failure it returns a closed namespace with the path plus the error, allowing callers to track cleanup paths even when opening fails.

State and persistence behavior: namespace objects wrap an open namespace handle and a bind-mount path. `Remove` unmounts and deletes the pinned path from disk.

Dependencies/integration points: depends on CNI plugins `ns`, storage idtools via config types, and unix syscalls. Used by Linux namespace manager and container factory PID namespace tracking.

Risks: `Remove` is idempotent for closing but still attempts path cleanup; unmount/remove errors can propagate. Returning a namespace object alongside an error from `GetNamespace` requires callers to treat partial results carefully.

Test signals: no direct tests here; behavior is indirectly covered by namespace lifecycle consumers.
