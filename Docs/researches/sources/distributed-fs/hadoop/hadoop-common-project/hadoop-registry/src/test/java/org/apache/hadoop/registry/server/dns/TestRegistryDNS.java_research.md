# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestRegistryDNS.java

Purpose: comprehensive tests for `RegistryDNS`, converting YARN registry `ServiceRecord` data into DNS records and replies.

Important APIs and functions: fixture initializes `RegistryDNS`, domain name, zones, TTL, and a service-record marshal. Tests cover application registration, container registration, missing persistence, TTLs, reverse PTR lookup, large-network reverse zones, missing reverse records, records without IPs, DNSKEY signing primitives, IPv4-to-IPv6 mapping, AAAA lookup, negative lookup authority SOA, reading master zone files, reverse zone name calculation, split reverse zones, external CNAME, root NS lookup, multiple A records, and upstream fault behavior.

Control flow: tests marshal JSON service records, call `registryDNS.register(path, record)`, build dnsjava `Message` queries, invoke `generateReply()`, and inspect RCODE, questions, answer sections, record types, TTLs, and signatures. `assertDNSQuery()` doubles expected answer count when DNSSEC is enabled by subclasses.

State and persistence: dynamic DNS state is held inside `RegistryDNS` zones and stopped after each test. Some tests read static zone resources and DNSSEC private key resources from the test classpath.

Dependencies and integration: integrates registry constants, YARN service record attributes, dnsjava record types, DNSSEC, RSA keys, reverse-zone utilities, and `BaseServiceRecordProcessor`.

Risks and test signals: very strong behavior signal for DNS mapping and negative responses. Tests rely on fixed static JSON and test resource files; changes in dnsjava ordering or DNSSEC output can affect assertions.
