# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_hw.h

Defines the ERDMA hardware ABI: register offsets, BAR and MSI-X constants, doorbell layouts, command queue opcodes and descriptors, WQE/CQE/EQE formats, capability masks, protocol enums, and status/opcode values.

Important groups include PCI/register constants, device control/status masks, DB space offsets, CQ/EQ DB fields, queue element sizes, CMDQ submodules/opcodes/header masks, create/destroy EQ/CQ/QP/AH requests, MR registration requests, GID/stats/query formats, capability response masks, CQE layouts, SGE/RQE/SQE layouts, AEQE/CEQE formats, opcodes, WC statuses, and vendor errors.

There is no executable flow. All ERDMA command submission and queue parsing depends on these layouts. The structures are persistent hardware-visible state in coherent queues, BAR registers, and doorbell records; owner bits, phase/index fields, WQEBB counts, cookies, and queue depths define ring protocols.

Dependencies are kernel types and Ethernet constants. Risks are hardware ABI drift, wrong endian annotations, mask mistakes, log-size vs count conversion mistakes, and doorbell/vector indexing mismatches. Test signals include probe capability decode, CMDQ operations, QP/CQ/EQ creation, all WQE opcodes, CQE status mapping, RoCEv2 GID/AH commands, iWARP modify-QP commands, and stats queries.
