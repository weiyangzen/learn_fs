# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/platform.c

Purpose: registers SWARM/LittleSur platform devices for PATA and SB1250 Ethernet MACs.

Important APIs/types/functions: `swarm_pata_init`, `sb1250_device_init`, `swarm_pata_device`, `sb1250_dev_struct` platform device templates.

Control flow and state: PATA init checks board IDE availability, reads GenBus chip-select mapping, computes command/control MMIO resources, and registers `pata_platform`; MAC init registers 2, 3, or 4 `sb1250-mac` devices based on `soc_type`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: GenBus decoding must be correct or PATA maps the wrong bus region; device count depends on SoC type; resources are static and hardware-specific.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
