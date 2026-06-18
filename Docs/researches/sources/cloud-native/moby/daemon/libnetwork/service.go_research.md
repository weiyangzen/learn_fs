<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service.go -->
## sources/cloud-native/moby/daemon/libnetwork/service.go

Purpose: shared service/load-balancer data structures for swarm service discovery and dataplane programming.

Important APIs/types/functions: global `fwMarkCtr` with mutex, `portConfigs.String`, `serviceKey`, `service`, `assignIPToEndpoint`, `removeIPToEndpoint`, `printIPToEndpoint`, `lbBackend`, and `loadBalancer`.

Control flow: service IP-to-endpoint mapping uses a set-matrix to track transient duplicate endpoint/IP states. `portConfigs.String` creates a stable key fragment from published/target/protocol tuples. Load balancers store per-network VIP, fwmark, backends, and service alias reference counts.

State and persistence: process memory only. Service bindings are held on `Controller.serviceBindings`; fwmarks are monotonic from 256 and not persisted here.

Dependencies and integration points: used heavily by `service_common.go`, `service_linux.go`, and `service_windows.go` to manage DNS records, IPVS/HNS policy, and alias lifetime.

Risks and test signals: alias reference counts and transient duplicate IP states are sensitive during rolling updates. Tests in `service_common_unix_test.go` cover alias ref-counting and cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service.go -->
