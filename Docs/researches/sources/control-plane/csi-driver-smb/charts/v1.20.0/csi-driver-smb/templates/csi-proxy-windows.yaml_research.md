# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-proxy-windows.yaml

## Purpose
This template renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart `v1.20.0` when `.Values.windows.csiproxy.enabled` is true. It can install the Windows CSI proxy alongside the SMB CSI driver for clusters that do not manage CSI proxy separately.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. The pod uses `windowsOptions.hostProcess: true`, `runAsUserName` from `.Values.windows.csiproxy.username`, host networking, Windows node selectors from `.Values.windows.csiproxy.nodeSelector`, and the `csi-proxy` image from `.Values.image.csiproxy`. It follows the same rolling update `maxUnavailable` value as node workloads.

## Control Flow
Rendering is entirely conditional on `.Values.windows.csiproxy.enabled`. Helm injects labels, tolerations, affinity, priority class, pull secrets, image repository composition, and pull policy. The template does not configure explicit command arguments, so the image entrypoint is responsible for exposing named pipes.

## State And Persistence Behavior
The DaemonSet does not declare persistent volumes in this template. Its practical state is host-level Windows CSI proxy processes and named pipes, which are consumed by the legacy Windows SMB node DaemonSet.

## Dependencies And Integration Points
It integrates with `csi-smb-node-windows.yaml` through the expected `\.\pipe\csi-proxy-filesystem-*` and `\.\pipe\csi-proxy-smb-*` endpoints. It depends on Windows HostProcess support and the configured service account/security policy allowing host-process pods.

## Risks And Test Signals
Risks include enabling it on clusters that already install CSI proxy, using an incompatible proxy image tag, or omitting required pipe exposure. Test with `helm template --set windows.csiproxy.enabled=true`, DaemonSet rollout on Windows nodes, and successful Windows PVC mount through the legacy node path.
