<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c

Purpose: Synthesizes Loongson CPUCFG feature words for Loongson processors lacking hardware CPUCFG and advertises CPUCFG to userspace when usable.

Important APIs/types/functions: `loongson3_cpucfg_synthesize_data(struct cpuinfo_mips *c)`, plus helpers `is_loongson()`, `cpu_has_uca()`, `probe_uca()`, `decode_loongson_config6()`, and `patch_cpucfg_sel1/2/3()`.

Control flow: Non-Loongson CPUs return. CPUs with hardware CPUCFG skip synthesis but still set HWCAP. Known Loongson revisions build selector 1-3 feature words from PRID, Config6, UCAC probing, ASE flags, FPU revision, and CPU options, then patch dynamic features.

State and persistence: Writes `c->loongson3_cpucfg_data[]` and global `elf_hwcap`.

Dependencies and integration: Uses Loongson PRID/config register definitions and MIPS ELF hwcap exposure.

Risks: Briefly toggles diagnostic UCAC bit to probe capability. Unknown future Loongson CPUs without CPUCFG get no emulation, intentionally conservative.

Test signals: Userspace `HWCAP_LOONGSON_CPUCFG` should appear on supported cores, and emulated CPUCFG selectors should match documented revision features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c -->
