# sources/distributed-fs/ceph-client/drivers/virt/coco/Kconfig

## Purpose
Top-level Kconfig menu for confidential-computing collateral under `drivers/virt/coco`.

## APIs, Types, and Functions
It conditionally sources EFI secret, pKVM guest, SEV guest, TDX guest, Arm CCA guest, and shared guest Kconfig files when `VIRT_DRIVERS` is enabled. It also declares boolean `TSM`, the class-device switch for `tsm-core.c`.

## Control Flow and State
There is no runtime state. Build-time state is the selected set of confidential-computing features and their transitive selects such as `TSM_REPORTS` and `TSM_MEASUREMENTS`.

## Dependencies and Integration
Feeds the `drivers/virt/coco/Makefile` object selection. It integrates multiple architecture-specific guest drivers under one menu.

## Risks and Test Signals
Risk is misconfigured symbol naming. The Makefile uses `CONFIG_INTEL_TDX_GUEST` for the `tdx-guest/` directory, while the TDX guest sub-Kconfig defines `TDX_GUEST_DRIVER`; this relies on an external architecture symbol to descend into the directory. Build tests should cover x86 TDX, AMD SEV, arm64 CCA, pKVM, EFI secret, and `CONFIG_TSM` combinations.
