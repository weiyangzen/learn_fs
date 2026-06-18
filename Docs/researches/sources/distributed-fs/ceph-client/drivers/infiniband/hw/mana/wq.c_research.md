# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wq.c

## Purpose
`wq.c` implements receive work queue and RWQ indirection-table operations used mainly for MANA raw-packet RSS QPs.

## Important APIs, Types, And Functions
`mana_ib_create_wq()` reads userspace WQ buffer attributes, allocates `struct mana_ib_wq`, creates a user queue DMA region, stores max WR and buffer size, and initializes `rx_object` invalid. `mana_ib_modify_wq()` returns `-EOPNOTSUPP`. `mana_ib_destroy_wq()` destroys the queue and frees the wrapper. `mana_ib_create_rwq_ind_table()` and `mana_ib_destroy_rwq_ind_table()` are no-op wrappers because the driver stores no extra indirection-table state.

## Control Flow
Creation validates/copies udata, allocates the WQ, creates a queue over `ucmd.wq_buf_addr`/`wq_buf_size`, and returns the embedded `ib_wq`. Destroy reverses queue creation. RSS QP creation later consumes these WQs to create MANA RQ objects and configure vport steering.

## State And Persistence
Each WQ stores a `mana_ib_queue`, max WQE count, userspace buffer size, and firmware RX object handle once RSS setup creates it. State is runtime-only.

## Dependencies And Integration Points
The file depends on MANA userspace ABI structures, RDMA WQ/RWQ APIs, queue helpers in `main.c`, and RSS setup/destruction in `qp.c`.

## Risks
No kernel WQ creation path exists; `udata` is assumed valid. Modify WQ is unsupported, so userspace must create new WQs for changes. RWQ indirection-table no-ops rely on RDMA core owning the table contents and `qp.c` consuming them directly.

## Test Signals
Test udata validation, queue creation failure, WQ destroy before and after RSS object creation, modify rejection, indirection table create/destroy, and invalid userspace buffer sizes.
