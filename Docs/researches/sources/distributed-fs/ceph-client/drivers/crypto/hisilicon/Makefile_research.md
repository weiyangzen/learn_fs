# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Makefile

## Purpose
This Makefile maps HiSilicon crypto Kconfig symbols to built objects and subdirectories. It builds shared queue-manager support and routes accelerator-specific drivers to `hpre/`, `sec/`, `sec2/`, `zip/`, and `trng/`.

## Important APIs, Types, and Functions
There are no C APIs. The important build targets are `obj-$(CONFIG_CRYPTO_DEV_HISI_HPRE) += hpre/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_SEC) += sec/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_SEC2) += sec2/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_QM) += hisi_qm.o`, `obj-$(CONFIG_CRYPTO_DEV_HISI_ZIP) += zip/`, and `obj-$(CONFIG_CRYPTO_DEV_HISI_TRNG) += trng/`. The composite `hisi_qm-objs` is `qm.o sgl.o debugfs.o`.

## Control Flow
Kernel build logic expands each `obj-y` or `obj-m` based on the corresponding Kconfig symbol. When `CRYPTO_DEV_HISI_QM` is enabled, the shared `hisi_qm` module/object includes queue management, scatter-gather-list support, and debugfs support.

## State and Persistence Behavior
No runtime state is maintained. The file persists build composition rules in source control and affects module boundaries.

## Dependencies and Integration Points
This file is coupled to `Kconfig` and to object names in the HiSilicon crypto tree. HPRE has its own subdirectory Makefile that composes `hisi_hpre.o` from `hpre_main.o` and `hpre_crypto.o`.

## Risks and Edge Cases
If a source file is renamed or a Kconfig symbol changes, this Makefile is a build-break point. Because `hisi_qm-objs` includes `debugfs.o`, debugfs support is built whenever QM is built; feature assumptions must match the C code's config guards.

## Test Signals
Build with individual HiSilicon symbols enabled as modules and built-ins, verify `hisi_qm.o` composition, and verify that HPRE builds pull both the parent directory support and the `hpre/` subdirectory objects.
