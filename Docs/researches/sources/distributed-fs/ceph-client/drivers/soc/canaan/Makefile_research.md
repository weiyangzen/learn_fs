# sources/distributed-fs/ceph-client/drivers/soc/canaan/Makefile

Purpose: Kbuild file for Canaan SoC drivers.

Important build behavior: `obj-$(CONFIG_SOC_K210_SYSCTL) += k210-sysctl.o` compiles the K210 system controller only when the matching Kconfig option is enabled.

Control flow and integration: this Makefile connects the Canaan SoC directory to the K210 sysctl driver. Runtime behavior is entirely in `k210-sysctl.c`.

State and persistence: no runtime state.

Risks and test signals: risk is limited to object selection drift. Test signals are successful K210 builds and absence of the object when the option is disabled.
