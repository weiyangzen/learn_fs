# sources/distributed-fs/ceph-client/include/linux/mlx5/device.h

## Purpose
Defines mlx5 hardware ABI helpers and structures: IFC bitfield accessors, command/init segments, event and CQE layouts, work-queue and memory-key constants, capability access macros, flow/vport/protocol enums, and command/status/counter vocabulary.

## Important APIs/Types
The `MLX5_SET/GET/SET64/GET64/GET16/SET16/ADDR_OF` macro family manipulates generated `mlx5_ifc_*_bits` layouts. Enums cover inline modes, command limits, CQ states, permissions, PCI controls, BFREG/UAR limits, MKey/UMR masks, event types, driver events, tracer/general/port subtypes, RoCE, opcodes, TLS WQE opmods, set-port fields, bandwidth units, ODP caps, command statuses, and counter groups.

Structures include command layout, health/init segments, many `mlx5_eqe_*` payloads, packed `mlx5_eqe`, command data blocks, error and normal CQEs, mini CQEs, signature-error CQE, SRQ next segment, MKey segment, and ODP caps. Inline helpers decode CQE format/opcode, compressed CQE counts, LRO flags, L4 type, tunnel/TLS/VLAN bits, timestamps, flow tags, MPWQE byte/stride/filler fields, and pkey table sizes. Capability macros read current/max HCA caps across general, Ethernet, RoCE, atomic, flow table, eswitch, ODP, QoS, debug, device memory, TLS, IPsec, crypto, MACsec, SHAMPO, PSP, and virtualization features.

## Control Flow
mlx5 core maps the init segment, starts the command interface, queries capabilities into `mdev->caps`, and gates upper-layer features through macros. EQ polling decodes typed event payloads; CQ processing decodes CQEs, mini-CQEs, checksums, timestamps, RSS, LRO/MPWQE, TLS/tunnel state, and error syndromes.

## State And Persistence
Hardware-shared persistent state includes init and health segments, command queues, timers, EQEs, CQEs, MKeys, UMR translations, capability snapshots, and vport/flow-table configuration.

## Dependencies And Integration Points
Depends on RDMA verbs, generated `mlx5_ifc`, bitfield/endian helpers, and mlx5 driver structures. Integrates with mlx5_core/e/ib, eswitch, flow steering, ODP/HMM, TLS/IPsec/MACsec/crypto, vDPA/TLP, devlink health, firmware reset/live patch, and PTP/PPS.

## Risks
IFC layout drift, bit/endian misuse, missing cap allocation for new cap types, compressed CQE decode bugs, packed ABI changes, mask overflow, event subtype collisions, and confusing current versus max caps.

## Test Signals
Bitfield round trips, capability query coverage, init/health reads, command status decoding, EQ events, CQE parsing for checksum/RSS/VLAN/tunnel/TLS/LRO/MPWQE/compression, MKey/UMR programming, flow capability gating, and endian/sparse builds.
