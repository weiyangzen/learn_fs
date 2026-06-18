# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/Makefile

Purpose: defines the build composition for x86 machine-check exception support.

Important APIs and flow: `core.o`, `severity.o`, and `genpool.o` are always built for this directory. Optional objects are selected by Kconfig: ancient P5/Winchip handlers, Intel MCE support, AMD MCE support, threshold interrupt support, the `mce-inject` module/object from `inject.o`, APEI bridge support, and legacy `/dev/mcelog`.

State and persistence: no runtime state; this file controls which machine-check code exists in the kernel image or module set.

Dependencies and integration: ties `CONFIG_X86_ANCIENT_MCE`, `CONFIG_X86_MCE_INTEL`, `CONFIG_X86_MCE_AMD`, `CONFIG_X86_MCE_THRESHOLD`, `CONFIG_X86_MCE_INJECT`, `CONFIG_ACPI_APEI`, and `CONFIG_X86_MCELOG_LEGACY` to the implementation files in this folder.

Risks and test signals: incorrect object selection can leave unresolved symbols or silently remove vendor handling. Signals are configuration matrix builds, module build for injection, and boot tests with optional legacy and ACPI APEI paths enabled/disabled.
