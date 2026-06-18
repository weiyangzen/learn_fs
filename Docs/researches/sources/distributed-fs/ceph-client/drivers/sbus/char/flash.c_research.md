# sources/distributed-fs/ceph-client/drivers/sbus/char/flash.c

Purpose: exposes UltraSPARC OpenBoot PROM flash memory through a misc device named `flash`, allowing read access and noncached mmap access for firmware update tools.

Important APIs/types/functions: global `flash` stores physical read/write bases, sizes, and a busy flag. File operations are `flash_open()`, `flash_release()`, `flash_llseek()`, `flash_read()`, and `flash_mmap()`. `flash_probe()` validates the parent bus node, records resource ranges, and registers misc minor `SBUS_FLASH_MINOR`.

Control flow: probe accepts flash nodes under `sbus`, `sbi`, or `ebus`, then sets separate read/write mappings if a second resource exists. Only one opener is allowed through a busy bit. Reads use `upa_readb()` from the read physical base. `mmap()` selects the read or write physical range depending on VMA flags when the ranges differ, rejects simultaneous read/write mappings in that case, marks the mapping noncached, and remaps PFNs into userspace.

State and persistence: the driver stores global physical ranges and busy state. The actual persistent state is OBP flash hardware, but this file performs no direct write operation; writing is expected through mapped flash-specific update sequences.

Dependencies and integration: depends on SPARC OF platform resources, miscdevice registration, UPA/MMIO helpers, Linux VM remapping, and `asm/upa.h`. The matching node name is `flashprom`.

Risks and test signals: `flash_mmap()` size calculation appears suspicious because it adjusts `size` to the requested mapping length when the request exceeds the resource, rather than clamping to remaining resource bytes. Read path does not guard negative/out-of-range `*ppos` beyond unsigned arithmetic effects. Busy state uses both mutex and spinlock on the same word. Test open exclusivity, resource combinations with shared/separate read/write bases, read at EOF and beyond EOF, mmap read-only/write-only/read-write cases, pgoff near range end, unsupported parent nodes, and misc registration failure.
