## sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux.go

Purpose: Linux exec proxy network provider that creates isolated exec/proxy namespaces, injects an HTTP(S) MITM proxy, enforces source policy, routes egress through selected network mode, and captures downloaded material digests.

Important APIs/types: `Opt`, `Supported`, `New`, provider `Close/NewProxy/newNS/certForHost`, `proxyNS` implementing `ProxyNamespace`, and `proxyHandler` implementing HTTP proxy behavior. Helpers manage netns files, veth setup, certificate generation/cache, URL redaction/normalization, and body digest tracking.

Control flow: `New` cleans old proxy namespaces, creates a CA, builds a namespace pool, and pre-fills it. `newNS` creates paired exec and proxy namespaces, assigns veth interfaces and /30 IPs. `NewProxy` pulls a namespace from the pool and starts a proxy. `startProxy` listens inside the proxy namespace, creates an egress namespace from configured providers, requires it to implement `network.Dialer`, clones transport with egress dialer, and serves HTTP. `ProxyEnv` returns HTTP/HTTPS proxy variables pointing at the proxy-side listener and localhost `NO_PROXY`; `ProxyCACert` returns generated CA PEM.

HTTP handling: plain requests are normalized to absolute URLs, policy-checked and optionally converted for GET URL rewrites, then sent upstream with proxy headers and Accept-Encoding stripped. CONNECT is MITM'd with per-host leaf certs, reads HTTP requests inside TLS, applies the same policy/conversion, and writes upstream responses back. Successful complete GET 2xx responses record SHA-256 material digests; non-GET, ranges/partial responses, transformed/unreadable bodies, and >=400 responses are recorded as incomplete where applicable. Redirects are captured for later aliasing.

State/persistence: creates namespace bind mounts under `<root>/net/proxy`, veth devices, per-provider CA private key, LRU leaf cert cache up to 1024 entries, pooled namespaces, live HTTP servers/transports, and capture records. Dependencies: netlink/netns, containerd OCI, BuildKit network/netpool/source protobufs, TLS/X509, HTTP, OCI digest.

Integration points: constructed by `netproviders` when Linux proxy support is enabled. Executor uses returned namespace/spec/proxy env/CA. Source policy engine evaluates requests through `ProxyPolicy`.

Risks: MITM proxy requires containers to trust injected CA; namespace and veth cleanup must run to avoid leaks; generated CA is per provider lifetime and in memory; policy conversion supports URL-only GET rewrites; digest capture only represents full successful untransformed bodies. Tests in `provider_linux_test.go` cover capture, transforms, canceled contexts, HTTP/2 transport clone, MITM response framing, incomplete classification, redirects, redaction, policy conversion/rejection, and cert cache refresh.
