<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h -->
# sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h

Purpose: Shared packet and transaction structure definitions for `nosy-dump` and protocol decoders.

Important APIs/types/functions: Defines ACK helper macros, `TCODE_PHY_PACKET`, PHY packet identifiers, `struct phy_packet`, `struct link_packet`, `struct subaction`, and `struct link_transaction`. Declares `int decode_fcp(struct link_transaction *t)`.

Control flow: This header has no executable flow, but its unions/bitfields define how packet decoding code interprets captured quadlets. Flexible-array members in block packet layouts model variable payload data followed by CRC/ACK.

State and persistence: The structs represent in-memory decoded packet state and pending transactions. No persistence is defined here.

Dependencies/integration: Includes `<stdint.h>` and `list.h`; uses Linux FireWire tcode constants indirectly through C files. It is the contract between `nosy-dump.c` and `decode-fcp.c`.

Risks/tests: Risks are ABI/layout assumptions from C bitfields, zero-length arrays, and host endian differences. Test signals include compilation on target architectures, packet decode comparisons against known FireWire traces, and sanitizers for variable-length packet access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.h -->
