# sources/distributed-fs/ceph-client/sound/ppc/burgundy.c

## Purpose

This file implements low-level register access, default programming, ALSA controls, and automute for the PowerMac Burgundy codec.

## Important APIs, types, and functions

`snd_pmac_burgundy_init()` is the exported initializer. Register helpers `snd_pmac_burgundy_wcw()/rcw()` and `wcb()/rcb()` access 32-bit word and byte codec registers using AWACS codec command/status cycles. Control helper families implement 0-100 volumes, two-byte volumes, gain/attenuation, word switches, and byte switches. The mixer arrays select common, iMac-specific, and PowerMac-specific controls. `snd_pmac_burgundy_detect_headphone()` and `snd_pmac_burgundy_update_automute()` handle jack routing.

## Control flow

Initialization checks whether the codec appears disabled, writes output/input/gain/attenuation/default volume registers, sets the headphone-detect mask, builds common and model-specific ALSA controls, creates master/speaker/line/headphone switches, registers automute controls, installs detect/update callbacks, and applies initial routing. Control puts write hardware, read back values, and report changes based on hardware-observed state.

## State and persistence behavior

Unlike AWACS, Burgundy control state is mostly read back from hardware rather than cached in a large software register array. Persistent driver state is mainly `chip->hp_stat_mask`, ALSA control pointers, and common `snd_pmac` fields. Register read/write sequences are protected by `reg_lock` for read paths.

## Dependencies and integration points

It depends on AWACS MMIO command/status registers, `burgundy.h` register definitions, Open Firmware `of_machine_is_compatible("iMac")`, ALSA controls, and `snd_pmac_add_automute()` from `pmac.c`. It is selected by `powermac.c` when `snd_pmac_detect()` reports `PMAC_BURGUNDY`.

## Risks and test signals

Risks include busy/extend wait timeouts, inconsistent locking for write helpers, model-specific output mask mistakes, returning success from init when MacOS disabled the codec, and fragile read-back based change detection. Test Burgundy iMac and non-iMac mixer maps, all input/output switches, headphone automute, register timeout logs, and suspend/removal behavior.
