<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c

Purpose: provides KUnit round-trip tests for standard IEEE 1394 packet header helpers in `packet-header-definitions.h` and PHY packet helpers in `phy-packet-definitions.h`. It protects the mask/shift helpers used by `ohci.c` for packet parsing, self-ID processing, and synthetic self-ID construction.

Important APIs and control flow: helper functions serialize and deserialize common async header fields, request offsets, response rcodes, block lengths, extended tcodes, isochronous headers, self-ID zero packets, self-ID extended packets, and PHY config packets. Test cases cover async write quadlet/block request, write response, read quadlet/block request and response, lock request and response, one isochronous header vector, three self-ID layouts with port status extraction/insertion, and two PHY config packet forms. The suite is registered as `firewire-packet-serdes`.

State and persistence behavior: no state persists beyond each KUnit case. Tests use constant expected packet words and local zeroed output buffers.

Dependencies and integration points: depends on KUnit, FireWire constants, `packet-header-definitions.h`, and `phy-packet-definitions.h`. It is a direct test signal for the inline helpers consumed by the OHCI host controller driver.

Risks and test signals: the suite validates representative values but not every boundary or invalid input path. It does not currently exercise `self_id_sequence_enumerator_next()` error cases or every possible port index. It will catch common regressions such as wrong masks, shifts, setter clearing mistakes, data-length/extended-tcode swaps, and self-ID port-status packing errors. Test signal is a passing KUnit suite named `firewire-packet-serdes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-serdes-test.c -->
