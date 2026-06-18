<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go

Purpose: option constructors used to configure `Sandbox` creation.

Important APIs/functions: hostname/domain/hosts path/origin hosts, extra host, resolv.conf path/origin, DNS nameservers/search/options, default sandbox, external key, exposed ports, port mappings, ingress marker, and load-balancer marker.

Control flow: each function returns a `SandboxOption` closure that mutates `sb.config` or sandbox flags. Exposed ports and port mappings defensively copy slices before storing in `config.generic` under netlabel keys for drivers. Ingress/load-balancer options append OSL sandbox type markers.

State and persistence: options initialize sandbox config that later affects file creation, namespace key selection, driver labels, exposed port data, and load balancer behavior. Some values are persisted indirectly through sandbox state or endpoint/driver state.

Dependencies and integration points: used by controller `NewSandbox`, restore flows, daemon container setup, network drivers via `netlabel`, and OSL sandbox type tuning.

Risks and test signals: missing defensive copies would let caller mutations affect driver config; this file avoids that for slices. Direct tests are mostly through sandbox creation and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go -->
