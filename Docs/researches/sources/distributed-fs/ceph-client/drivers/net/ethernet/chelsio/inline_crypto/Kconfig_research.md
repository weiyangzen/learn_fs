# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Kconfig

## Purpose
Defines Kconfig switches for Chelsio inline crypto support under the Chelsio T4 driver family. It gates the inline TLS TOE driver, IPsec XFRM TX crypto offload, and kernel TLS device offload subdrivers.

## Important APIs, Types, And Functions
The public build symbols are `CHELSIO_INLINE_CRYPTO`, `CRYPTO_DEV_CHELSIO_TLS`, `CHELSIO_IPSEC_INLINE`, and `CHELSIO_TLS_DEVICE`. Their dependencies encode required kernel subsystems: `CHELSIO_T4`, `TLS`, `TLS_TOE`, `XFRM_OFFLOAD`, `INET_ESP_OFFLOAD || INET6_ESP_OFFLOAD`, and `TLS_DEVICE`. `CHELSIO_TLS_DEVICE` selects `CRYPTO_LIB_AES`.

## Control Flow
The file is declarative. When `CHELSIO_INLINE_CRYPTO` is enabled, the nested symbols become visible. The selected tristate values drive Makefile recursion into `chtls/`, `ch_ipsec/`, and `ch_ktls/`.

## State And Persistence
Kconfig state is persisted in the kernel build configuration (`.config`) and determines whether code is built-in, modular, or omitted. It has no runtime state.

## Dependencies And Integration Points
The parent Chelsio Kconfig sources this file from `drivers/net/ethernet/chelsio/Kconfig`. The symbols are consumed by `inline_crypto/Makefile` and the subdirectory Makefiles. Runtime integration is with cxgb4 ULD registration, xfrmdev operations, TLS TOE, and TLS device offload.

## Risks
Dependency mistakes can expose drivers without required kernel interfaces or hide valid combinations. The top-level `CHELSIO_INLINE_CRYPTO` is `bool` and defaults to yes when `CHELSIO_T4` is enabled, so downstream tristates still control actual module builds. Feature naming overlaps TLS TOE (`chtls`) and kernel TLS device (`ch_ktls`), making config/test matrices easy to confuse.

## Test Signals
Kernel config tests should cover disabled inline crypto, each subdriver as module, and built-in combinations. Build signals include correct object recursion and absence of missing symbol errors for TLS/XFRM/AES dependencies.
