# sources/distributed-fs/ceph-client/drivers/nvmem/qfprom.c

Purpose: Qualcomm QFPROM NVMEM provider for corrected/raw fuse reads and optional permanent fuse programming.

Important APIs/types/functions: `struct qfprom_priv` stores corrected, raw, config, and security MMIO regions plus clock/regulator/power data. `qfprom_reg_read()` reads corrected data by default or raw data under module parameter `read_raw_data`. `qfprom_enable_fuse_blowing()` and `qfprom_disable_fuse_blowing()` sequence clock rate, regulator voltage, runtime PM, genpd performance, timer, and accel values. `qfprom_reg_write()` performs aligned word writes to raw fuses. `qfprom_fixup_dt_cell_info()` aligns NVMEM cells to 32-bit read granularity.

Control flow: probe always maps corrected space and registers read access. If raw/config/security resources exist, it maps them, reads QFPROM version, selects known SoC programming constants, gets regulator and optional clock, and enables writes only when all required programming data is available. Read path loops 32-bit words. Write path validates word alignment, enables fuse-blowing conditions, waits for ready, writes each word, waits for ready again, then restores all touched hardware state.

State/persistence: fuses are permanent. Runtime state includes MMIO mappings and supplies; `read_raw_data` is mutable module state affecting all instances. Keepout tables hide SoC-specific unsafe ranges from NVMEM access.

Dependencies/integration: OF compatibles `qcom,qfprom`, `qcom,sc7180-qfprom`, and `qcom,sc7280-qfprom`; depends on regulator, clock, runtime PM, power domains, NVMEM keepouts, and fixed OF cells.

Risks: write operations are irreversible and rely on exact clock/voltage/timer sequencing. Writes are silently unavailable on unsupported QFPROM versions or absent clock/soc data. Raw reads through a module parameter may expose uncorrected or sensitive data. The 32-bit cell fixup changes offsets/bit offsets, so cell definitions must be validated carefully.

Test signals: corrected versus raw read mode, keepout enforcement, unsupported write setup, alignment errors, regulator/clock/genpd failure unwinding, fuse-blow timeout, and DT cell fixup for unaligned cells.
