# sources/distributed-fs/ceph-client/arch/s390/include/asm/qdio.h

Purpose: This header defines the public s390 QDIO queue layout and driver API used by high-speed channel I/O devices such as qeth, zfcp, and IQDIO.

Important APIs/types/functions: It defines queue limits, qfmt constants, packed/aligned hardware structures (`qdesfmt0`, `qdr`, `qib`, `slibe`, `qaob`, `slib`, `qdio_buffer_element`, `qdio_buffer`, `sl`, `slsb`, `qdio_ssqd_desc`), SBAL/QIB/CHSC flags, `qdio_handler_t`, error flags, cleanup flags, `struct qdio_initialize`, buffer allocation helpers, and lifecycle APIs from `qdio_allocate()` through `qdio_free()` plus queue inspect/add operations and SSQD query.

Control flow: Drivers allocate SBAL buffers, fill `qdio_initialize`, establish queues on a CCW device, activate/start IRQ processing, add buffers to input or output queues, receive callbacks with processed ranges/errors, inspect queues, and shut down/free queues during device removal.

State and persistence: Persistent state is allocated QDIO queue memory, QDR/QIB/SLIB/SL/SLSB/SBAL/QAOB hardware-visible blocks, handler pointers, interruption parameter, and device queue activation state.

Dependencies and integration points: It depends on Linux interrupts, s390 DMA types, CCW devices, CIO definitions, and channel subsystem CHSC/QEBSM capabilities.

Risks and test signals: Packed alignment and buffer counts are hardware contracts; callback ranges and SLSB states must be handled correctly to avoid data loss. Tests should cover qeth/zfcp/IQDIO devices, multi-queue setup, input/output buffer recycling, async QAOB completions, QEBSM/data-div flags, shutdown via halt/clear, and error callbacks.
