# sources/distributed-fs/ceph-client/include/rdma/ib_ucaps.h

Purpose: declares RDMA userspace capability file-descriptor support. It lets user access code create, remove, collect, and test capability tokens such as mlx5 local or other-VHCA control.

Important APIs and types: `enum rdma_user_cap` currently defines `RDMA_UCAP_MLX5_CTRL_LOCAL`, `RDMA_UCAP_MLX5_CTRL_OTHER_VHCA`, and `RDMA_UCAP_MAX`. `UCAP_ENABLED()` tests a bitmask for a capability. APIs include global `ib_cleanup_ucaps()`, `ib_get_ucaps()` to derive an index mask from file descriptors, and config-gated `ib_create_ucap()`/`ib_remove_ucap()`. When `CONFIG_INFINIBAND_USER_ACCESS` is disabled, create/remove are no-op stubs returning `-EOPNOTSUPP` or doing nothing.

Control flow: user-access-enabled code creates capability FDs for a requested type, passes FDs back into RDMA ioctls or setup paths, and `ib_get_ucaps()` validates/collects them into an index mask. Cleanup removes global capability resources during subsystem teardown.

State and persistence: capability state is runtime kernel object/file state. The bitmask represents active validated capabilities for a call; it is not persisted.

Dependencies and integration points: depends on RDMA user-access config, Linux FD/file lifetime rules, and provider-specific policy such as mlx5 control scopes. It integrates privileged or delegated RDMA control flows with uverbs-like userspace entry points.

Risks and test signals: risks include capability bit shifts exceeding mask width, accepting stale/wrong FDs, missing cleanup of capability objects, config-stub behavior surprising callers, and confused local vs other-VHCA authority. Test capability FD create/remove, `ib_get_ucaps()` with valid/invalid/duplicate FDs, config-disabled builds, mask testing with `UCAP_ENABLED()`, and permission checks in provider callers.
