# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/b43legacy.h

## Purpose
Central private header for the legacy Broadcom 43xx driver. It defines MMIO offsets, SHM routing constants, host flags, IRQ masks, rate constants, firmware file formats, PHY/radio state, DMA/PIO container state, shared mac80211 device state, per-core device state, locking rules, low-level SSB accessors, and logging prototypes.

## Important APIs, Types, and Functions
Important structures are `b43legacy_wl` for chip-wide mac80211 state, `b43legacy_wldev` for one SSB 802.11 core, `b43legacy_phy`, `b43legacy_dma`, `b43legacy_pio`, `b43legacy_firmware`, `b43legacy_key`, `b43legacy_noise_calculation`, and `b43legacy_stats`. Firmware ABI types are `b43legacy_fw_header` and `b43legacy_iv`. Inline helpers include `hw_to_b43legacy_wl`, `dev_to_b43legacy_wldev`, `b43legacy_using_pio`, `b43legacy_is_mode`, MMIO read/write wrappers, `b43legacy_get_lopair`, and board-vendor checks.

## Control Flow
The header establishes state-machine and locking contracts rather than implementing major flow. `b43legacy_status` and `b43legacy_set_status` wrap the atomic initialization state transitions among uninitialized, initialized, and started. `b43legacy_using_pio` compiles to runtime or constant selection depending on Kconfig. MMIO helpers route all register access through SSB read/write primitives.

## State and Persistence
All defined state is live kernel driver state. Persistent hardware/firmware-facing state includes SHM offsets, key-table pointers, GPIO/radio bits, firmware references, calibration tables, and rate tables stored in device memory. The lock policy states that `wl->mutex` and `wl->irq_lock` usually protect core state, with exceptions for IRQ, tasklet, and packet TX paths.

## Dependencies and Integration Points
Depends on Linux kernel primitives, SSB, mac80211, debugfs/LED/rfkill/PHY headers, hwrng, netdevice, PCI, and atomic/spinlock APIs. It is consumed by nearly every b43legacy source file.

## Risks
Changing constants can break undocumented firmware/hardware ABI. The shared `union` of DMA and PIO state assumes only one backend is active. Lock-order mistakes around `wl->mutex` and `irq_lock` can deadlock IRQ/tasklet/workqueue paths. Structure fields are widely shared, so small changes have high blast radius.

## Test Signals
Compile coverage across config variants, sparse/lockdep runs, probe/init/start/stop cycles, suspend/resume, RF-kill transitions, and mixed DMA/PIO builds validate this header. Hardware smoke tests are essential because many constants are only validated by device behavior.
