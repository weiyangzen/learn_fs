# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.c

Purpose: implements Marvell CESA platform-device probing, engine setup, interrupt-driven request scheduling, and crypto algorithm registration.

Important APIs and functions: global `cesa_dev` exposes the single probed device to algorithm files. `mv_cesa_queue_req()` enqueues async requests and chains TDMA descriptors when needed. `mv_cesa_dequeue_req_locked()`, `mv_cesa_rearm_engine()`, `mv_cesa_std_process()`, `mv_cesa_int_process()`, and `mv_cesa_int()` implement request dispatch and interrupt completion. `mv_cesa_add_algs()`/`remove_algs()` register skcipher and ahash algorithm tables selected by SoC capability data. Probe helpers configure TDMA MBUS windows, DMA pools, SRAM, clocks, IRQs, queue/load state, and engine registers.

Control flow: probe rejects a second CESA device, picks capability tables from OF compatible data, allocates device/engine state, maps registers, creates DMA pools for TDMA-capable SoCs, maps or allocates SRAM per engine, requests threaded IRQs, initializes hardware registers and queues, sets IRQ affinity, stores `cesa_dev`, and registers algorithms. Runtime queueing selects an engine in algorithm code, enqueues the request, rearms idle engines, processes interrupts, completes backlog with `-EINPROGRESS`, and drains a complete queue outside engine ownership.

State and persistence: persistent state includes global `cesa_dev`, per-engine register/SRAM pointers, DMA address, spinlock, current request, crypto queue, atomic load, TDMA chains, complete queue, clocks, IRQ, and optional DMA pools. SRAM may come from a gen_pool or direct ioremap/resource DMA mapping.

Dependencies and integration points: depends on platform/OF bindings, MBUS DRAM info, SRAM gen_pool, DMA pools, Linux crypto async queues, CESA cipher/hash/TDMA modules, and hardware IRQ/status registers.

Risks: only one global device is supported; remove unregisters algorithms and releases SRAM but does not explicitly clear `cesa_dev`, which can affect reprobe assumptions. IRQ handling reads/clears status in a loop and relies on algorithm `process()` returning exact `0`, `-EINPROGRESS`, or error semantics. Error cleanup loops call `mv_cesa_put_sram()` for all engines, including possibly uninitialized ones. Tests should cover OF capability selection, no-SRAM fallback, TDMA and non-TDMA paths, IRQ status masks, backlog completion, engine load balancing, probe failure at each stage, remove/reprobe behavior, and known-answer crypto/hash tests.
