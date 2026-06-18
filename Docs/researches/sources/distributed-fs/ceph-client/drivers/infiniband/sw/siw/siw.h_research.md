# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw.h

Purpose: Defines the central SoftiWARP provider object model for this kernel RDMA driver: device capabilities, PDs, memory registrations, CQs, QPs, RX/TX protocol contexts, SRQs, helper conversions, queue helpers, CRC helpers, and exported cross-file function prototypes. This header is the shared contract tying RDMA core verbs, iWARP wire processing, TCP socket callbacks, memory protection, and completion handling together.

Important APIs/types/functions: `struct siw_device` wraps `ib_device`, device limits, xarrays for QP and memory lookup, CEP/QP lists, and active object counters. `struct siw_qp` owns `ib_qp`, state lock, CEP/socket association, SQ/RQ/ORQ/IRQ queues, RX stream state, TX context, completion queues, SRQ, mmap entries, and lifetime reference state. `struct siw_mem`, `siw_mr`, `siw_umem`, and `siw_pbl` model STag-indexed registered memory. `siw_qp_id2obj()` uses RCU plus `kref_get_unless_zero`; queue helpers inspect user-mapped WQE flags with `READ_ONCE`; CRC helpers wrap crc32c for MPA.

Control flow: Verbs code allocates device, QP, CQ, SRQ, and MR instances matching these structures. CM moves sockets into QP ownership. TX/RX paths consume `siw_iwarp_tx` and `siw_rx_stream` state across partial TCP sends/receives. Completion helpers flush and reap queues through `siw_cq`.

State and persistence behavior: State is entirely in kernel memory and RDMA-core objects, not persistent on disk. Long-lived state is protected by spinlocks, rwsems, xarrays, krefs, atomics, and memory barriers because user queues may be mmaped and touched concurrently.

Dependencies/integration: Depends on RDMA core headers, `rdma/siw-abi.h`, `iwarp.h`, Linux sockets/skbuff, CRC, xarray, RCU, and ibverbs object lifecycles. Integration points are the function prototypes used by `siw_main.c`, `siw_verbs.c`, `siw_cm.c`, `siw_qp*.c`, `siw_mem.c`, and `siw_cq.c`.

Risks: Incorrect queue flag ordering can expose partially written WQEs/CQEs to userspace. Kref/xarray lifetime mistakes can become UAFs in socket callbacks or TX worker paths. STag validation and bounds errors are security-sensitive. Any layout drift must stay ABI-compatible with `siw-abi.h`.

Test signals: Build with lockdep/KASAN/KCSAN, create/destroy QPs/CQs/MRs/SRQs from userspace, exercise mmaped queues, RDMAP SEND/WRITE/READ, CRC on/off, invalid STag/key/bounds paths, QP error/flush paths, and concurrent QP destruction while sockets or TX workers are active.
