# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.h

Purpose: Declares HNS RoCE HEM table/list types, HEM type identifiers, hop-count classification macros, and public HEM APIs.

Important APIs/types/functions: HEM types identify mapped context tables (`QPC`, `MTPT`, `CQC`, `SRQC`, `SCCC`, timers, `GMV`) and unmapped address/resource tables (`MTT`, `CQE`, `SRQWQE`, `IDX`, `IRRL`, `TRRL`). `struct hns_roce_hem` holds a coherent buffer, DMA address, size, and refcount. `struct hns_roce_hem_mhop` carries cap-derived hop configuration and calculated indexes. Macros classify whether a type/hop combination needs one, two, or three BA table chunks.

Control flow: Callers initialize HEM tables during device setup, get/put table chunks during object creation/destruction, find CPU/DMA addresses for existing entries, and use HEM lists to build MTR root/middle/bottom BA chains.

State and persistence: This header defines the in-memory shape for refcounted HEM chunks and multi-hop index calculation, but state is stored in `hns_roce_hem_table` from `hns_roce_device.h` and list structs embedded in MTRs.

Dependencies and integration: Consumed by CQ, MR, QP, SRQ, EQ, and main teardown code. It relies on device caps and `HNS_ROCE_HOP_NUM_0` constants from `hns_roce_device.h`.

Risks: Type ordering matters because macros treat values below `HEM_TYPE_MTT` as mapped context HEM and values at/above it as unmapped buffer/address tables. Reordering or adding types without updating the classification logic is risky. Test signals include compile coverage for all HEM users, cap combinations for hop 0/1/2/3, and cleanup coverage for every type.
