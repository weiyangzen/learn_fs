# sources/distributed-fs/ceph-client/drivers/tee/optee/Kconfig

## Purpose
`Kconfig` defines OP-TEE driver build options: the main OP-TEE TEE driver, an optional insecure firmware image loading mode, and a static protected-memory pool helper option.

## Important APIs, Types, And Functions
`config OPTEE` is a tristate depending on `HAVE_ARM_SMCCC`, `MMU`, and a satisfiable `RPMB || !RPMB` expression. It enables the OP-TEE Trusted Execution Environment driver. `config OPTEE_INSECURE_LOAD_IMAGE` is an ARM64-only boolean behind `OPTEE` that loads `optee/tee.bin` as firmware during probe. `config OPTEE_STATIC_PROTMEM_POOL` is an internal bool defaulting to yes when `HAS_IOMEM` and `TEE_DMABUF_HEAPS` are enabled.

## Control Flow And State
These symbols control compile-time inclusion and code paths. `OPTEE_INSECURE_LOAD_IMAGE` activates firmware loading support in `smc_abi.c`. `OPTEE_STATIC_PROTMEM_POOL` enables static protected-memory pool setup in the same backend. `OPTEE` controls the module/object build through the Makefile.

## Dependencies And Integration Points
The options integrate with ARM SMCCC, MMU, RPMB availability, arm64 firmware loading, I/O memory mapping, and TEE DMA-BUF heap support. The warning text points readers to OP-TEE and Trusted Firmware-A threat documentation because image loading from the kernel materially changes the trust model.

## Risks
The insecure image loading option is explicitly dangerous: loading BL32 from filesystem firmware makes kernel/rootfs integrity part of the secure-world boot path. Build coverage for protected memory depends on a default-y internal symbol, so platforms without `HAS_IOMEM` or `TEE_DMABUF_HEAPS` silently lose that path.

## Test Signals
Validate builds with OP-TEE as built-in, module, and disabled. Build ARM64 with and without `OPTEE_INSECURE_LOAD_IMAGE`. Confirm protected-memory code is compiled only when expected and that RPMB-disabled configurations still allow OP-TEE to build.
