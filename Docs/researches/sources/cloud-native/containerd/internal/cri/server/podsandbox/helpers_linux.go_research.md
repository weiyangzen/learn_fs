# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_linux.go

## Purpose

This Linux helper file owns Linux-specific sandbox filesystem paths, SELinux label construction, user namespace mapping, cgroup path formatting, recursive mount cleanup, and snapshot remapping options.

## Important APIs, Types, and Functions

Key functions include `getCgroupsPath`, `pinUserNamespace`, `toLabel`, `initLabelsFromOpt`, `checkSelinuxLevel`, `unmountRecursive`, `ensureRemoveAll`, `modifyProcessLabel`, `parseUsernsIDMap`, `parseUsernsIDs`, and `snapshotterRemapOpts`. Path helpers return sandbox hostname, hosts, resolv.conf, dev-shm, and pinned namespace paths.

## Control Flow

Cgroup paths use systemd `slice:prefix:name` format when the parent basename ends in `.slice`; otherwise they join parent and sandbox ID. User namespace parsing allows no mappings for node mode and exactly one UID and one GID mapping for pod mode. `ensureRemoveAll` unmounts recursively, retries races on missing children, detaches busy mountpoints, and caps retries.

## State and Persistence Behavior

The file creates and bind-mounts pinned user namespace files and removes sandbox state directories. It also generates remapper labels for snapshots when pod user namespaces are enabled.

## Dependencies and Integration Points

It integrates with Linux syscalls, `mountinfo`, containerd mount and snapshot APIs, SELinux, seccomp, CRI runtime namespace options, and runtime spec Linux ID mappings.

## Risks and Test Signals

Risks include SELinux level regex drift, single-line ID mapping limitations, mount cleanup races, and KVM SELinux label conversion failures. Tests cover cgroup path formatting, SELinux options, ID mappings through sandbox spec tests, and root-only busy mount removal.
