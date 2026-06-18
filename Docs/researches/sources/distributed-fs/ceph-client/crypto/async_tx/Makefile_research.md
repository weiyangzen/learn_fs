# sources/distributed-fs/ceph-client/crypto/async_tx/Makefile

Purpose: maps async_tx Kconfig symbols to the corresponding kernel objects.

Important APIs/types/functions: builds `async_tx.o`, `async_memcpy.o`, `async_xor.o`, `async_pq.o`, `async_raid6_recov.o`, and optionally `raid6test.o` based on config symbols.

Control flow: kbuild includes each object only when its config is enabled, allowing minimal kernels to omit unused async transaction helpers.

State and persistence: no runtime state. Build outputs are controlled by kbuild.

Dependencies and integration points: tied to `crypto/async_tx/Kconfig` and RAID/DMA consumers that call exported async_tx APIs.

Risks: object selection must track exported API dependencies; missing objects cause unresolved symbols for RAID code.

Test signals: parallel builds across all config combinations and module/built-in variants.
