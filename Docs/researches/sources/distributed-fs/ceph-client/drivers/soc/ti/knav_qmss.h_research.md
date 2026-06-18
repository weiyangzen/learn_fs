# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss.h

## Purpose
This internal header defines the shared data model, register layouts, constants, range operation hooks, and helper macros used by the Keystone Navigator QMSS queue and accumulator drivers.

## Important APIs, Types, And Functions
It defines accumulator command/status constants, descriptor pointer masks, queue/pool/region constants, PDSP control bits, and `RANGE_*` flags. Major structs include `knav_reg_config`, `knav_reg_region`, `knav_reg_pdsp_regs`, `knav_reg_acc_command`, `knav_link_ram_block`, `knav_acc_info`, `knav_acc_channel`, `knav_pdsp_info`, `knav_qmgr_info`, `knav_queue_stats`, `knav_reg_queue`, `knav_region`, `knav_pool`, `knav_queue_inst`, `knav_queue`, `knav_device`, `knav_range_ops`, `knav_irq_info`, and `knav_range_info`. It declares `knav_init_acc_range` and `knav_queue_notify`.

## Control Flow
The header itself has no runtime control flow, but its operation table drives queue-range behavior: generic queue ranges and accumulator-backed ranges supply init/open/close/notify/free callbacks used by `knav_qmss_queue.c`.

## State And Persistence
The structs model persistent driver state for descriptor regions, queues, pools, accumulator lists, PDSP firmware state, queue manager MMIO windows, and per-handle stats. Hardware state is represented by mapped register structs and queue descriptors.

## Dependencies And Integration Points
It includes percpu support and depends on external public Keystone types from `linux/soc/ti/knav_qmss.h` through the C files. It binds the queue and accumulator source files together and should remain private to the driver implementation.

## Risks And Test Signals
Risks are ABI drift between this private model and public client headers, descriptor mask assumptions, fixed accumulator channel/list limits, and packed hardware field assumptions. Test signals are successful builds of both QMSS source files, correct struct field use under sparse/build checks, and runtime queue/accumulator behavior.
