# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_pd.c

## Purpose
`hns_roce_pd.c` manages simple ID-backed protection domains, user access regions, and XRC domains for HNS RoCE. It provides the RDMA-core PD/XRCD verbs callbacks and initializes the per-device IDA ranges used by those objects.

## Important APIs, Types, And Functions
The main exported functions are `hns_roce_init_pd_table()`, `hns_roce_alloc_pd()`, `hns_roce_dealloc_pd()`, `hns_roce_uar_alloc()`, `hns_roce_init_uar_table()`, `hns_roce_init_xrcd_table()`, `hns_roce_alloc_xrcd()`, and `hns_roce_dealloc_xrcd()`. It manipulates `struct hns_roce_ida`, `struct hns_roce_pd`, `struct hns_roce_uar`, and `struct hns_roce_xrcd`.

## Control Flow
Table initialization sets IDA ranges from capability limits and reserved counts. PD allocation obtains an ID from the PD IDA, stores it in `pdn`, and returns the PD number to userspace when udata is present. PD deallocation returns the ID to the IDA. UAR allocation obtains a logical index, maps it to a physical UAR index modulo available physical UARs, sets the BAR2 page frame number for doorbells, and records the direct-WQE BAR4 base when supported. XRCD allocation checks the XRC capability flag before allocating an XRC domain number; deallocation frees the ID.

## State And Persistence
All state is volatile IDA allocation state plus object fields (`pdn`, `logic_idx`, `index`, `pfn`, `xrcdn`). UAR physical mapping is derived from PCI BAR addresses and capability flags at allocation time. No hardware context is created here and there is no nonvolatile persistence.

## Dependencies And Integration Points
This file is called by `hns_roce_main.c` during HCA setup and through the registered `ib_device_ops`. UAR allocation is consumed by user-context setup and kernel doorbell paths. PD numbers are embedded in MR, AH, QP, and SRQ hardware contexts. XRCDs are only exposed when `HNS_ROCE_CAP_FLAG_XRC` is enabled.

## Risks
Negative IDA allocation results are collapsed to `-ENOMEM`, losing exhaustion versus interruption detail. `hns_roce_uar_alloc()` sets `hr_dev->dwqe_page` as a device-wide side effect on every allocation when direct WQE is supported. UAR cleanup is done by callers using raw `ida_free()`, so the logical index must remain valid through all failure paths. PD userspace response failure frees the ID but leaves no additional object state to clear.

## Test Signals
Test PD allocation/deallocation across reserved ranges, userspace response copy failure, PD ID exhaustion, UAR physical index mapping with one and many physical UARs, direct-WQE BAR address selection, XRCD allocation when capability is absent/present, XRCD ID exhaustion, and repeated init/destroy cycles for IDA state.
