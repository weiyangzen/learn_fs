# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/Makefile

Purpose: build glue for Broadcom STB power management support. It compiles the MIPS PM C implementation and S2/S3 assembly helpers when `CONFIG_MIPS` is enabled.

Important API/build behavior: `obj-$(CONFIG_MIPS)` adds `pm-mips.o`, `s2-mips.o`, and `s3-mips.o`. These objects provide `brcm_pm_do_s2()`, `brcm_pm_do_s3()`, `s3_reentry`, and the arch init logic that installs suspend and power-off operations.

Control flow and integration: the Makefile keeps this PM implementation architecture-specific. Non-MIPS builds of the brcmstb PM directory do not consume the MIPS-only assembly and CP0 register dependencies.

State and persistence: no runtime state is defined here; persistence is via kernel build composition.

Dependencies, risks, and tests: depends on Kbuild selecting this subdirectory from the parent Broadcom STB SoC build. Risks are missing PM symbols if the object list diverges from `pm.h` declarations. Test signals are successful MIPS build/link with suspend symbols resolved and absence of these objects in non-MIPS builds.
