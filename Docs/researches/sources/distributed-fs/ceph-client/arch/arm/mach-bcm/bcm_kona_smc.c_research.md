# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.c

Purpose: implements Broadcom Kona secure monitor call support using a small non-cacheable shared buffer.

Important APIs/types/functions: `struct bcm_kona_smc_data`, global `bcm_smc_buffer_phys` and `bcm_smc_buffer`, `bcm_kona_smc_init()`, `bcm_kona_do_smc()`, `__bcm_kona_smc()`, and public `bcm_kona_smc()`.

Control flow: init finds the compatible secure service node, reads its buffer size, allocates coherent memory, and stores physical/virtual addresses. Callers populate the shared buffer with service ID and arguments, execute the monitor call on CPU0 via `on_each_cpu()`/IPI-safe helper, and return the monitor status.

State and persistence: the shared coherent buffer and its physical address persist after init. Calls temporarily store arguments/results in that buffer.

Dependencies and integration: used by Kona L2 cache setup and other mobile Broadcom platform code; depends on DT, DMA coherent allocation, CPU affinity, and secure monitor ABI constants from `bcm_kona_smc.h`.

Risks: secure monitor calls are firmware ABI-sensitive and use global shared state, so concurrent callers would require serialization by higher-level assumptions. Missing init leaves later secure calls unable to communicate.

Test signals: successful `bcm_kona_smc_init()`, secure L2 enable return value `SEC_ROM_RET_OK`, and boot tests on BCM mobile SoCs with OP-TEE/secure ROM present.
