# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_mm.sh

Purpose: Tests MAC Merge / frame preemption configuration and verification through ethtool on two connected interfaces.

Important APIs/functions: `traffic_test()`, `manual_with_verification()`, directional wrappers, `manual_without_verification()`, `manual_failed_verification()`, `smallest_supported_add_frag_size()`, `expected_add_frag_size()`, `lldp_change_add_frag_size()`, `lldp()`, `h1_create()`, `h2_create()`, cleanup/setup helpers, ethtool MM commands, and LLDP traffic handling.

Control flow: The script initializes two interfaces, configures MAC Merge in multiple modes, sends traffic to validate connectivity, checks verification success/failure expectations, calculates supported add-frag-size values, and verifies LLDP interaction with add-frag-size configuration.

State and persistence: Mutates ethtool MM/preemption settings, link state, and possibly LLDP-related state; cleanup restores interface setup through forwarding helpers.

Dependencies and integration points: Requires hardware and driver support for ethtool MM, two connected ports, forwarding helpers, and traffic generation.

Risks and test signals: Failures map to MAC Merge verification, add-frag-size validation, LLDP integration, or ethtool MM reporting regressions.
