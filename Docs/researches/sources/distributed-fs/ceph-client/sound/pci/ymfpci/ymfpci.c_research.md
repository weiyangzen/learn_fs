# sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.c

Purpose: Provides the PCI probe/module wrapper for Yamaha DS-1 family cards (`YMF724`, `YMF724F`, `YMF740`, `YMF740C`, `YMF744`, `YMF754`). It handles module parameters, card creation, legacy FM/MPU/gameport resource configuration, calls the core YMFPCI initialization routines, and registers the ALSA card.

Important APIs/types/functions: Module arrays configure card index/id/enable, optional FM and MPU IO ports, optional joystick port, and rear/line-in switch. `snd_ymfpci_ids[]` lists supported PCI IDs. `snd_ymfpci_create_gameport()` and `snd_ymfpci_free_gameport()` manage optional gameport resources and PCI legacy registers. `__snd_card_ymfpci_probe()` performs card allocation, model naming, legacy register selection, resource requests, calls `snd_ymfpci_create()`, creates PCM/SPDIF/mixer/timer interfaces, optional 4-channel and secondary capture PCMs, optional MPU401 rawmidi, optional OPL3 hwdep, gameport, and finally card registration.

Control flow: Probe is gated by static `dev` and `enable[dev]`. Newer YMF744/754 chips can autodetect FM/MPU/gameport bases from PCI BARs/config registers; older chips restrict ports to fixed legacy choices encoded in `PCIR_DSXG_ELEGACY`. The code writes legacy control registers before calling `snd_ymfpci_create()` and preserves old legacy control for cleanup. Optional MPU and OPL3 failures disable the corresponding legacy IRQ/enable bits but do not fail the whole sound card unless hwdep creation fails after OPL3 creation.

State and persistence: Persistent chip state is allocated as `card->private_data` and initialized in `ymfpci_main.c`; this file contributes legacy resource choices, `old_legacy_ctrl`, optional rawmidi/OPL3/gameport setup, and card naming. Gameport state is stored in `chip->gameport`.

Dependencies/integration: Depends on Linux PCI/module/time, ALSA core/initval, MPU401, OPL3, optional gameport, and the `ymfpci.h` helper API. Integrates with `module_pci_driver`, ALSA card lifecycle, and legacy PC IO port resource management.

Risks: Legacy IO port encoding differs before and after YMF744/754, so resource validation regressions can break FM/MPU/gameport. The static `dev` index can be consumed by disabled or failed probes. Card longname is initially formatted before `snd_ymfpci_create()` sets `reg_area_phys`/IRQ, so later registration behavior should be checked if user-facing names matter. Optional feature failures must leave PCI legacy registers consistent.

Test signals: Probe each supported PCI ID, test module parameter combinations for FM/MPU/gameport/rear switch, verify `snd_ymfpci_create()` plus PCM/mixer/timer creation, check MPU401 and OPL3 optional devices, confirm gameport registration and teardown, and suspend/resume through `snd_ymfpci_pm`.
