# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/irdma.h

## Purpose
`irdma.h` is the common hardware register and capability contract shared across IRDMA generations. It defines generic register enum slots, common bit masks, shift/mask table indexes, multicast context structures, hardware generation enum values, and hardware attribute structures.

## Important APIs, types, and functions
Important definitions include `enum irdma_registers`, `enum irdma_shifts`, `enum irdma_masks`, `enum irdma_vers`, `struct irdma_uk_attrs`, `struct irdma_hw_attrs`, and multicast group context structures. It declares `i40iw_init_hw`, `icrdma_init_hw`, `ig3rdma_init_hw`, and `ig3rdma_get_reg_addr`.

## Control flow, state, and persistence
There is no executable flow. The enum order is persistent ABI within the driver because generation-specific files fill arrays indexed by these enums and common code reads register pointers and masks through the same indexes.

## Dependencies and integration points
This header is included by generation hardware headers and common type/control code. It bridges hardware-specific register maps with common CQP, interrupt, HMC, statistics, and verbs capability logic.

## Risks and test signals
Risks are enum/table ordering drift, bit mask width mistakes, and capability fields being interpreted differently by user/kernel paths. Tests should include table-size validation, generation init smoke tests, and verbs capability checks across Gen1, Gen2, and Gen3.
