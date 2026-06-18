<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestNIC.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestNIC.cpp

**Purpose:** Tests network interface discovery and NIC preference rule matching.

**Important APIs/types/functions:** `NetworkInterfaceCard::findAll`, `findNicPosition`, `IPAddress::resolve`, `NicAddress`, `NICADDRTYPE_STANDARD`, `NICADDRTYPE_RDMA`, and protocol fields.

**Control flow:** `testFindNICs` discovers non-loopback interfaces and asserts each has a name, standard or RDMA type, and IPv4 or IPv6 protocol, with at least one NIC found. `testFindNicPosition` builds synthetic IPv4/IPv6 standard/RDMA NICs and evaluates preference/deny rule lists including wildcard, protocol preference, interface preference, RDMA preference, address-specific rules, and negation.

**State and persistence behavior:** Reads live host NIC state in `testFindNICs`; synthetic tests are in-memory.

**Dependencies and integration points:** Important for node connection selection and `NodesTk::applyLocalNicListToList`. Depends on actual network environment for discovery test.

**Risks:** Live NIC discovery can fail in minimal CI containers without non-loopback interfaces. Rule parsing coverage is good but does not test malformed rules.

**Test signals:** Strong coverage for preference order and deny semantics in NIC selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestNIC.cpp -->
