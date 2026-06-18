# sources/distributed-fs/ceph-client/drivers/firmware/psci/Kconfig

Purpose: Defines build options for ARM PSCI firmware support and the optional PSCI checker.

Important APIs/types/functions: `ARM_PSCI_FW` is the base bool. `ARM_PSCI_CHECKER` depends on PSCI firmware, CPU hotplug, CPU idle, and excludes torture tests.

Control flow: No runtime flow in this file. It controls inclusion of PSCI core and checker objects.

State and persistence behavior: No state. Enabling checker causes startup validation of PSCI hotplug and suspend behavior elsewhere.

Dependencies and integration points: Integrates with ARM firmware, CPU hotplug, CPU idle, and test/torture configuration.

Risks and test signals: Checker can interfere with CPU torture tests, hence the explicit dependency exclusion. Test Kconfig resolution for architectures selecting `ARM_PSCI_FW` and checker enable/disable combinations.
