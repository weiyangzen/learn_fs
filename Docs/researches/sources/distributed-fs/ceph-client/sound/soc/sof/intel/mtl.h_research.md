# sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.h

Purpose: defines Meteor Lake/ACE register offsets, bit masks, SRAM/mailbox windows, ROM state codes, IMR flags, and prototypes for MTL helper functions used by MTL, ARL, LNL, NVL, and PTL-derived platform code.

Important APIs: register groups cover DSP subsystem power (`MTL_HFDSSCS`), power-gated domains (`MTL_HFPWRCTL*`/`PTL_HFPWRCTL2`), interrupt IP pointer, HDA D0i3, primary core controls, IPC initiator/target registers, host IPC/SoundWire interrupt enables, IRQ status, SRAM windows, ROM status/error registers, and ROM FSR state codes. Prototypes export IPC IRQ check, interrupt enable/disable, DSP power down, code-loader init, and `sof_mtl_set_ops()`.

Control flow role: no executable flow, but the constants are directly consumed by `mtl.c` boot, IPC, IRQ, and power sequences and by later platforms that reuse MTL helpers.

State and persistence: none in the header; constants identify hardware state registers used elsewhere.

Dependencies and integration: requires Linux bit macros through including files. Shared by MTL and descendants, so changes affect multiple PCI modules.

Risks and test signals: risks include wrong offsets across ACE generations and using PTL versus MTL power registers incorrectly. Test by building MTL/LNL/NVL/PTL, validating MMIO access does not read `U32_MAX`, and checking firmware boot/IRQ paths on each generation.
