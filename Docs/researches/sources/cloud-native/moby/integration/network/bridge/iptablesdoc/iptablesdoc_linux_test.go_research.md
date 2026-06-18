<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go

Purpose: generates and verifies Markdown documentation for bridge-driver iptables rules across selected daemon/network/container/swarm configurations.

Important APIs/types/functions: data structs `ctrDesc`, `networkDesc`, and `section` describe documentation scenarios; `index` lists scenarios such as new daemon, port mapping with/without userland proxy, ICC disabled, internal networks, routed/nat-unprotected gateway modes, swarm ingress, and loopback-published ports. `TestBridgeIptablesDoc`, `runTestNet`, `createBridgeNetworks`, `createServices`, `pollService`, `runIptables`, and `generate` orchestrate the test.

Control flow: the test skips under firewalld, rootless, or nftables backend. It creates an `L3Segment`, then one host namespace per section. For each section it starts a daemon in that namespace, optionally initializes swarm or creates bridge networks/containers, zeroes iptables counters, captures several `iptables` views, normalizes packet/byte counters, renders a template from `templates/<section>`, writes the generated Markdown under the bundle directory, and compares with `generated/<section>`.

State/persistence: creates temporary namespaces, daemons, networks, containers, services, firewall rules, generated bundle files, and golden-doc comparisons. No repository files are updated unless the test is run with gotest golden update flags.

Dependencies/integration: depends on `networking.L3Segment`, `daemon.Daemon`, `netlink.GenlFamilyGet("IPVS")`, swarm APIs, bridge driver options, text templates, gotest `golden`, and host `iptables`. It documents libnetwork's iptables backend by observing real rules rather than mocking them.

Risks: highly environment-sensitive: requires privileged iptables backend, no firewalld, working IPVS for swarm sections, and stable rule ordering/output. Template/golden drift must be reviewed carefully because expected rule changes can be functional regressions or legitimate backend changes. Counter normalization handles only one class of CI noise.

Test signals: failures provide generated docs in the bundle path and diffs against `generated/`. Passing tests signal that the iptables rules emitted by bridge networking still match the documented rule set for all configured scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go -->
