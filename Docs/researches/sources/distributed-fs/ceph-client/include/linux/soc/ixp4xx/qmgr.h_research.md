# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/qmgr.h

Purpose: This header exposes the IXP4xx queue manager API used by NPE-backed networking and other queue-based hardware blocks.

Important APIs/types/functions: It defines queue counts, queue length, status bits, watermarks, IRQ sources, and `struct qmgr_regs`. APIs include `qmgr_put_entry`, `qmgr_get_entry`, queue status helpers, `qmgr_release_queue`, IRQ setup/enable/disable, and `qmgr_request_queue`/`__qmgr_request_queue` with debug owner metadata.

Control flow: Consumers request a queue with length and watermarks, push and pop 32-bit entries, react to configured queue IRQs, and release the queue at teardown.

State and persistence: Queue contents, read/write pointers, status, overflow/underflow flags, and IRQ enables are hardware state. `qmgr_queue_descs` tracks software descriptions when debugging is enabled.

Dependencies and integration: Integrates with IXP4xx NPE drivers, interrupt handling, and platform MMIO mapping.

Risks and test signals: Queue length/watermark mismatch can overflow, underflow, or lose interrupts. Test queue request collisions, empty/full transitions, IRQ source configuration, and high-rate NPE traffic.
