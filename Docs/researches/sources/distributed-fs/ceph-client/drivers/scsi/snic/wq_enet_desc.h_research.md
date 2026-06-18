## sources/distributed-fs/ceph-client/drivers/scsi/snic/wq_enet_desc.h

### Purpose
Defines the 16-byte Ethernet-style work queue descriptor used by Cisco vNIC queues and inline encode/decode helpers. SNIC uses this descriptor format to send firmware request buffers over the vNIC work queue even though the payloads are SCSI/FNIC/SNIC control structures.

### Important APIs, Types, and Constants
- `struct wq_enet_desc` contains little-endian `address`, `length`, `mss_loopback`, `header_length_flags`, and `vlan_tag`.
- Bit masks and shifts define fields for length, MSS, loopback, header length, offload mode, EOP, CQ-entry request, FCoE encapsulation, VLAN insertion, and VLAN tag.
- Offload modes include checksum, reserved, L4 checksum, and TSO.
- `wq_enet_desc_enc()` packs host-order arguments into the little-endian descriptor fields.
- `wq_enet_desc_dec()` reverses the operation for diagnostics or validation.

### Control Flow and State
The helpers are pure pack/unpack routines. Runtime state is in descriptor rings allocated by `vnic_wq.c`; descriptor publication happens through `svnic_wq_post()` after callers encode the descriptor.

### Dependencies and Integration Points
The file relies on Linux endian conversion helpers. SNIC queue submission code calls the encoder before posting a WQ entry and requests completion queue notifications with the CQ-entry flag.

### Risks and Test Signals
Risks are bitfield truncation and endian mistakes. Boundary tests should encode/decode maximum length, MSS, and header length values, check VLAN/offload flags independently, and validate descriptor bytes consumed by firmware.
