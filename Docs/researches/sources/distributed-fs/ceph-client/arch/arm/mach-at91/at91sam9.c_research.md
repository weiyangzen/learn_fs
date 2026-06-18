# sources/distributed-fs/ceph-client/arch/arm/mach-at91/at91sam9.c

Purpose: declares the DT machine descriptor for Atmel AT91SAM9 systems. It matches `atmel,at91sam9` and installs `at91sam9_pm_init` as late init.

Control flow is ARM DT machine matching and deferred PM setup; no local persistent state exists. Dependencies include `generic.h`, system misc headers, and a matching root DT compatible. Risks are compatible mismatch and PM init being stubbed when CONFIG_PM is off. Test signals include AT91SAM9 DT boot selecting this descriptor and PM initialization behavior when enabled.
