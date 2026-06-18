# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_intel_dg.c

Purpose: MTD driver for Intel discrete graphics NVM exposed by i915/xe auxiliary devices. It maps firmware-defined NVM regions into a master MTD with per-region partitions and performs register-mediated read, write, and erase operations.

Important APIs/types/functions: `struct intel_dg_nvm` owns refs, MTD, runtime-PM device, MMIO bases, lock, size, and flexible region table. Low-level helpers are `idg_nvm_read32/64()`, `idg_nvm_write32/64()`, `idg_nvm_error()`, `idg_nvm_get_access_map()`, and `idg_nvm_is_valid()`. MTD callbacks are `intel_dg_mtd_read()`, `intel_dg_mtd_write()`, and `intel_dg_mtd_erase()`. Lifecycle is `intel_dg_mtd_probe()`/`intel_dg_mtd_remove()`.

Control flow: probe copies named regions from `intel_dg_nvm_aux`, enables runtime PM, maps BAR resources, validates the flash signature, reads descriptor access permissions, computes region offsets/sizes from flash descriptor records, creates MTD partitions for readable regions, and registers the master MTD. Reads and writes find the containing region, clip to its end, resume PM, lock, issue aligned 32/64-bit register accesses with workarounds, set retlen, then autosuspend. Erase requires 4 KiB alignment, walks regions, and erases 4 KiB blocks.

State and persistence: persistent state is GPU NVM content and descriptor metadata. Runtime state includes access permissions, region geometry, non-posted erase mode, BAR mappings, runtime PM usage, mutex, and kref lifetime. `_get_device`/`_put_device` hold `nvm` while partition users are active.

Dependencies/integration: depends on `linux/intel_dg_nvm_aux.h`, auxiliary bus IDs `i915.nvm` and `xe.nvm`, MMIO accessors, `pm_runtime`, MTD partition registration, and optional second BAR for non-posted erase completion.

Risks: debug logging references `nvm->regions[idx]` before checking `idx >= nregions` in read/write, which is risky on out-of-range offsets. Cross-region requests are clipped for read/write but erase loops. Partial writes read-modify-write 32-bit words, so concurrent access must remain serialized. Hardware-specific 1 KiB boundary workaround is fragile.

Test signals: validate descriptor signature failure, unreadable/writable partition masks, runtime PM get failures, unaligned erase rejection, reads/writes around unaligned offsets and 1 KiB boundaries, non-posted erase timeout/fail_addr, remove while partitions are open.
