# sources/distributed-fs/ceph-client/include/rdma/ib_pack.h

Purpose: declares generic bit-field packing/unpacking utilities and unpacked header structures for InfiniBand UD-style packet construction, including LRH, Ethernet/VLAN, GRH, IPv4/UDP, BTH, DETH, and immediate data.

Important APIs and types: byte-size constants define link, Ethernet/VLAN, GRH, IPv4, UDP, BTH, DETH, atomic/XRC, and ICRC header lengths. `struct ib_field` describes a mapping between C structure fields and bit positions in a packed buffer. Opcode enums define transport bases and concrete RC/UC/RD/UD opcodes through `IB_OPCODE()`, plus local/global LNH values. Unpacked structs model LRH, GRH, BTH, DETH, Ethernet, IPv4, UDP, VLAN, and aggregate `struct ib_ud_header` with presence flags. APIs are `ib_pack()`, `ib_unpack()`, `ib_ud_ip4_csum()`, `ib_ud_header_init()`, and `ib_ud_header_pack()`.

Control flow: callers initialize an `ib_ud_header` for the desired encapsulation and payload size, optionally compute IPv4 checksum fields, then pack the header into a wire buffer. Generic pack/unpack functions use descriptor arrays to move bitfields between native structs and network buffers.

State and persistence: no state is stored. Structures are caller-owned packet assembly/parse state.

Dependencies and integration points: depends on `ib_verbs.h`, Ethernet UAPI constants, GID types, and the RDMA packet transmit path. It integrates software header construction with drivers and transports that need to build UD, RoCE, or encapsulated packets.

Risks and test signals: risks include descriptor offset mistakes, opcode constant drift, bitfield truncation, checksum mismatch, payload length errors, and inconsistent presence flags causing malformed packets. Test pack/unpack round trips, known IB/RoCE header byte vectors, IPv4 checksum vectors, each encapsulation combination, immediate-data cases, and boundary payload sizes.
