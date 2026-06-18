# sources/distributed-fs/ceph-client/include/rdma/ib_pma.h

Purpose: defines Performance Management Agent MAD attribute IDs, capability bits, wire structures, and counter-select masks for InfiniBand port sampling and port counter queries.

Important APIs and types: capability flags include all-port select, extended width variants, and transmit wait support. Attribute IDs cover class port info, port samples control/result/result-ext, port counters, and extended port counters. `struct ib_pma_mad` provides a PMA MAD wrapper. Sampling structs model control, 32-bit result, and 64-bit extended result records. `struct ib_pma_portcounters` and `struct ib_pma_portcounters_ext` represent standard and extended port counters, with select masks for symbol/link/receive/transmit/discard/constraint/VL15 and 64-bit data/packet/unicast/multicast counters.

Control flow: PMA clients or agents form MADs with these attribute IDs and structs, select counters through masks, and read or update counter records through the MAD subsystem. Extended counters are used when capability bits indicate support.

State and persistence: no local state is stored. The structures mirror hardware-maintained port counters and sampling controls; hardware owns counter persistence until reset/clear per device behavior.

Dependencies and integration points: depends on `ib_mad.h` for MAD headers and byte-order constants. It integrates performance query tooling, subnet management, and provider PMA implementations.

Risks and test signals: risks include packed layout mismatch, counter-select masks not matching struct fields, 32-bit counter wrap handling, extended capability misdetection, and endian mistakes in MAD payloads. Test PMA MAD encode/decode, standard vs extended counter queries, sampling control/result paths, counter wrap behavior, and devices with/without extended-width capabilities.
