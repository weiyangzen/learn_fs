# sources/distributed-fs/ceph-client/drivers/crypto/caam/Kconfig

Purpose: Kconfig menu for Freescale/NXP CAAM crypto drivers. It controls the main CAAM controller backend, job-ring backend, Crypto API registrations, QI/DPAA2 variants, public-key/RNG/PRNG/blob-generation support, debug output, and job-ring interrupt coalescing settings.

Important symbols: `CRYPTO_DEV_FSL_CAAM_COMMON`, `CRYPTO_DEV_FSL_CAAM_CRYPTO_API_DESC`, and `CRYPTO_DEV_FSL_CAAM_AHASH_API_DESC` are shared descriptor/common libraries; `CRYPTO_DEV_FSL_CAAM` enables the platform controller; `CRYPTO_DEV_FSL_CAAM_JR` enables job rings; `CRYPTO_DEV_FSL_CAAM_CRYPTO_API`, `_QI`, `_AHASH_API`, `_PKC_API`, `_RNG_API`, `_PRNG_API`, `_BLOB_GEN`, and `_RNG_TEST` select feature modules; `CRYPTO_DEV_FSL_DPAA2_CAAM` enables DPAA2 DPSECI support.

Control flow: build configuration gates which objects the Makefile links and which algorithms later register with the Crypto API. Nested `if` blocks require the CAAM controller and job-ring backend before most service APIs can be enabled.

State and persistence: no runtime state; persistent effect is kernel build configuration.

Dependencies and integration points: depends on SoC architecture symbols, `FSL_MC_DPIO`, `NETDEVICES`, `FSL_DPAA`, Crypto API symbols, hwrng, and job-ring/crypto-engine infrastructure.

Risks: defaults enable many APIs when CAAM/JR are selected; QI needs DPAA and NET; interrupt coalescing thresholds can force timeouts if set at or above ring size; blob generation is a silent bool selected by other users rather than a user-visible menu.

Test signals: configuration matrix builds for platform CAAM, JR-only APIs, QI, DPAA2, COMPILE_TEST, and RNG test; verify selected crypto dependencies and produced modules.
