<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go

Purpose: generates and verifies Markdown documentation for the bridge driver's nftables backend using live daemon/network/container scenarios.

Important APIs/types/functions: shares scenario descriptors with the iptables documentation test: `ctrDesc`, `networkDesc`, `section`, `index`, `TestBridgeNftablesDoc`, `runTestNet`, `createBridgeNetworks`, `createServices`, `runNftables`, `lines`, and `generate`. `runNftables` captures `nft -s list table ip docker-bridges`, normalizes the output priority wording, and breaks the table into template-addressable blocks.

Control flow: the test skips when firewalld is running, rootless mode is active, or the daemon is not using nftables. It creates isolated L3 host namespaces, starts a daemon per scenario, creates configured bridge networks and containers, captures nftables state, renders a Markdown template, writes a bundle artifact, and golden-compares with `generated/`. Swarm support is present in struct fields but commented out in the nftables scenario/index and service helper.

State/persistence: creates temporary netns/daemons/networks/containers and writes generated docs to the test bundle directory. Repository golden files are read for comparison and updated only under external golden update mode.

Dependencies/integration: depends on Linux nftables, bridge driver options, `networking.L3Segment`, daemon helper, templates, gotest `golden`, and `iter.Seq` for line iteration.

Risks: requires stable nftables output format and rule ordering. The parser uses string keys derived from block headers, so template keys can break if nft syntax changes. Swarm sections are disabled/commented, leaving ingress nftables documentation less covered than iptables.

Test signals: passing tests mean observed nftables bridge rules match the documented generated Markdown for new daemon, port publishing, ICC, internal, routed, nat-unprotected, and loopback host-port scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go -->
