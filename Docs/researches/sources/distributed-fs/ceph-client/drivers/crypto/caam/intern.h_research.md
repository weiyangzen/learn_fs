<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h

Purpose: shared private header for CAAM backend modules, defining job-ring/controller private structures, queue sizing, optional algorithm-registration hooks, PM save state, and DMA mask selection.

Important APIs and control flow: defines `JOBR_DEPTH`, interrupt coalescing constants, `CRYPTO_ENGINE_MAX_QLEN`, `struct caam_jrentry_info`, JR state/dequeue params/private data, controller save state, and `struct caam_drv_private` with controller register bases, capability flags, clocks, debugfs state, RNG handle state, and PM state. Provides Kconfig-guarded prototypes or no-op stubs for symmetric/hash/PKC/RNG/PRNG/QI algorithm registration. `caam_get_dma_mask()` chooses 32-, 36-, 40-, or 49-bit masks from `caam_ptr_sz`, `caam_dpaa2`, and compatible strings.

State and persistence behavior: structures here are the main long-lived driver state allocated by `ctrl.c` and `jr.c`. The header itself owns no state but fixes cross-module layout and expectations.

Dependencies and integration points: included by controller, JR, RNG/PRNG, debugfs, error-adjacent code, and algorithm modules. It bridges platform probing, crypto-engine queueing, PM, debugfs, and optional Kconfig APIs.

Risks and test signals: risks include global assumptions embedded in `caam_get_dma_mask()`, `JOBR_DEPTH` needing to remain a power of two for circular macros, stubbed algorithm init hiding disabled features, and structure layout changes affecting many modules. Test signals include successful builds for all Kconfig permutations, correct JR ring wrap behavior, DMA mask matching hardware pointer mode, PM save/restore on supported SoCs, and registration/unregistration balance with multiple JRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h -->
