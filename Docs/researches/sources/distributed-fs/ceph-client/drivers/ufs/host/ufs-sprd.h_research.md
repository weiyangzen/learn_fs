# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.h

## Purpose
`ufs-sprd.h` is the private definitions header for the Unisoc UFS host driver. It collects vendor DME attributes, syscon offsets/bits, the ARM SMCCC function ID for storage crypto key access, enum indexes for reset/syscon/regulator arrays, and the Sprd host/private structures.

## Important APIs, Types, And Macros
Key macros include `RXSQCONTROL`, `CBRATESEL`, `CBCREG*`, `CBREFCLKCTRL2`, `VS_MPHYDISABLE`, AON APB reference-clock/PLL bits, and `SPRD_SIP_SVC_STORAGE_UFS_CRYPTO_ENABLE`. `enum SPRD_UFS_RST_INDEX`, `enum SPRD_UFS_SYSCON_INDEX`, and `enum SPRD_UFS_VREG_INDEX` provide stable array positions. `struct ufs_sprd_priv` stores named reset controls, syscon regmaps, regulators, and an embedded `ufs_hba_variant_ops`; `struct ufs_sprd_host` stores the active HBA, private SoC descriptor, optional debug MMIO, and cached UniPro version.

## Control Flow And State
The header does not execute code. The array-index enums drive DT parsing and N6 callback access in `ufs-sprd.c`. The embedded variant ops allow OF match data to point at the ops member and recover the containing SoC descriptor with `container_of()`.

## Dependencies And Integration Points
This header integrates with Linux reset, regmap, regulator, ARM SMCCC, and UFS core types through its including C file. It is private to `ufs-sprd.c`; no symbols are exported from it.

## Risks And Edge Cases
The `container_of()` match-data pattern depends on OF data pointing exactly to `ufs_hba_sprd_vops`. Any new SoC entry must keep array indexes aligned with callback assumptions. The SMCCC call value is a firmware ABI and must match secure monitor implementation.

## Test Signals
Compile tests should catch missing UFS/SMCCC constants. Runtime tests should validate the N6 descriptor arrays resolve every named DT resource and that crypto enable calls reach firmware with the expected function ID.
