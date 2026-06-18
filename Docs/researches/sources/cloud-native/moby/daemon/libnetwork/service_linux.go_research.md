<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_linux.go

Purpose: Linux dataplane implementation for swarm service load balancing, ingress port rules, IPVS backends, and firewall marks.

Important APIs/functions: `Sandbox.populateLoadBalancers`, `Network.findLBEndpointSandbox`, `findIfaceDstName`, `Network.addLBBackend`, `Network.rmLBBackend`, ingress helpers (`addIngressPorts`, `removeIngressPorts`, `restoreIngressPorts`, `filterPortConfigs`, `initIngressConfiguration`, rule generation/program/delete), proxy helpers, `configureFWMark`, and `addRedirectRules`.

Control flow: adding a backend finds the LB endpoint sandbox, ensures VIP alias and IPVS service exist, configures ingress ports and firewall mark rules, adds IPVS destination, and applies OS tweaks. Removing deweights or deletes destinations, removes service/VIP/firewall/ingress state when last backend leaves. Ingress setup creates `DOCKER-INGRESS`, NAT/filter jumps, route_localnet, MASQUERADE, per-port DNAT/ACCEPT rules, and dummy listeners to reserve ingress ports.

State and persistence: global ingress rule/proxy/reference maps, kernel iptables state, IPVS state, namespace aliases, and `/proc` sysctl writes.

Dependencies and integration points: `moby/ipvs`, iptables, bridge driver chains, netlink, SCTP, sandbox `ExecFunc`.

Risks and test signals: rollback/refcount correctness is critical; IPv6 TODOs remain. Direct tests are not in this subset; broader swarm/ingress integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_linux.go -->
