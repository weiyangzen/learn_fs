# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the HiSilicon crypto accelerator family: SEC, SEC2, the shared QM queue-manager module, ZIP, HPRE, and TRNG. It is the dependency and feature-selection gate that decides which driver subdirectories and shared objects become buildable.

## Important APIs, Types, and Functions
This is declarative Kconfig, so the important symbols are `CRYPTO_DEV_HISI_SEC`, `CRYPTO_DEV_HISI_SEC2`, `CRYPTO_DEV_HISI_QM`, `CRYPTO_DEV_HISI_ZIP`, `CRYPTO_DEV_HISI_HPRE`, and `CRYPTO_DEV_HISI_TRNG`. HPRE selects `CRYPTO_DEV_HISI_QM`, `CRYPTO_DH`, `CRYPTO_RSA`, and `CRYPTO_ECDH`; SEC2 selects QM plus skcipher, AEAD, authenc, HMAC, hash, and SM4 support.

## Control Flow
There is no runtime control flow. At configuration time, selecting a public accelerator symbol pulls in the crypto algorithms and shared dependencies it needs. Hidden symbol `CRYPTO_DEV_HISI_QM` is selected by users such as SEC2, ZIP, and HPRE instead of being directly user-facing.

## State and Persistence Behavior
The file persists build configuration state through kernel `.config` symbols. It does not create runtime state. Tristate choices determine whether drivers are built-in, modules, or absent.

## Dependencies and Integration Points
The symbols constrain builds to ARM64 or compile-test cases, PCI MSI where PCI queue-manager devices are used, ACPI for modern HiSilicon PCI accelerators, and optional UACCE compatibility through `depends on UACCE || UACCE=n`. The Makefile in the same directory consumes these symbols to include subdirectories and objects.

## Risks and Edge Cases
Misconfigured dependencies here can produce build failures or runtime-inaccessible hardware support. The `UACCE || UACCE=n` pattern prevents incompatible modular combinations and should remain aligned with the queue-manager implementation. HPRE help text mentions RSA and DH but the driver also registers ECDH when supported, so user-facing text may lag actual functionality.

## Test Signals
Build matrix signals are `allyesconfig`/`allmodconfig`, ARM64 native configs, `COMPILE_TEST && 64BIT`, configurations with and without UACCE, and verifying that enabling HPRE selects QM and required asymmetric crypto algorithms.
