# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-crypto.c

## Purpose
`zynqmp-crypto.c` exports firmware-call wrappers for Xilinx/AMD secure crypto services. It lets kernel crypto/security clients invoke AES-GCM, SHA, platform-feature discovery, and Versal AES key/operation APIs through the ZynqMP firmware invocation layer.

## Important APIs and functions
`zynqmp_pm_aes_engine()` invokes `PM_SECURE_AES` with a physical address to an AES parameter structure and returns a firmware output word through `out`. `zynqmp_pm_sha_hash()` invokes `PM_SECURE_SHA` with address, size, and flags controlling init/update/final behavior. `xlnx_get_crypto_dev_data()` reads the platform family code, scans a caller-provided `struct xlnx_feature` table, checks feature availability with `zynqmp_pm_feature()`, and returns feature-specific data or an error pointer.

The Versal AES wrappers call XSecure API ids through the same `zynqmp_pm_invoke_fn()` transport: key write/zero, operation init, AAD update, encrypt update/final, decrypt update/final, and AES block init. All exported functions use `EXPORT_SYMBOL_GPL`.

## Control flow and integration
Each function is intentionally thin: validate required output pointer where applicable, split 64-bit addresses into lower/upper 32-bit arguments in the order required by the firmware API, invoke the PM function id, and return the firmware-layer status. The feature discovery helper adds a small table scan and returns `ERR_PTR()` on firmware or matching failure.

## State and persistence behavior
This file stores no driver-private state. Persistent crypto state, volatile keys, AES operation context, SHA engine state, and feature information are owned by firmware/hardware. Callers must provide DMA-safe buffers and manage operation sequencing.

## Dependencies and integration points
The file depends on `linux/firmware/xlnx-zynqmp.h` for API ids, `PAYLOAD_ARG_CNT`, feature structures, and `zynqmp_pm_invoke_fn()`. It integrates with downstream crypto drivers that need firmware-mediated secure operations and with platform-family/feature detection for selecting implementation data.

## Risks and test signals
Risks center on address argument ordering, DMA/cache coherency expectations, invalid caller buffers, firmware API availability by platform family, and minimal local validation. `zynqmp_pm_aes_engine()` writes `*out` even if the firmware call fails, so callers must check the return code before trusting it. Test signals include exported symbol resolution, secure AES/SHA known-answer tests, feature-table selection on each supported family, and negative tests for absent firmware features and null output pointers.
