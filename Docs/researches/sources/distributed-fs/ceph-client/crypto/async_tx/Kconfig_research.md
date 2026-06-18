# sources/distributed-fs/ceph-client/crypto/async_tx/Kconfig

Purpose: defines async_tx feature configuration for asynchronous memory copy, XOR, RAID6 P/Q syndrome generation, RAID6 recovery, and optional DMA validation-disable switches.

Important APIs/types/functions: `ASYNC_CORE` provides core async transaction support. `ASYNC_MEMCPY`, `ASYNC_XOR`, `ASYNC_PQ`, and `ASYNC_RAID6_RECOV` select the core and related primitives. `ASYNC_TX_DISABLE_PQ_VAL_DMA` and `ASYNC_TX_DISABLE_XOR_VAL_DMA` disable validation DMA paths.

Control flow: selected configs determine which async_tx objects are built and which RAID paths can use DMA offload versus synchronous fallback.

State and persistence: no runtime state; configuration persists in the built kernel.

Dependencies and integration points: integrated by async_tx Makefile, DMA engine support, RAID5/6 code, XOR blocks, and PQ helpers.

Risks: selecting high-level recovery without required lower-level primitives would break builds, so dependencies are expressed through `select`. Disabling DMA validation changes performance and exercised code paths.

Test signals: build configs for each async primitive alone and combined, DMA engine enabled/disabled, and RAID6 recovery with validation DMA switches.
