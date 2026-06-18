<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c

Purpose: CAAM Job Ring backend driver. It probes hardware JRs, manages DMA input/output rings, enqueues descriptors, services completions, owns JR allocation among clients, and registers CAAM crypto/RNG algorithms when the first JR becomes active.

Important APIs and control flow: `caam_jr_probe()` maps JR registers, sets DMA mask, starts a crypto engine, maps IRQ, initializes rings, adds the JR to the global list, and calls `register_algs()`. `caam_jr_enqueue()` maps the descriptor, reserves an input slot under `inplock`, records callback metadata, writes descriptor DMA address to the input ring, uses a full `wmb()`, updates head and hardware job-add, and returns `-EINPROGRESS`. IRQ handling masks interrupts, acknowledges status, and schedules `caam_jr_dequeue()` tasklet, which matches output descriptors to software entries, unmaps descriptors, advances tail across out-of-order completions, removes output entries, and invokes callbacks. PM paths remove/add JRs from allocation list, flush or restart hardware, save ring DMA addresses, and reinitialize hwrng.

State and persistence behavior: global `driver_data.jr_list` and `active_devs` coordinate JR allocation and one-time algorithm registration. Per-JR state includes coherent rings, entry metadata, head/tail indices, input availability, tasklet, IRQ, crypto engine, tfm reference count, and PM ring addresses.

Dependencies and integration points: integrates with OF JR child nodes, crypto-engine, tasklets/IRQs, DMA mapping, controller private data, algorithm modules, hwrng/PRNG, QI algapi, and `jr.h` exported APIs used by all JR-backed operations.

Risks and test signals: risks include `BUG()` on JR hardware errors or unmatched completions, no enqueue retry in callers unless implemented above, tasklet-era interrupt handling, busy remove when `tfm_count` is nonzero, strict ring depth power-of-two assumptions, and subtle memory ordering around CAAM reads. Test signals include descriptor completion under load, out-of-order completion matching, `-ENOSPC` behavior at full ring, suspend/resume with in-flight jobs flushed, one-time algorithm registration across multiple JRs, and no DMA leaks on enqueue/dequeue failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c -->
