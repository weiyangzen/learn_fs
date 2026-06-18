# sources/distributed-fs/ceph-client/drivers/nvme/host/apple.c

Purpose: Implements the Apple ANS2 NVMe host driver for Apple SoCs. It adapts NVMe core and blk-mq to Apple firmware, RTKit coprocessor boot, SART shared-memory authorization, a single admin queue, a single I/O queue, and an Apple NVMMU tag-control-block model.

Important APIs and flow: Probe allocates platform state, attaches power domains, maps ANS/NVMe MMIO, initializes SART, reset, queues, DMA pools, mempool, tag sets, IRQ, RTKit, and `nvme_ctrl`, then schedules reset. Request flow uses `apple_nvme_queue_rq()`, `nvme_setup_cmd()`, PRP setup for simple or scatter-gather DMA, request start, and hardware-specific submit functions. Completion flow polls CQ phase bits, invalidates NVMMU TCBs, finds blk-mq requests by tag, and batches completions. Reset work boots or wakes RTKit, configures NVMMU/linear submission queues, enables the NVMe controller, creates I/O queues, updates queue counts, and starts the controller. Disable handles freeze/quiesce, queue deletion, controller disable, CQ draining, and request cancellation.

State and persistence behavior: Runtime state includes `struct apple_nvme`, queue memory, TCB arrays, tag sets, DMA pools, RTKit/SART handles, power-domain links, IRQ, and controller state. No persistent media metadata is modified beyond normal NVMe commands issued by upper layers.

Dependencies and integration points: Depends on NVMe core, blk-mq, Apple RTKit, Apple SART, reset framework, OF platform matching, power domains, DMA mapping/pools, mempools, IRQ handling, and PM sleep operations.

Risks and test signals: Hardware-specific ordering is delicate: tags are shared across queues on LSQ/NVMMU hardware, interrupts can be missed without the submission lock, abort is unsupported so timeouts reset the controller, and RTKit crashes are unrecoverable without reboot. Tests should cover probe deferral, reset/suspend/resume, request timeout polling, PRP list allocation/free, DMA mapping failures, queue disable races, power-domain cleanup, T8015 versus T8103 paths, and namespace teardown after reset failure.
