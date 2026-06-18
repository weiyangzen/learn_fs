# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/platsmp.c

Purpose: MediaTek secondary CPU boot support for TrustZone and non-TrustZone boot-info register protocols.

Important APIs/types/functions: Defines `struct mtk_smp_boot_info`, boot-info tables for MT8135/MT8127/MT2701, MT6572, MT6589, MT7623/MT6582/MT7629, `mtk_boot_secondary()`, `__mtk_smp_prepare_cpus()`, `mtk_tz_smp_prepare_cpus()`, `mtk_smp_prepare_cpus()`, and CPU method declarations for `mediatek,mt81xx-tz-smp` and `mediatek,mt6589-smp`.

Control flow: Prepare selects the boot-info table by root compatible, maps the boot register block either with `phys_to_virt()` for TrustZone-reserved SRAM or `ioremap()` for normal MMIO, then writes `secondary_startup_arm` to the SoC jump register. Boot validates the requested CPU has a nonzero magic key, writes that key to the per-core release register, and sends a wakeup IPI.

State and persistence: Global state is `mtk_smp_base` and `mtk_smp_info`. Hardware/firmware state includes the jump register and per-core release-key registers in reserved SRAM/MMIO; no persistent kernel-managed resource remains after boot.

Dependencies and integration points: Depends on DT root compatible strings, CPU method compatible strings, ARM SMP core, `secondary_startup_arm`, fixed boot-info addresses/register offsets, and TrustZone firmware/reserved-memory behavior for the TZ path.

Risks: CPU indexes are used as `cpu - 1` into fixed arrays and only support the encoded number of secondary cores. TrustZone mode assumes the physical boot-info area is already mapped/reserved so `phys_to_virt()` is valid. Missing or wrong compatible data leaves `mtk_smp_base` unset and secondary boot fails with `-EINVAL`.

Test signals: Boot SMP on each supported MediaTek SoC, validate CPU1+ online, and test both `mediatek,mt81xx-tz-smp` and `mediatek,mt6589-smp` DT CPU methods.
