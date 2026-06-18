# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node.go

## Purpose
This file derives monitor scheduling network information from Kubernetes `Node` objects. It turns a node into `opcontroller.MonScheduleInfo`, choosing the IP address Rook should use for monitor endpoints when host networking or node-based monitor placement is involved.

## Important APIs, Types, And Functions
`monIPAnnotation` is the annotation key `network.rook.io/mon-ip`. `getNodeInfoFromNode(n v1.Node)` returns a `MonScheduleInfo` populated with the Kubernetes node name, hostname label from `k8sutil.LabelHostname()`, and an address. Address precedence is explicit annotation, then `NodeInternalIP`, then `NodeExternalIP`.

## Control Flow And State
The function is read-only. It first creates schedule info from node metadata, then checks annotations for a custom monitor IP and returns immediately if present. If no annotation exists, it scans `n.Status.Addresses` for an internal IP and falls back to an external IP. If no usable address is found, it returns an error. No Kubernetes writes or persistent state updates happen here; persistence happens later when monitor scheduling information is saved to endpoint ConfigMaps.

## Dependencies And Integration Points
The function depends on Kubernetes core API node fields, Rook Kubernetes label helpers, and the monitor package logger. Its output feeds monitor assignment and endpoint persistence through `opcontroller.MonScheduleInfo`.

## Risks And Test Signals
The main risk is selecting the wrong address in clusters with multiple network planes; the annotation override is the escape hatch. `node_test.go` covers no-address errors, internal-IP precedence over external IP, external-only fallback, and annotation override. Hostname label absence is not treated as an error here, so downstream scheduling logic must tolerate or validate an empty hostname where required.
