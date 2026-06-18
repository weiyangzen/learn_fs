# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mana_ib.h

## Purpose
`mana_ib.h` is the central private header for the MANA RDMA driver. It defines driver object wrappers, firmware command structures, queue types, CQE/WQE wire formats, helper functions, constants, and cross-file prototypes.

## Important APIs, Types, And Functions
Key driver objects include `mana_ib_dev`, `mana_ib_pd`, `mana_ib_ucontext`, `mana_ib_queue`, `mana_ib_cq`, `mana_ib_qp`, `mana_ib_wq`, `mana_ib_mr`, `mana_ib_mw`, `mana_ib_dm`, and `mana_ib_ah`. Capability and firmware ABI types include `mana_ib_adapter_caps`, RNIC create/destroy/config requests, CQ/QP create/destroy requests, `mana_rnic_set_qp_state_req`, `mana_rdma_cqe`, and counter responses. Helpers include `mdev_to_gc()`, `mana_get_qp_ref()`, `mana_put_qp_ref()`, `mana_ib_is_rnic()`, `mana_ib_get_netdev()`, and `copy_in_reverse()`.

## Control Flow
The header has no standalone runtime flow, but it defines the contracts followed by every MANA source file. QP lookup uses an xarray keyed by queue ID and `MANA_SENDQ_MASK` for send queues; successful lookup increments a refcount and release completes a `free` completion when the last reference drops.

## State And Persistence
The header describes all runtime state: adapter handle, EQ arrays, QP xarray, AV pool, netdevice notifier, PD vport use count, queue memory/region IDs, firmware handles, shadow queues, and command payloads. None of this is persistent across driver unload; firmware resources are reference-counted through handles and command lifetimes.

## Dependencies And Integration Points
It includes RDMA verbs, MAD, iterator, MANA userspace ABI, uverbs ioctl, DMA pool, MANA net core, `shadow_queue.h`, and `counters.h`. Its prototypes connect build units listed in the Makefile and define the firmware ABI shared by `main.c`, `mr.c`, `qp.c`, `cq.c`, `wr.c`, and `device.c`.

## Risks
Firmware command structures marked as hardware data require stable layout, natural alignment, and endianness expectations; casual refactoring can break the ABI. The header includes `counters.h` while `counters.h` includes this header, so new declarations must avoid circular type requirements. `mana_ib_get_netdev()` returns raw pointers from the MANA context without taking references. `copy_in_reverse()` is used in address commands and AH creation; misuse can silently invert protocol addresses.

## Test Signals
Compile with sparse/struct layout checks where available, exercise QP xarray refcounting under concurrent completions and destroy, verify firmware command sizes against expected ABI, check RNIC-vs-Ethernet mode helpers, and run create/destroy cycles for every object wrapper.
