# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_test.go

Purpose: Linux ZFS graphdriver conformance tests.

Important APIs and control flow: setup/teardown tests acquire and release a shared ZFS driver. Generic graphtest functions validate empty/base/snapshot layer behavior. `TestZfsSetQuota` runs `DriverTestSetQuota` with quota marked required, so an unsupported quota path is a failure rather than a skip.

State, dependencies, and risks: tests require Linux with a functional ZFS setup, `zfs` command, `/dev/zfs`, a ZFS-backed test root or configured dataset, and privileges to create/destroy datasets and mount them. The suite gives strong signals for dataset lifecycle and quota enforcement but is environment-sensitive.
