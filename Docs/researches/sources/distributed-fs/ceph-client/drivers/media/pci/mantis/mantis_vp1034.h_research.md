# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.h

- Purpose: Board declaration header for Mantis VP-1034.
- Important APIs/types/functions: Defines PCI subsystem ID macro(s) `MANTIS_VP_1034_DVB_S and `vp1034_set_voltage`` and declares the exported `struct mantis_hwconfig` used by the PCI ID table.
- Control flow: Included by `mantis_cards.c` so `MAKE_ENTRY` can bind a matching PCI subsystem ID to the board configuration; implementation files provide the actual frontend attach logic.
- State and persistence: No runtime state or persistence.
- Dependencies and integration points: Depends on `mantis_common.h` for `struct mantis_hwconfig` and on DVB frontend types where voltage callback is declared.
- Risks: Incorrect IDs or missing extern declarations would prevent board matching or link-time resolution.
- Test signals: Compile coverage and PCI ID probe tests for the board.
