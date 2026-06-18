# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.h

## Purpose
`i40iw_hw.h` contains Gen1 i40e PF/VF register offsets, bit masks, shift definitions, doorbell offsets, interrupt constants, and hardware capability constants.

## Important APIs, types, and functions
The header exports `i40iw_init_hw`. Key definitions include PF/VF PE queue registers, `I40E_PFINT_*` interrupt registers, `I40E_GLPES_*` statistics registers, CQP status masks, CQ/CEQ field masks, and `enum i40iw_device_caps_const`.

## Control flow, state, and persistence
There is no runtime control flow. The file is a compile-time hardware contract consumed by `i40iw_hw.c`; its values become persistent runtime register pointers and attribute limits after `i40iw_init_hw`.

## Dependencies and integration points
It relies on Linux bit macros and common IRDMA constants from included users. It is tightly coupled to `i40iw_hw.c` table ordering and the common `enum irdma_registers`, `enum irdma_masks`, and `enum irdma_shifts`.

## Risks and test signals
The main risk is register or mask drift versus i40e hardware specifications. Test signals include read/write smoke tests on interrupt and CQP registers, capability exposure checks through RDMA core, and compile-time/table-size validation when common enum entries change.
