# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.h

Purpose: expected receive/TID helper header. It defines TID field encoders, KDETH header field accessors, TID group data structures, list operations, write-combining receive-array fill helper, TID creation helper, and group index conversion APIs.

Important APIs/types: `struct tid_group` stores a list node, base receive entry, size, used count, and map. `EXP_TID_GET/SET/CLEAR/RESET` manipulate expected TID descriptor fields. `KDETH_GET/SET/RESET` manipulate little-endian KDETH dwords. `rcv_array_wc_fill()`, `tid_group_add_tail()`, `tid_group_remove()`, `tid_group_move()`, `tid_group_pop()`, `create_tid()`, `hfi1_tid_group_to_idx()`, and `hfi1_idx_to_tid_group()` are inline helpers. Prototypes mirror the implementation in `exp_rcv.c`.

Control flow: TID management code initializes lists, pops free groups, moves them between free/used/full sets as registrations consume entries, creates encoded TID values from receive-array indexes and page counts, updates KDETH templates, and optionally writes zero fills to the write-combined RcvArray mapping.

State and persistence: TID descriptor values are hardware-facing state. `struct tid_group` instances persist per receive context in `rcd->groups`; `exp_tid_set.count` mirrors each list. Write-combined RcvArray fills affect device-visible receive table memory and flush every fourth entry.

Dependencies and integration: includes `hfi.h` for core context/device structures and uses Linux list, endian, writeq, and WC flush primitives through that include chain. It is consumed by TID RDMA and expected receive code.

Risks: bitfield encoders must match hardware and KDETH ABI exactly. `tid_group_pop()` assumes the set is non-empty; callers must check `EXP_TID_SET_EMPTY()` or equivalent. `rcv_array_wc_fill()` only flushes on indexes where `(index & 3) == 3`, so callers ending on other indexes need a final flush elsewhere if ordering matters. Pointer arithmetic in group/index conversion assumes `grp` belongs to `rcd->groups`.

Test signals: TID encode/decode round trips, KDETH field mutation tests, registration stress with group moves, empty-set guard tests, WC fill ordering on real hardware, and teardown clearing expected receive entries.
