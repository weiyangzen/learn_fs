# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.c

## Purpose

`qcom_pil_info.c` records Qualcomm Peripheral Image Loader relocation information in a reserved IMEM region described by the `qcom,pil-reloc-info` DT node. Remoteproc/PIL drivers call it to publish loaded firmware image name, base address, and size for post-mortem crash analysis.

## Important APIs, types, and functions

- `PIL_RELOC_NAME_LEN` is 8 bytes; each entry stores an 8-byte name, 64-bit little-endian base, and 32-bit little-endian size.
- `struct pil_reloc` stores the mapped IMEM base and number of entries.
- `_reloc` is a module-global, read-mostly relocation table descriptor protected by `pil_reloc_lock`.
- `qcom_pil_info_init()` lazily finds the `qcom,pil-reloc-info` node, maps its first resource, clears the region, and computes the number of fixed-size entries.
- `qcom_pil_info_store()` finds an existing matching image slot or the first empty packed slot, writes the name if new, then writes base low/high and size using 32-bit writes.
- `pil_reloc_exit()` unmaps the region at module unload.

## Control flow

The first store call locks the mutex and initializes the IMEM mapping if needed. Initialization is skipped on later calls if `_reloc.base` is already set. Store scans entries in order; an empty first byte terminates the packed list and becomes the new slot, while a matching first 8 bytes updates an existing slot. If all entries are occupied, it warns and returns `-ENOMEM`. Base is written with two `writel()` operations because odd entries may only be 4-byte aligned for the 64-bit field.

## State and persistence behavior

The IMEM table is persistent hardware/shared-memory state used outside this driver for crash analysis. The driver clears the entire region on first initialization, so previous bootloader or earlier-kernel records are discarded. `_reloc.base` and `_reloc.num_entries` persist until module exit; individual entries persist until overwritten or the IMEM region is cleared on the next initialization/reset.

## Dependencies and integration points

The file depends on DT address translation, IO mapping/accessors, mutexes, and the local `qcom_pil_info.h` declaration. Qualcomm remoteproc/PIL loaders are expected to call `qcom_pil_info_store()` after placing firmware images.

## Risks and edge cases

- Image names are truncated to 8 bytes and compared over exactly 8 bytes, so names sharing the same prefix collide intentionally or accidentally.
- If no `qcom,pil-reloc-info` node exists, store returns `-ENOENT`; callers must treat this as optional on platforms without the feature.
- `pil_reloc_exit()` calls `iounmap(_reloc.base)` without checking for NULL; this is generally tolerated but depends on architecture implementation.
- The table is cleared at first init even if some firmware had already populated entries before Linux.
- Entry count truncates resource size to a whole number of entries; trailing bytes are ignored.

## Test signals

Tests should cover missing DT node, invalid resource, ioremap failure, first store clearing and writing, update of an existing 8-byte name, name truncation collisions, full table exhaustion, odd-entry base alignment, concurrent stores under the mutex, and module exit after no successful init.
