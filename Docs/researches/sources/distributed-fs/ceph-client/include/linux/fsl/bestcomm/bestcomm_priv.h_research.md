# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/bestcomm_priv.h

Purpose: defines the private BestComm engine/task internals used by the engine driver and intermediate task wrappers: SRAM zones, task descriptor tables, task image format, descriptor bitfields, pragmas, initiator IDs/priorities, low-level task allocation/loading, and register helpers.

Important APIs and types: constants size SRAM regions for task contexts, variables, increments, FDTs, and task descriptors. `struct bcom_tdt` mirrors a hardware task descriptor table entry. `struct bcom_engine` stores OF node, SDMA registers, register base, TDT/context/variable/FDT pointers, and lock. `struct bcom_task_header` describes task images with `BCOM_TASK_MAGIC`. Many `BCOM_PRAGMA_*`, `BCOM_INITIATOR_*`, and `BCOM_IPR_*` constants encode hardware scheduling and bus behavior. Private functions include `bcom_task_alloc()`, `bcom_task_free()`, `bcom_load_image()`, and `bcom_set_initiator()`. Inline helpers control prefetch, task enable/disable, descriptor/variable access, descriptor classification, initiator rewriting, task pragmas, auto-start, and TCR initiator fields.

Control flow: engine setup maps registers and allocates SRAM-backed tables. Task wrappers allocate a task, load a task image into SRAM, adjust initiators/pragmas, and program task control registers. Runtime helpers directly read/write big-endian SDMA registers and convert SRAM physical addresses back to virtual pointers.

State and persistence: state is hardware task programming and SRAM-resident descriptor/context tables. It is volatile and platform-specific, but mistakes can corrupt DMA execution across devices.

Dependencies and integration points: depends on PowerPC I/O helpers, MPC52xx SDMA register definitions, OF nodes, BestComm SRAM allocator, and public `bestcomm.h`. It is intentionally not for ordinary device drivers.

Risks and test signals: risks include SRAM layout misalignment, wrong task image sizes, incorrect initiator/priorities, one-way prefetch disable side effects, endian register access errors, and invalid descriptor rewriting. Tests should cover engine probe/remove, task load validation, every task wrapper, hardware IRQ/error handling, original MPC5200 ATA prefetch erratum, and suspend/resume if supported.
