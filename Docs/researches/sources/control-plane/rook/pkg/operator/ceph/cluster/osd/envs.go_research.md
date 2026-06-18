# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs.go

## Purpose
This file centralizes environment variable construction for OSD prepare, activate, daemon, and key-rotation containers. It defines the env var names that form the contract between the Rook operator, Rook OSD entrypoints, `ceph-volume`, KMS support, and Kubernetes-injected runtime data.

## Important APIs, Types, and Functions
Constants define Rook-specific variables such as `ROOK_OSD_DATABASE_SIZE`, `ROOK_OSDS_PER_DEVICE`, `ROOK_ENCRYPTED_DEVICE`, `ROOK_PVC_NAME`, `ROOK_PVC_BACKED_OSD`, `ROOK_BLOCK_PATH`, `ROOK_CV_MODE`, `ROOK_OSD_CRUSH_DEVICE_CLASS`, `ROOK_REPLACE_OSD`, and `ROOK_CRUSHMAP_ROOT`. `CephVolumeEncryptedKeyEnvVarName` preserves the hard-coded `ceph-volume` dmcrypt variable.

`Cluster.getConfigEnvVars()` builds common env vars for prepare and daemon contexts: node name, cluster UID/name, pod IPs, namespace, monitor endpoint, config directory, config override, node name, crush root, CRUSH host hint, ceph-volume variables, and optional store-config variables. In prepare mode it adds the Ceph username, FSID from `rook-ceph-mon`, and OSD store type. It hides the CRUSH hostname for non-portable PVC prepare pods until the pod's node is known.

Helper constructors return individual `v1.EnvVar` values for data devices, filters, metadata/wal devices, PVC flags, wipe behavior, debug logging, block path, ceph-volume mode, LV-backed PV, crush class, store type, replacement OSD ID, initial weight, encryption, and PVC name. `cephVolumeEnvVar()` returns the ceph-volume runtime contract (`CEPH_VOLUME_DEBUG`, `CEPH_VOLUME_SKIP_RESTORECON`, `DM_DISABLE_UDEV`). `osdActivateEnvVar()` adds monitor host and `CEPH_ARGS`. `getEnvFromSources()` includes an optional `rook-ceph-osd-env-override` ConfigMap. `getTcmallocMaxTotalThreadCacheBytes()` reads an explicit value or parses `/etc/sysconfig/ceph` with `ini`.

## Control Flow
Callers compose helper outputs into pod specs. `getConfigEnvVars()` branches on prepare mode and on non-zero store config fields, leaving absent settings unset instead of adding empty env vars. TCMalloc lookup falls back to an empty value if the packaged config file cannot be read.

## State and Persistence
This file does not persist state itself, but env vars it creates become part of Job, Deployment, and CronJob pod specs. Those pod specs preserve OSD identity, block device paths, encryption flags, and activation details across reconciles and upgrades.

## Dependencies and Integration Points
It integrates with Ceph monitor env helpers, Kubernetes downward API helpers, Ceph client crush-root derivation, and `gopkg.in/ini.v1`. It is consumed by prepare job construction, daemon deployment construction, activation init containers, and key rotation jobs.

## Risks and Edge Cases
Env var names are compatibility-sensitive because older Deployments are parsed by `getOSDInfo()`. Changing names can break upgrades or migration. Optional override ConfigMap use is intentionally non-fatal. `getTcmallocMaxTotalThreadCacheBytesFromFile()` silently returns empty on parse/read failure, which avoids blocking pods but can hide packaging problems.

## Test Signals
`envs_test.go` validates ceph-volume env ordering/content, activation env additions, explicit TCMalloc override, missing file behavior, empty file behavior, and sysconfig parsing.
