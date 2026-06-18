# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.c

## Purpose

This file is the PCMCIA module front-end for Digigram VXPocket and VXPocket440 cards. It handles module parameters, card allocation, PCMCIA resource configuration, IRQ registration, hardware variant detection, firmware setup, suspend/resume, and ALSA card lifetime.

## Important APIs, types, and functions

`vxpocket_probe()` allocates an ALSA card, reserves a card index, calls `snd_vxpocket_new()`, and runs `vxpocket_config()`. `snd_vxpocket_new()` creates a `vx_core` with VXPocket hardware data and `snd_vxpocket_ops`, stores PCMCIA config requirements, and returns the embedded `snd_vxpocket`. `vxpocket_config()` selects VXPocket440 metadata based on CIS product string, requests I/O, registers a shared threaded IRQ using VX core handlers, enables the PCMCIA device, and calls `snd_vxpocket_assign_resources()` to load firmware. `vxpocket_detach()` disconnects and frees safely.

## Control flow

Probe finds a free module slot, honors `enable[]`, creates the ALSA card, creates the VX core, configures PCMCIA, and leaves card registration to the VX firmware/setup path. Config failure unwinds IRQ and PCMCIA resources. Detach marks the core stale, disconnects ALSA, releases IRQ/device resources, and defers card memory free until users close the card.

## State and persistence behavior

Global `card_alloc` tracks occupied module parameter slots. Per-device state lives in `struct snd_vxpocket` and embedded `vx_core`; `link->priv` points to the core. Hardware capabilities are persisted in `chip->hw` and `chip->type`, overwritten for 440 cards.

## Dependencies and integration points

It depends on PCMCIA CIS/resource APIs, ALSA card/module APIs, shared VX core firmware setup, and `vxp_ops.c` for hardware callbacks. It uses `request_threaded_irq()` with `snd_vx_irq_handler` and `snd_vx_threaded_irq_handler`.

## Risks and test signals

Risks include CIS string assumptions, card-index leaks on partial failure, IRQ/resource ordering during detach, and stale state while user file handles remain open. Test insertion/removal, disabled module slot behavior, V2 versus 440 detection, firmware load failure unwind, suspend/resume with card present, and hot-unplug during PCM use.
