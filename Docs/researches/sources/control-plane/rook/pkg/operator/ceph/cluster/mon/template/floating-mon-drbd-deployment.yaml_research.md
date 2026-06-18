# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/template/floating-mon-drbd-deployment.yaml

## Purpose
This embedded YAML template defines a DRBD-backed floating monitor Deployment. It is rendered by `spec.go` when `spec.Mon.FloatingMon` selects a monitor that should move with a DRBD device rather than use the standard monitor pod construction path.

## Important APIs, Types, And Functions
The template produces an `apps/v1` Deployment named `rook-ceph-mon-{{ .NAME }}` with labels identifying `app: rook-ceph-floating-mon`, monitor daemon IDs, cluster namespace, Ceph/Rook versions, and operator namespace. Parameters include monitor identity, namespace, cluster name, versions, FSID, Ceph image, image pull policy, public IP, priority class, host path directories, DRBD config/device/resource values, container data dir, and `ROOK_MSGR2`.

## Control Flow And State
The pod is a single-replica recreate Deployment with hostPath volumes for Rook config, mon keyring, socket, logs, crash dir, monitor data, `/dev`, DRBD config/dir, and host root. Init flow first runs a privileged DRBD utility container to set hostname and promote the DRBD resource primary. A privileged chown container mounts the DRBD device, chowns Ceph paths, and traps exit for cleanup. A privileged `init-mon-fs` container mounts the device and runs `ceph-mon --mkfs`. The main `mon` container mounts the device and runs `ceph-mon --foreground` with public address, bind address, keyring, mon host, initial members, and probes. Sidecars include a log collector and a floating-mon shutdown container whose preStop hook attempts unmount and DRBD demotion.

## Dependencies And Integration Points
The template depends on DRBD utilities, privileged containers, hostPath access, Rook/Ceph secrets, Rook config override ConfigMap, Ceph monitor env vars from `rook-ceph-config`, and mounted host directories. It integrates with `makeFloatingMonDeployment()` and receives resource requirements after YAML decoding.

## Risks And Test Signals
This is a high-risk operational template because it changes hostnames inside containers, mounts/demotes DRBD devices, uses privileged security contexts, and relies on shell lifecycle cleanup. Missing DRBD parameters or incorrect host paths can render an invalid or dangerous workload. `mon_test.go` verifies rendering, resource patching, annotations/labels, update behavior, and missing ConfigMap failures, but it does not execute the DRBD lifecycle.
