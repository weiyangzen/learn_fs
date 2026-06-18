# `sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic.h`

## Purpose

`cnic.h` is the private header for `cnic.c`. It defines the CNIC driver's ring geometry, hardware context offsets, default TCP/iSCSI parameters, DMA bookkeeping structures, UIO state, per-device private state, and `bnx2x` constants/macros used to bridge Broadcom/QLogic Ethernet devices to CNIC ULPs. It is source-local infrastructure rather than a public ULP interface; public-facing structures such as `struct cnic_dev`, `struct cnic_sock`, and `struct cnic_ulp_ops` come from `cnic_if.h`.

## Important Types, Macros, and Constants

Queue and completion sizing:

- `KWQ_PAGE_CNT` and `KCQ_PAGE_CNT` set KWQ and KCQ page counts to 4 and 16.
- `KWQ_CID` and `KCQ_CID` reserve context IDs 24 and 25 for `bnx2` kernel work/completion queues.
- `KWQE_CNT`, `KCQE_CNT`, `MAX_KWQE_CNT`, `MAX_KCQE_CNT`, `MAX_KWQ_IDX`, and `MAX_KCQ_IDX` derive queue entry counts and ring masks from `BNX2_PAGE_SIZE`.
- `KWQ_PG()`, `KWQ_IDX()`, `KCQ_PG()`, and `KCQ_IDX()` translate logical producer/consumer indices into page and entry offsets.
- `BNX2X_NEXT_KCQE()` and `BNX2X_NEXT_RCQE()` encode the `bnx2x` convention of skipping chain-next entries at page boundaries.
- `MAX_COMPLETED_KCQE` limits one service batch to 64 completions.

Hardware context and page-table constants:

- `L5_KRNLQ_*` offsets and `KRNLQ_*` bit masks define the `bnx2` kernel queue context layout used by `cnic_start_bnx2_hw()`.
- `BNX2_PG_CTX_MAP` and `BNX2_ISCSI_CTX_MAP` identify `bnx2` context map registers read during 5709 context allocation.
- `BNX2_MAX_CID`, `MAX_CNIC_L5_CONTEXT`, `MAX_CM_SK_TBL_SZ`, and `MAX_ISCSI_TBL_SZ` bound context and socket tables.
- `CDU_VALID_DATA()`, `CDU_CRC8()`, and `CDU_RSRVD_VALUE_TYPE_A()` compute `bnx2x` context validation bytes for iSCSI/FCoE XCM/UCM regions.

Default protocol settings:

- `CNIC_LOCAL_PORT_MIN`, `CNIC_LOCAL_PORT_MAX`, and `CNIC_LOCAL_PORT_RANGE` define the ephemeral local TCP source-port range CNIC uses for offloaded connections.
- `DEF_IPID_START`, `DEF_KA_TIMEOUT`, `DEF_KA_INTERVAL`, `DEF_KA_MAX_PROBE_COUNT`, `DEF_TOS`, `DEF_TTL`, `DEF_RCV_BUF`, `DEF_SND_BUF`, `DEF_MAX_RT_TIME`, `DEF_MAX_DA_COUNT`, `DEF_SWS_TIMER`, and `DEF_MAX_CWND` supply default IP/TCP keepalive, buffer, delayed-ACK, and congestion/window settings.

Core state structures:

- `struct cnic_ctx` stores one firmware context block's base CID, CPU pointer, and DMA mapping.
- `struct cnic_dma` stores coherent DMA page arrays, per-page DMA addresses, optional page table memory, and the page-table DMA address.
- `struct cnic_id_tbl` wraps a spinlocked bitmap allocator with `start`, `max`, and `next` fields.
- `struct kwqe_16_data` is a 128-byte per-connection backing buffer for `bnx2x` slow-path ramrod parameters referenced by physical address.
- `struct cnic_iscsi` groups per-iSCSI-connection task array, R2T queue, and HQ DMA allocations.
- `struct cnic_context` maps one logical L5 CID to firmware CID, KWQE data buffer, waitqueue state, timestamp, context flags, protocol id, and protocol-specific resources.
- `struct kcq_info` describes one KCQ ring: DMA storage, page pointers, hardware/software producer indexes, status index pointer, producer doorbell address, and index helper callbacks.
- `struct cnic_uio_dev` tracks the UIO registration and DMA mappings exposed to userspace for BAR, status block, L2 ring, and L2 buffer access.
- `struct cnic_local` is the main per-device private state used by `cnic.c`.

`struct cnic_local` contains several groups of state:

- ULP synchronization and callback state: `cnic_ulp_lock`, `ulp_handle[]`, `ulp_flags[]`, and RCU `ulp_ops[]`.
- Device and lower-driver links: `dev`, `ethdev`, `udev`, `chip_id`, `func`, `shmem_base`, and `cnic_ops`.
- L2/UIO ring state: ring sizes, RX/TX consumer pointers, and cached consumers.
- KWQ/KCQ DMA and index state: `kwq_info`, `kwq_16_data_info`, `kwq`, producer/consumer indexes, `kcq1`, `kcq2`, and `completed_kcq`.
- Interrupt/status state: status block union, default `bnx2x` status block, status block ids, IGU id, interrupt number, last status index, and bottom-half work item.
- Connection state: `csk_tbl`, source-port table, iSCSI/FCoE CID tables, connection count, start CIDs, max CID space, per-connection sizing, and delayed delete work.
- Context memory: `ctx_tbl`, `ctx_arr`, block count/size/alignment, and CIDs per block.
- Hardware-family operation pointers: start/stop hardware, page-table setup, resource alloc/free, CM init/stop, interrupt enable/disable/ack/arm, and close-connection callback.

BNX2X constants and macros:

- `BNX2X_CONTEXT_MEM_SIZE`, `BNX2X_FCOE_CID`, `BNX2X_ISCSI_START_CID`, `BNX2X_ISCSI_NUM_CONNECTIONS`, task/R2T/HQ/global buffer sizes, and cache sentinel values define `bnx2x` offload memory geometry.
- `BNX2X_FCOE_NUM_CONNECTIONS` and `BNX2X_FCOE_L5_CID_BASE` partition FCoE L5 CIDs after iSCSI table entries.
- `BNX2X_CHIP_IS_E2_PLUS()`, `BNX2X_HW_CID()`, `BNX2X_SW_CID()`, `BNX2X_CL_QZONE_ID()`, `MAX_STAT_COUNTER_ID`, and `CNIC_SUPPORTS_FCOE()` provide chip-generation-aware address/id calculations.
- `BNX2X_SHMEM_ADDR()`, `BNX2X_SHMEM2_ADDR()`, `BNX2X_SHMEM2_HAS()`, and `BNX2X_MF_CFG_ADDR()` calculate shared-memory and multi-function configuration offsets.
- `CNIC_RAMROD_TMO` sets the ramrod wait timeout to `HZ / 4`.

## Control Flow Role

This header does not implement executable control flow, but it directly shapes the control flow in `cnic.c`. Queue index macros define how service loops advance through KWQ/KCQ/RCQ rings. Context constants drive the hardware start paths that program `bnx2` kernel queue contexts and `bnx2x` storm/context tables. State flags in `struct cnic_local` and `struct cnic_context` control whether rings are initialized, whether L2 setup/halt is waiting, whether iSCSI should be stopped asynchronously, and whether CIDs are offloaded or waiting for delayed delete.

The function-pointer table embedded in `struct cnic_local` is the key dispatch mechanism. `init_bnx2_cnic()` and `init_bnx2x_cnic()` fill these pointers with family-specific implementations, allowing common lifecycle functions such as `cnic_start_hw()`, `cnic_stop_hw()`, `cnic_cm_open()`, and `cnic_cm_process_kcqe()` to call hardware-specific behavior without repeatedly branching on chip family.

## State and Persistence Behavior

The header defines only in-memory state. All structures are allocated and initialized by `cnic.c` at module/device/connection startup and released during device shutdown or module exit. DMA structures describe coherent memory that persists only while the device is active or, for UIO rings, while a UIO object remains open. Bitmap ID tables persist only for the lifetime of the corresponding CNIC resource allocation and are not serialized.

State flags are significant:

- `ULP_F_INIT`, `ULP_F_START`, and `ULP_F_CALL_PENDING` track ULP callback lifecycle.
- `CNIC_LCL_FL_KWQ_INIT`, `CNIC_LCL_FL_L2_WAIT`, `CNIC_LCL_FL_RINGS_INITED`, and `CNIC_LCL_FL_STOP_ISCSI` track queue/ring initialization and asynchronous stop work.
- `CTX_FL_OFFLD_START`, `CTX_FL_DELETE_WAIT`, and `CTX_FL_CID_ERROR` track firmware context ownership, delayed delete scheduling, and CFC delete errors.

## Dependencies and Integration Points

`cnic.h` depends on types and constants included before it by `cnic.c`, especially `struct kwqe`, `struct kcqe`, `struct cnic_dev`, `struct cnic_eth_dev`, `struct cnic_sock`, `struct cnic_ulp_ops`, `BNX2_PAGE_SIZE`, `BNX2_PAGE_BITS`, `CHIP_IS_*`, `BP_PORT()`, `BP_VN()`, `NO_FCOE()`, `struct bnx2x`, firmware HSI structures, and storm-memory offset macros. It is therefore tightly coupled to the Broadcom driver and firmware header include order.

The header's structures are consumed almost exclusively by `cnic.c`, while its constants encode contracts with:

- `bnx2` context memory/register programming.
- `bnx2x` storm-memory, context, and IGU/status-block programming.
- iSCSI and FCoE firmware command formats.
- UIO ring layout shared with user-space consumers.
- CNIC ULP callback and connection-manager state from `cnic_if.h`.

## Risks and Edge Cases

- The queue size/index macros assume page-sized rings and power-of-two-like masks from firmware entry sizes. Any change in `struct kwqe`, `struct kcqe`, or page sizing could alter ring wrap behavior.
- `BNX2X_NEXT_KCQE()` and `BNX2X_NEXT_RCQE()` hide a hardware chain-entry skip rule. Reusing plain increment logic in `cnic.c` would corrupt ring traversal.
- `CNIC_SUPPORTS_FCOE(cp)` ignores its formal argument and references `bp`, relying on call sites to have a local variable named `bp`. This is fragile macro hygiene.
- `MAX_STAT_COUNTER_ID` is conditionally defined using `bp`, also requiring call-site scope discipline.
- `struct cnic_local` is large and owns many resource classes. Adding fields requires careful pairing in allocation, error unwinding, shutdown, and UIO-open cases.
- `struct cnic_id_tbl.next` wrap uses `(id + 1) & (max - 1)`, which only behaves as intended when `max` is a power of two. Current iSCSI and FCoE table sizes are powers of two, but the local port range macro is not obviously power-of-two-safe if changed.
- Hardware constants such as CIDs, status-block indexes, and queue sizes are magic values derived from firmware contracts. They need hardware/firmware validation, not just C compile coverage.

## Test Signals and Validation Ideas

- Compile both `bnx2` and `bnx2x` CNIC configurations and ensure all macro dependencies resolve under the intended include order.
- Use static assertions or build-time checks if queue counts, local port range assumptions, or CID table sizes are modified.
- Exercise KCQ/RCQ page-boundary completion traversal on `bnx2x` to confirm chain-next entries are skipped.
- Validate DMA page table byte ordering separately for `bnx2` and `bnx2x` devices.
- Test FCoE-capability paths on E1/E1H/E2/E3 combinations, especially macros that depend on a local `bp`.
- Stress resource open/close with UIO users active to verify `struct cnic_uio_dev` and ring fields remain valid across CNIC device teardown and reattach.
