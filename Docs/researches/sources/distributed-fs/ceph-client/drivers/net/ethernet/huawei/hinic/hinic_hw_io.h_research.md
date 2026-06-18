# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.h

## Purpose
Declares the HINIC IO-channel state and lifecycle APIs. It defines doorbell sizing, WQ page sizing, DB types, IO paths, doorbell free-list bookkeeping, NIC config cache, and the `hinic_func_to_io` aggregate used by the hardware device.

## Important APIs, Types, and Functions
Key constants are `HINIC_DB_PAGE_SIZE`, `HINIC_DB_SIZE`, `HINIC_HW_WQ_PAGE_SIZE`, `HINIC_DEFAULT_WQ_PAGE_SIZE`, and `HINIC_DB_MAX_AREAS`. Important types are `hinic_db_type`, `hinic_io_path`, `hinic_free_db_area`, `hinic_nic_cfg`, `hinic_func_to_io`, and `hinic_wq_page_size`. Public APIs create/destroy QPs, init/free IO, and set WQ page size.

## Control Flow
The header has no execution. It defines the state consumed by `hinic_hw_io.c`, `hinic_hw_dev.c`, command queue code, QP code, and upper NIC modules.

## State and Persistence Behavior
`hinic_func_to_io` is long-lived during interface-up state and stores queue arrays, depths, doorbells, coherent CI memory, command queue resources, VF metadata, link status, and cached pause/autoneg configuration. `hinic_wq_page_size` is serialized to firmware.

## Dependencies and Integration Points
Includes HWIF, EQs, WQs, command queue, and QP headers. It bridges the control-plane hardware setup and the actual SQ/RQ data path.

## Risks
DB area sizing assumes a 4 MiB doorbell BAR with 4 KiB slots. `max_qps`, `sq_depth`, and `rq_depth` must match firmware capabilities and QP context encoding. The NIC config mutex protects only cached config state, not queue lifetime.

## Test Signals
Compile coverage, IO init/free, QP create/destroy, WQ page-size command success, DB allocation/return, and PF/VF paths validate this contract.
