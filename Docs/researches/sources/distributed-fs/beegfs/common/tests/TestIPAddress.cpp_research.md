<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp

**Purpose:** Tests `IPAddress` parsing, classification, formatting, equality, hashing, IPv4-mapped IPv6 handling, binary conversion, and CIDR network containment.

**Important APIs/types/functions:** Fixtures and tests cover `IPAddress::resolve`, `isIPv4`, `isIPv6`, `isLoopback`, `isLinkLocal`, `equals`, `toString`, default constructor, unordered maps with `std::hash<IPAddress>`, `toIPv4InAddrT`, `hash`, and `IPNetwork::fromCidr().containsAddress`.

**Control flow:** A table drives parse/classification expectations for IPv4, IPv6, zero, loopback, link-local, mapped IPv4, ULA, and invalid strings. Separate tests compare loopbacks/all-addresses, mapped IPv4 equality and data equivalence, network masks from /0 to /128, and expected hash values from upper/lower 64-bit halves.

**State and persistence behavior:** In-memory tests only. They validate stable textual and binary representations that may be persisted in configs or protocol fields elsewhere.

**Dependencies and integration points:** Depends on `IPAddress`, `IPNetwork`, GoogleTest, and unordered map hashing. These signals matter for network interface selection and node addressing.

**Risks:** Some tests assume host byte order values for `in_addr_t` expectations. The `testMap` loop only inserts `"::"` due to the condition, despite the comment mentioning `::0`; coverage may be narrower than intended.

**Test signals:** Strong coverage for IPv4-mapped IPv6 normalization and CIDR containment across IPv4/IPv6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestIPAddress.cpp -->
