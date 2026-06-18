## sources/cloud-native/buildkit/util/network/host.go

Purpose: non-Windows host-network provider and namespace implementation.

Important APIs/types: `NewHostProvider`, `host`, `hostNS`. `host.New` returns `hostNS`; `hostNS.Set` applies containerd `oci.WithHostNamespace(specs.NetworkNamespace)`; `DialContext` uses the default `net.Dialer`.

State/persistence: no state, no cleanup. Dependencies: containerd OCI spec helper, resource sample type, Go net.

Integration points: default fallback on Unix when CNI is not configured, explicit `pb.NetMode_HOST`, and proxy egress mode. Risks: hostname parameter is ignored; `Sample` has no metrics; unavailable on Windows. Test signals: no direct tests.
