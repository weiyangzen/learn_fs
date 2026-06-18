# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/Makefile

Purpose: builds AMD CS5536 southbridge Virtual Support Module components for Loongson2F platforms.

Important APIs/types/functions: `CONFIG_CS5536` builds PCI, IDE, ACC, OHCI, ISA, and EHCI VSM objects; `CONFIG_CS5536_MFGPT` builds MFGPT timer support.

Control flow: object inclusion follows CS5536 Kconfig symbols.

State and persistence: build-system only.

Dependencies and integration: VSM objects virtualize CS5536 PCI config space through MSR-backed register emulation.

Risks: omitting a VSM object can make southbridge functions invisible or unconfigurable.

Test signals: CS5536 PCI enumeration, USB/IDE/ISA function config accesses, and optional MFGPT timer boot.
