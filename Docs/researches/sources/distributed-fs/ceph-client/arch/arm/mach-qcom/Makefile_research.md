# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Makefile

Purpose: build rule for Qualcomm ARM machine support.

Important APIs/types/functions: adds `platsmp.o` only when `CONFIG_SMP` is enabled.

Control flow: make-time object selection; no runtime flow.

State and persistence: none.

Dependencies and integration points: couples Qualcomm ARM support to the generic ARM SMP framework and Kconfig `CONFIG_SMP`.

Risks: non-SMP Qualcomm builds omit all code in this directory, so any future non-SMP machine hooks would need Makefile changes.

Test signals: build matrix with `ARCH_QCOM=y` and SMP on/off, confirming object inclusion matches expected symbols.
