# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.h

Purpose: hardware and firmware ABI header for the 3Com Typhoon 3XP driver. It defines the shared DMA layout, descriptor formats, command opcodes, response/stat structures, offload bits, wake-event bits, firmware image records, MMIO register offsets, boot commands, interrupt bits, and status values.

Important APIs, types, and functions: central data types are `struct basic_ring`, `struct transmit_ring`, `struct typhoon_indexes`, `struct typhoon_interface`, `struct tx_desc`, `struct tcpopt_desc`, `struct ipsec_desc`, `struct rx_desc`, `struct rx_free`, `struct cmd_desc`, `struct resp_desc`, `struct stats_resp`, `struct sa_descriptor`, `struct typhoon_file_header`, and `struct typhoon_section_header`. `INIT_COMMAND_NO_RESPONSE()` and `INIT_COMMAND_WITH_RESPONSE()` standardize command descriptor initialization.

Control flow: the header is declarative, but it directly drives driver flow: the host fills `typhoon_interface`, the 3XP updates `typhoon_indexes`, TX/RX/command/response rings are advanced by byte offsets, firmware is described by file and section headers, and boot/download handshakes use `TYPHOON_REG_*`, `TYPHOON_BOOTCMD_*`, and `TYPHOON_STATUS_*`.

State and persistence: all shared state is little-endian packed hardware state. The first four `typhoon_indexes` fields are host-written and NIC-read; the remaining fields are NIC-written and host-read. Descriptor `flags` encode type, validity, response/error state, and option subtype.

Dependencies and integration points: consumed by `typhoon.c` and tightly coupled to firmware `3com/typhoon.bin`. It assumes Linux endian helpers and packed layout semantics. The constants bridge Linux netdev concepts such as VLAN, checksum, TSO, link state, and wake events into 3XP command fields.

Risks: ABI layout changes would corrupt DMA communication. Many constants are little-endian expressions rather than plain integers, so comparisons and assignments must preserve endian expectations. IPsec structures are present even though the driver does not implement full IPsec offload. The comments state current 3XP versions only use low 32-bit bus addresses.

Test signals: compile-time structure use, successful firmware boot-record handoff, valid command/response processing, correct stats decoding, checksum/VLAN/TSO flags observed on traffic, link/WOL command behavior, and no sparse/endian warnings around descriptor fields.
