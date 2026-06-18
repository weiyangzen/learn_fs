# sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.c

## Purpose
`vt1720_mobo.c` supplies minimal VT1720/Envy24PT motherboard support for Albatron, Chaintech, and Shuttle boards. It mainly provides EEPROM defaults and a shared initialization callback for VT1616 AC-link based onboard audio.

## Important APIs, Types, and Functions
- `k8x800_init()` marks the device as VT1720, sets six DACs and two ADCs, and leaves a WM8728 TODO.
- `k8x800_add_controls()` is a placeholder for future VT1616 quirks.
- `k8x800_eeprom[]` and `sn25p_eeprom[]` provide static EEPROM configuration images.
- `snd_vt1720_mobo_cards[]` maps five supported subdevices to names, models, callbacks, and EEPROM data.

## Control Flow
The generic ICE1724 probe selects a matching table entry, loads the EEPROM image, calls `k8x800_init()`, and later calls `k8x800_add_controls()`. All listed boards share the same initialization path; SN25P gets a variant EEPROM with S/PDIF bits.

## State and Persistence
The only state change is runtime initialization of `ice->vt1720`, `num_total_dacs`, and `num_total_adcs`. EEPROM arrays are static data consumed by the core; there is no dynamic board-private allocation.

## Dependencies and Integration Points
The file depends on ICE1712/Envy24HT core types and constants. It integrates by exporting `snd_vt1720_mobo_cards[]`.

## Risks and Test Signals
The main risk is incomplete hardware support: control quirks and WM8728 support are marked TODO, so board-specific mixer behavior may be missing. The SN25P table entry uses `sizeof(k8x800_eeprom)` with `sn25p_eeprom` data, which is currently the same size but is a maintenance trap. Test signals include successful probe, AC97/AC-link codec availability, channel count reporting, and no regression in EEPROM-derived GPIO setup.
