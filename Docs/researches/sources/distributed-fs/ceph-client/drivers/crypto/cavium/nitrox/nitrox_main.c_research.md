# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_main.c

## Purpose

`nitrox_main.c` is the PCI physical-function entry point for the Cavium CNN55XX Nitrox crypto accelerator. It binds the `CNN55XX` PCI device, performs function-level reset and BAR mapping, initializes software queues/interrupts, programs hardware units, loads SE and AE firmware, registers debugfs and Crypto API algorithms, and exposes `nitrox_get_first_device()`/`nitrox_put_device()` for algorithm front ends to borrow a ready device.

## Important APIs, Types, And Functions

- `nitrox_pci_tbl`, `nitrox_driver`, `module_pci_driver()` define the PCI match/driver object and connect `.probe`, `.remove`, `.shutdown`, and `.sriov_configure`.
- `qlen` is a module parameter controlling packet command queue length; the probed device stores it in `ndev->qlen`.
- `struct ucode` describes the firmware blob header: id, version, big-endian code size, padding, and 64-bit code payload.
- `write_to_ucd_unit()` writes firmware data into a selected UCD microcode load block by programming `UCD_UCODE_LOAD_BLOCK_NUM` and `UCD_UCODE_LOAD_IDX_DATAX()`.
- `nitrox_load_fw()` requests `cavium/cnn55xx_se.fw` and `cavium/cnn55xx_ae.fw`, validates firmware sizes, copies version strings, writes firmware blocks 0 and 2, and maps SE/AE cores to default groups.
- `nitrox_add_to_devlist()`, `nitrox_remove_from_devlist()`, `nitrox_get_first_device()`, and `nitrox_put_device()` manage the global ready-device list and reference counts.
- `nitrox_device_flr()` saves PCI config state, performs FLR, and restores state.
- `nitrox_pf_sw_init()`/`nitrox_pf_sw_cleanup()` wrap common queue allocation and interrupt registration.
- `nitrox_bist_check()` aggregates many BIST CSR values and fails initialization if any are nonzero.
- `nitrox_pf_hw_init()` sequences unit configuration, firmware load, and EMU setup.
- `nitrox_probe()`, `nitrox_remove()`, and `nitrox_shutdown()` implement lifecycle and cleanup.

## Control Flow

Probe starts with `pci_enable_device_mem()`, FLR, DMA mask setup, PCI region request, bus mastering, `struct nitrox_device` allocation, driver data installation, and global device-list insertion. The probe then records PCI IDs, timeout, NUMA node, maps BAR0, selects `min(MAX_PF_QUEUES, num_online_cpus())` queues, and applies the `qlen` module parameter.

Software setup calls `nitrox_common_sw_init()` then `nitrox_register_interrupts()`. Hardware setup first reads BIST registers, then calls the HAL configuration sequence: `nitrox_get_hwinfo()`, NPS core, AQM, packet, POM, EFL, BMI, BMO, LBC, random, firmware load, and EMU configuration. After hardware is usable, debugfs is initialized, statistics are zeroed, `__NDEV_READY` is published with an atomic barrier, and `nitrox_crypto_register()` exposes algorithms.

Removal requires the device reference count to reach zero. It marks the device not ready, removes it from the global list, disables SR-IOV, unregisters crypto algorithms and debugfs, tears down interrupts/common queues, unmaps BAR0, frees `ndev`, releases PCI regions, and disables the PCI device.

## State And Persistence Behavior

Persistent runtime state lives in the kernel driver object and hardware registers, not on disk. Global `ndevlist`, `devlist_lock`, and `num_devices` track available Nitrox devices. Each `ndev` stores hardware IDs, firmware names, queue count/length, timeout, mapped BAR, state atomics, stats, and refcount. Firmware load persists in device UCD blocks until reset. `nitrox_get_first_device()` increments `refcnt` only for a ready device; algorithm contexts later drop it through `nitrox_put_device()`.

## Dependencies And Integration Points

This file depends on Linux PCI, DMA, firmware loader, module, list/mutex/refcount APIs, and Nitrox internals from `nitrox_dev.h`, `nitrox_common.h`, `nitrox_csr.h`, `nitrox_hal.h`, `nitrox_isr.h`, and `nitrox_debugfs.h`. It integrates downward with CSR/HAL configuration and upward with the Crypto API registration layer. The firmware names are declared with `MODULE_FIRMWARE()`, so userspace firmware loading must provide the SE/AE blobs.

## Risks And Edge Cases

- Firmware validation only checks nonzero and maximum code size; malformed headers with short blobs or odd alignment can still stress firmware parsing assumptions.
- `nitrox_remove()` returns early if external references remain, leaving a partially bound device if consumers leak refs.
- `nitrox_shutdown()` is much lighter than remove and does not explicitly unregister crypto/debugfs or interrupts.
- `nitrox_load_fw()` multiplies big-endian `code_size` by two; the firmware contract must match this unit convention.
- Global list numbering decrements `num_devices` on removal, so indices can be reused across hotplug.

## Test Signals

Useful signals include successful PCI bind/unbind, firmware request/load messages, nonzero BIST failure handling, queue count and debugfs visibility, Crypto API algorithm registration, request processing through skcipher/AEAD paths, SR-IOV enable/disable transitions, and clean hot-unplug with no leaked references or IRQs.
