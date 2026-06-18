# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hds.py

Purpose: Python kselftest for ethtool Netlink Header Data Split (HDS) ring attributes and their interaction with XDP and legacy ioctl ring changes.

Important APIs/functions: `NetDrvEnv`, `EthtoolFamily`, `NlError`, `ksft_run`, `ksft_eq`, `ksft_raises`, `_get_hds_mode()`, `_xdp_onoff()`, `_ioctl_ringparam_modify()`, `get_hds()`, `get_hds_thresh()`, `_hds_reset()`, `_defer_reset_hds()`, `set_hds_enable()`, `set_hds_disable()`, threshold setters, `set_xdp()`, `enabled_set_xdp()`, `ioctl()`, `ioctl_set_xdp()`, and `ioctl_enabled_set_xdp()`.

Control flow: `main()` creates a local driver environment with three queues and runs HDS get/set cases. Setters read ring capabilities, skip unsupported devices, apply `tcp-data-split` or `hds-thresh`, and verify via Netlink. XDP cases confirm XDP can attach when HDS is auto/unknown and fails when HDS is explicitly enabled. Ioctl cases perturb unrelated ring size through legacy ethtool ioctl and confirm HDS state survives.

State and persistence: Mutates ethtool ring attributes, XDP program attachment, and TX ring size. Deferred cleanup restores prior HDS/ring state.

Dependencies and integration points: Requires ethtool Netlink ring support, optional HDS thresholds, XDP dummy BPF object, and net selftest Python library.

Risks and test signals: The file contains duplicate `set_xdp`/`enabled_set_xdp` definitions; later definitions override earlier ones but behavior is similar. Failures indicate HDS Netlink ABI, validation, reset, XDP compatibility, or ioctl interaction regressions.
