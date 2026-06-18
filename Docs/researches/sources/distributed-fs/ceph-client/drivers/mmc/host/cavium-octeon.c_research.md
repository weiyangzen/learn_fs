# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-octeon.c

## Purpose
`cavium-octeon.c` is the OCTEON platform front end for the shared Cavium MMC/eMMC host implementation in `cavium.c`/`cavium.h`. It binds OF platform devices, maps OCTEON register windows, wires interrupt registration, bus serialization, shared power GPIO handling, and model-specific DMA corruption workarounds.

## Important APIs, Types, and Functions
The file populates `struct cvm_mmc_host` callbacks: `octeon_mmc_acquire_bus`, `octeon_mmc_release_bus`, `octeon_mmc_int_enable`, `octeon_mmc_set_shared_power`, `octeon_mmc_dmar_fixup`, and `octeon_mmc_dmar_fixup_done`. Probe and remove are `octeon_mmc_probe` and `octeon_mmc_remove`. Low-level L2 cache helpers `phys_to_ptr`, `l2c_lock_line`, `l2c_unlock_line`, `l2c_lock_mem_region`, and `l2c_unlock_mem_region` implement the EMMC-17978 workaround on affected CN6XXX/CNF7XXX models.

## Control Flow and State
Probe allocates a common host, initializes the IRQ handler spinlock and serializer semaphore, assigns common callbacks, sets optional DMA fixup callbacks for affected models, records the IO clock rate, detects CIU3/big-DMA/SG capability for `cavium,octeon-7890-mmc`, maps control and DMA resources, sets a 64-bit DMA mask, clears bootloader-left interrupts, requests either per-bit CIU3 IRQs or a legacy IRQ, acquires optional global power GPIO, and creates one platform child per slot before calling `cvm_mmc_of_slot_probe`.

Removal removes all slot hosts, disables DMA engine enable in `MIO_EMM_DMA_CFG`, and drops shared power. Bus acquisition serializes access either with `octeon_bootbus_sem` plus a CN70XX boot-bus mux write or with the host semaphore for CIU3 systems.

## State and Persistence Behavior
State is volatile in `cvm_mmc_host`: callback pointers, mapped register bases, register offsets, feature flags, slot devices, global power user count, and `n_minus_one` L2 lock address for the workaround. No persistent files are written. Shared power is reference-counted through `shared_power_users` and a global GPIO.

## Dependencies and Integration Points
The file depends on OF platform devices, OCTEON model/bootbus APIs, GPIO descriptors, DMA mask setup, IRQ type overrides for legacy firmware, and the shared `cvm_mmc_interrupt` plus slot probe/remove APIs. Compatible strings are `cavium,octeon-6130-mmc` and `cavium,octeon-7890-mmc`.

## Risks and Test Signals
Risks include model-specific paths, legacy U-Boot IRQ type workarounds, child slot creation cleanup, shared power reference imbalance, bootbus serialization, and cache-line locking for the DMA workaround. Test signals include probe on legacy and CIU3 OCTEON variants, all IRQ lines firing through `cvm_mmc_interrupt`, multi-slot add/remove, global power on/off across slots, DMA write workload on workaround models, and error unwind after partial slot creation.
