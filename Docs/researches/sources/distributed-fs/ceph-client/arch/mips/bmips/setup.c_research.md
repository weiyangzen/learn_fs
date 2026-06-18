# sources/distributed-fs/ceph-client/arch/mips/bmips/setup.c

Purpose: BMIPS platform setup for DT-based Broadcom SoCs.

Important APIs and functions: setup hooks parse DT compatibility, configure restart/poweroff behavior, initialize SoC quirks, and populate platform devices.

Control flow: MIPS platform setup runs before device probing; it establishes machine callbacks and then lets OF platform population instantiate devices.

State and persistence: boot-only machine callback and device state.

Dependencies and integration points: depends on devicetree, BMIPS CPU support, OF platform, SMP/cache helpers, and reset/reboot registers.

Risks and test signals: wrong compatibility matching can select bad reboot or quirk paths. Test with BMIPS DTBs, reboot behavior, CPU info, and platform-device enumeration.
