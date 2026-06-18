# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.h

## Purpose
This header declares the command-specific HWRM helper layer used by probe, resource management, netdev open/close, VNIC setup, ring setup, stats, and link management.

## Important APIs, Types, And Functions
The declarations cover version/reset/time/driver registration, VNIC qcaps and configuration, NVM device info, backing-store qcaps/config, ring reservation, function qcaps/qcfg/resource qcaps, queue qportcfg, VNIC HDS/RSS/config/allocation/free, L2 filter allocation/free/mask, stat context allocation/free, ring allocation/free, async event completion-ring setup, TPA setup, link update/config/shutdown, and port/function stats queries.

## Control Flow
The header establishes the ordering used elsewhere: discover firmware capabilities, allocate backing-store memory, reserve resources, allocate software memory, allocate firmware rings/stat/VNIC/RSS/filter objects, enable link/TPA, then reverse those operations during close or remove.

## State And Persistence
No state is stored in the header. Its API mutates `struct bnge_dev`, `struct bnge_net`, `struct bnge_vnic_info`, `struct bnge_l2_filter`, `struct bnge_ring_struct`, and stats memory according to firmware command results.

## Dependencies And Integration Points
It depends on HSI constants and adjacent driver structures. `bnge_netdev.c`, `bnge_resc.c`, `bnge_rmem.c`, and `bnge_link.c` are the main consumers. The macros `BNGE_PLC_EN_*` and `BNGE_VNIC_CFG_ROCE_DUAL_MODE` alias HSI fields for local naming.

## Risks
The API is broad and has mixed ownership conventions: some functions allocate firmware IDs, some free them, some only query and cache capabilities, and some silently ignore unsupported optional features. Callers must pair allocation/free functions carefully and must not use firmware IDs after they are reset to invalid values.

## Test Signals
Build coverage catches mismatched prototypes. Runtime coverage should include full probe/open/close, link configuration, stats query, RSS setup, filter updates, and error paths where a later allocation fails after earlier firmware objects were created.
