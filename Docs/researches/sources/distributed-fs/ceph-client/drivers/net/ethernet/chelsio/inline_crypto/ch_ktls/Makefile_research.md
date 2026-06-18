# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/Makefile

## Purpose
Builds the Chelsio kernel TLS device-offload module from `chcr_ktls.o` with access to cxgb4 headers.

## Important APIs, Types, And Functions
The Makefile sets `ccflags-y` to include `drivers/net/ethernet/chelsio/cxgb4`, maps `CONFIG_CHELSIO_TLS_DEVICE` to `ch_ktls.o`, and sets `ch_ktls-objs := chcr_ktls.o`.

## Control Flow
Kbuild compiles and links the kTLS offload object when `CONFIG_CHELSIO_TLS_DEVICE` is enabled as built-in or module. There is no runtime logic.

## State And Persistence
State is limited to build artifacts. The file persists the module name and dependency on cxgb4 internal headers.

## Dependencies And Integration Points
It is reached from `inline_crypto/Makefile` and complements `inline_crypto/Kconfig`, whose `CHELSIO_TLS_DEVICE` symbol depends on TLS/TLS_DEVICE and selects AES crypto library support. Runtime integration is implemented in `chcr_ktls.c`, while `chcr_common.h` supplies shared helper definitions.

## Risks
The object mapping must stay aligned with the actual implementation file and Kconfig help text. Missing include paths would break access to cxgb4 queue and adapter structures used by kTLS offload.

## Test Signals
Building with `CONFIG_CHELSIO_TLS_DEVICE=m` should produce `ch_ktls.ko`; built-in mode should link without unresolved cxgb4/TLS symbols.
