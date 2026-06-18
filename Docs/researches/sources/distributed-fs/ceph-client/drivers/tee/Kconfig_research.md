# sources/distributed-fs/ceph-client/drivers/tee/Kconfig

## Purpose
Defines the top-level Kconfig menu for generic Trusted Execution Environment support and includes provider-specific TEE backends.

## Important APIs, Types, and Constants
`menuconfig TEE` is a tristate depending on `HAVE_ARM_SMCCC || COMPILE_TEST || CPU_SUP_AMD` and selects `CRYPTO_LIB_SHA1`, `DMA_SHARED_BUFFER`, and `GENERIC_ALLOCATOR`. `TEE_DMABUF_HEAPS` is a bool enabled by default when TEE, DMA, and dmabuf heaps are available. The file sources OP-TEE, AMDTEE, ARM TSTEE, and QCOMTEE Kconfig files.

## Control Flow and State
No runtime flow. Build configuration decides whether the generic TEE core and backend drivers are built in, modular, or omitted.

## Dependencies and Integration Points
Integrates TEE core configuration with architecture SMCCC support, AMD CPU support, shared DMA buffers, crypto SHA1, generic allocator, and provider subdirectories.

## Risks and Test Signals
Dependency changes affect which platforms can even see TEE support. `TEE_DMABUF_HEAPS` defaults on only when heap infrastructure exists. Test signals are Kconfig coverage for ARM, AMD, and COMPILE_TEST builds, plus correct provider menu visibility under `TEE`.
