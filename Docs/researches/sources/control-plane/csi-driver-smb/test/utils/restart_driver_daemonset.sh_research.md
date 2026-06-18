# sources/control-plane/csi-driver-smb/test/utils/restart_driver_daemonset.sh

## Purpose
This script restarts SMB CSI node daemonsets by deleting and reapplying Linux and Windows node manifests.

## Important APIs, Types, And Functions
It uses `kubectl delete -f ./deploy/csi-smb-node.yaml`, `kubectl delete -f ./deploy/csi-smb-node-windows.yaml`, sleeps 15 seconds, then applies both manifests.

## Control Flow
With strict shell settings, delete failures other than ignored not-found failures stop execution. After deletion and sleep, both daemonsets are reapplied.

## State, Persistence, And Dependencies
It mutates cluster daemonsets and pods. Dependencies include kubectl, current working directory at repository root, and deployment manifests.

## Integration Points
The restart-driver e2e tests can inject this script as `RestartDriverFunc`.

## Risks And Test Signals
It does not wait for new daemonset rollout after apply, leaving readiness to callers. Applying Windows manifests on clusters without Windows support may fail depending on manifest validity. Signal is kubectl exit status.
