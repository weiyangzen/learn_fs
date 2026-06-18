# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.c

## Purpose
Implements the b43legacy driver core: module parameters, SSB probe/remove, mac80211 registration and operations, firmware loading/upload, chip/core init and teardown, interrupt handling, beacon/template management, TX workqueue, periodic calibration/noise work, RF/radio configuration, suspend/resume, restart recovery, and low-level SHM/TSF/MMIO helpers.

## Important APIs, Types, and Functions
Key lifecycle functions are `b43legacy_probe`, `b43legacy_remove`, `b43legacy_wireless_init`, `b43legacy_one_core_attach`, `b43legacy_wireless_core_attach`, `b43legacy_wireless_core_init`, `b43legacy_wireless_core_start`, `b43legacy_wireless_core_stop`, `b43legacy_wireless_core_exit`, and `b43legacy_controller_restart`. mac80211 ops include TX, config, BSS changes, filter configuration, add/remove interface, start/stop, TIM update, survey, stats, and rfkill poll. Hardware helpers include SHM read/write, TSF read/write, MAC suspend/enable, GPIO init/cleanup, chip init, firmware upload/initvals, IRQ top/bottom halves, beacon/probe template writers, and retry/rate memory setup.

## Control Flow
Module init creates debugfs and registers an SSB driver. Probe allocates a mac80211 hw object on the first core, attaches each SSB core, performs lightweight PHY/radio discovery, adds debugfs, and schedules firmware loading. Firmware work requests ucode/PCM/initval files and registers the hw with mac80211. `start` initializes the core if needed, uploads firmware and initvals, initializes PHY/radio/GPIO/DMA or PIO/security/RNG/LEDs, requests IRQ, enables MAC/queues/interrupts, and schedules periodic work. TX from mac80211 is queued per priority and drained by workqueue into DMA or PIO. IRQ top half snapshots reason registers, acknowledges/masks interrupts, and schedules a tasklet; the tasklet processes DMA RX, TX status, beacon slots, TBTT/ATIM/PMQ, noise samples, DMA errors, and restart triggers. Stop disables IRQs, synchronizes tasklet, cancels work, drains queues, suspends MAC, and frees IRQ; exit stops firmware PSM, frees transfer backends and calibration memory, disables radio/analog/core, and powers down the bus.

## State and Persistence
Live state spans `b43legacy_wl` and `b43legacy_wldev`: current core, interface mode, BSSID/MAC, filter flags, queues, beacon skb/template flags, firmware refs, PHY calibration data, IRQ masks/reasons, DMA/PIO backend state, key table pointer, radio flags, RNG/LED/debugfs state, and initialization status. Hardware state persists in SHM, template RAM, GPIO, MMIO control registers, TSF registers, firmware PSM memory, and radio/PHY registers until reset or powerdown.

## Dependencies and Integration Points
Integrates with SSB, mac80211, firmware loader, Linux workqueues/tasklets/IRQs, DMA/PIO modules, PHY/radio/sysfs/rfkill/xmit/debugfs/LED modules, hwrng, PCI/SPROM board data, and kernel PM. Firmware files under `b43legacy*/` are external runtime dependencies.

## Risks
This file has high concurrency risk: `wl->mutex`, `irq_lock`, tasklet, workqueues, and IRQ masking must stay ordered. Firmware and initval format validation is strict but firmware availability fails at runtime. Restart, suspend/resume, and remove paths must coordinate queued work and firmware completion. Beacon template updates are asynchronous to avoid firmware transmitting partially updated templates. Some code is explicitly FIXME/TODO, including limited queue mapping, probe response handling, AP power-save, and ucode debug.

## Test Signals
Critical signals include probe/register/unregister with firmware present and absent, start/stop cycles, DMA and PIO traffic, association as STA, AP/IBSS beacon template updates, channel and retry-limit reconfiguration, RF-kill and software radio toggles, suspend/resume, controller restart after injected DMA/PHY errors, debugfs restart, hwrng registration, and lockdep under traffic plus module removal.
