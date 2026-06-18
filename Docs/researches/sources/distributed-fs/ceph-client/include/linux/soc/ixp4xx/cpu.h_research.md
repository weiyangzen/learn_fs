# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/cpu.h

Purpose: This Intel/IXP4xx header defines CPU and SoC identification helpers for legacy IXP4xx network processor platforms.

Important APIs/types/functions: It provides macros and inline helpers that classify IXP4xx variants based on CPU or SoC ID values, along with constants for supported devices and revisions.

Control flow: Platform setup and drivers call the helpers to select register maps, feature availability, and errata workarounds.

State and persistence: No state is owned by the header. It interprets CPU ID state obtained from architecture registers or platform code.

Dependencies and integration: Integrates with ARM IXP4xx platform code, NPE, queue manager, Ethernet, PCI, GPIO, and board-file support.

Risks and test signals: Wrong ID masks can enable unsupported peripherals or skip required errata. Test variant detection on each supported IXP4xx CPU, compile with and without platform options, and boot/probe of dependent NPE/QMGR devices.
