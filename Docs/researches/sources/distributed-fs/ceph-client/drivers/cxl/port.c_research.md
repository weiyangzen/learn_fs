# sources/distributed-fs/ceph-client/drivers/cxl/port.c

Purpose: CXL bus driver for CXL ports. It enumerates switch/endpoint port services, reads CDAT, sets up HDM decoders and RAS, creates endpoint ports for memdevs, and opportunistically assembles committed regions.

Important APIs/types/functions: `cxl_port_probe()`, `cxl_switch_port_probe()`, `cxl_endpoint_port_probe()`, `cxl_ras_unmask()`, `discover_region()`, `cxl_port_add_dport()`, `devm_cxl_add_endpoint()`, CDAT binary sysfs read/visibility, and `cxl_port_driver`.

Control flow and state: switch probe resets dport count and caches CDAT. Endpoint probe reads/parses CDAT, registers a detach action for the memdev, sets up endpoint decoders, handles RCH RAS mapping, unmasks RAS errors when OS controls AER, and scans decoder children for auto-enabled regions. `cxl_port_add_dport()` lazily sets up switch registers/decoders/RAS on the first dport, adds the dport, parses downstream CDAT, and updates decoder targets. `devm_cxl_add_endpoint()` backfills `cxl_ep->next` links up the parent chain and creates the endpoint port.

Dependencies and integration: depends on CXL memdevs, decoder setup, CDAT parsing, PCI/AER, RAS helpers, devres groups, device locks, and the CXL bus.

Risks and test signals: first-dport devres grouping, RCH vs VH setup ordering, parent driver checks, region autodiscovery failures, and RAS unmask privilege are sensitive. Test switch rebind, endpoint detach/rebind, missing CDAT/RAS/registers, first and later dports, auto-region assembly from committed decoders, CDAT sysfs visibility, and OS-vs-BIOS AER ownership.
