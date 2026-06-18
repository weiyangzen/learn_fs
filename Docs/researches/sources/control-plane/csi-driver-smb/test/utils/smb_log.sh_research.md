# sources/control-plane/csi-driver-smb/test/utils/smb_log.sh

## Purpose
This diagnostic script prints Kubernetes node, pod, driver, Samba server, service, metrics, and crash/restart information for SMB e2e runs.

## Important APIs, Types, And Functions
`cleanup` traps errors and exits 0. Variables are `NS=kube-system`, `CONTAINER=smb`, and `DRIVER=smb` or the first argument. It uses kubectl, xargs, awk, and curl.

## Control Flow
The script prints node and default namespace status, Samba server logs/events, kube-system pod status, controller logs, restart/crash details with previous container logs, Linux node logs, Windows node events/logs, services, and metrics from `csi-$DRIVER-controller` service IP on port 29644.

## State, Persistence, And Dependencies
No cluster state is intentionally changed. It depends on label conventions `app=csi-$DRIVER-*`, container name `smb`, service naming, kubectl access, and network access to metrics.

## Integration Points
The e2e suite and external e2e script call this in teardown/traps to collect failure evidence.

## Risks And Test Signals
The ERR trap masks diagnostic failures by exiting 0. Several pipelines can fail when no pods match unless guarded. Metrics IP extraction assumes service ClusterIP in column four. Signals are logs and events printed to test artifacts.
