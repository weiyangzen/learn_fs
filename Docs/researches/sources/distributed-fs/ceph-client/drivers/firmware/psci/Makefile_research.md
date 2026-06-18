# sources/distributed-fs/ceph-client/drivers/firmware/psci/Makefile

Purpose: Maps PSCI configuration symbols to build objects.

Important APIs/types/functions: Builds `psci.o` for `CONFIG_ARM_PSCI_FW` and `psci_checker.o` for `CONFIG_ARM_PSCI_CHECKER`.

Control flow: No runtime flow. Kbuild includes the PSCI core and optional checker based on config.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with `psci/Kconfig` and the ARM firmware driver subtree.

Risks and test signals: Build-only risk. Test with PSCI core alone and with checker enabled.
