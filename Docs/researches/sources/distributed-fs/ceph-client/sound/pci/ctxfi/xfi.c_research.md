# sources/distributed-fs/ceph-client/sound/pci/ctxfi/xfi.c

## Purpose

This is the PCI module entry point for Creative X-Fi ctxfi cards. It matches Creative 20K1/20K2 devices, creates ALSA cards, delegates hardware/ATC setup, registers ALSA devices, and wires PM callbacks.

## Important APIs, types, and functions

Static module parameters include `reference_rate`, `multiple`, `index`, `id`, `enable`, and `subsystem`. `ct_pci_dev_ids` maps PCI IDs to `ATC20K1`/`ATC20K2`. `ct_card_probe()` creates and registers the card. `ct_card_remove()` frees it. `ct_card_suspend()` and `ct_card_resume()` delegate to ATC when PM is enabled. `ct_driver` is registered through `module_pci_driver()`.

## Control flow

Probe checks the global card slot, honors `enable[]`, creates `snd_card`, validates module parameters, calls `ct_atc_create()`, creates ALSA devices through `ct_atc_create_alsa_devs()`, fills card names, registers the card, stores drvdata, and increments the static device counter. Error paths free the card. Remove frees drvdata. PM retrieves `ct_atc` from card private data.

## State and persistence behavior

State includes module parameters, a static probe counter, ALSA card private data, PCI drvdata, and ATC-managed hardware state. No persistent user configuration is stored beyond module parameters.

## Dependencies and integration points

It depends on Linux PCI/module APIs, ALSA card initialization, `ctatc.h`, and `cthardware.h`. It is the parent integration point for all ctxfi PCM, mixer, timer, resource, and hardware backend modules.

## Risks and test signals

Risks include the static `dev` counter not being decremented on remove, global mutation of invalid module parameters, subsystem override misuse, and PM callback assumptions about drvdata. Test signals include module load/unload, multi-card probing, invalid parameter fallback messages, suspend/resume, and correct ALSA card naming for 20K1 and 20K2 devices.
