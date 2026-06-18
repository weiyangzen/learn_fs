# sources/cloud-native/containerd/pkg/oci/spec_opts_user_test.go

Purpose: detailed tests for OCI user, group, and supplemental group resolution from container rootfs files.

Important APIs/types/functions: tests cover `WithUser`, `WithUserID`, `WithUsername`, `WithAdditionalGIDs`, `WithAppendAdditionalGroups`, and missing `/etc/group` behavior. Cases include numeric uid/gid, username/groupname, mixed forms, out-of-range IDs, missing passwd/group files, rootfs absolute-path requirements, and additional group append by name or gid.

Control flow: tests create temporary rootfs layouts with synthetic `etc/passwd` and `etc/group`, configure unmanaged root paths, apply user-related options, and assert `s.Process.User` fields or errors.

State/persistence: temporary rootfs files only.

Dependencies/integration: production user parsing and `openUserFile` paths are exercised through real filesystem reads.

Risks: rootfs parsing behavior can vary if Go or `moby/sys/user` changes. Tests focus on unmanaged rootfs paths rather than snapshotter-mounted rootfs.

Test signals: protects Docker/OCI-compatible `USER` parsing, fallback gid behavior, supplemental group lookup, error classification for missing groups, and additional-gid preservation.
