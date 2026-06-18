# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-testing.yaml

## Purpose
This manifest exposes the hostpath driver's Unix CSI socket as a TCP `NodePort` service for manual and automated testing with tools such as `csi-sanity` or `csc`. It is explicitly marked as test-only, not production deployment material.

## Important APIs, Types, And Functions
It defines a `Service` named `hostpath-service` with port `10000` and a `StatefulSet` named `csi-hostpath-socat`. The pod runs the `socat` command from image `registry.k8s.io/sig-storage/hostpathplugin:v1.15.0` with arguments `tcp-listen:10000,fork,reuseaddr` and `unix-connect:/csi/csi.sock`.

## Control Flow
The socat pod is colocated with the hostpath plugin through required pod affinity, mounts the driver socket hostPath at `/csi`, and forwards each TCP connection to the Unix socket. The distributed variant also mounts `/var/lib/kubelet/pods` because daemonset driver pod names are non-deterministic for sanity testing.

## State, Persistence, And Dependencies
No durable application state is created. The service allocates a NodePort and the pod relies on the driver socket directory. The socat image is intentionally excluded from deploy-script image overrides.

## Integration Points
External CSI test clients can connect to the NodePort and exercise the same CSI endpoint used by sidecars. Labels connect it to deploy readiness and destroy cleanup.

## Risks
Exposing the CSI socket over a NodePort can allow remote callers to create, delete, mount, or snapshot volumes, so this must remain test-only. Pod affinity or daemonset scheduling issues can point socat at a missing socket.

## Test Signals
Verify the service has a NodePort, TCP connections reach CSI RPCs, `csi-sanity` can run through the port, and deleting the manifest removes both service and forwarding pod.
