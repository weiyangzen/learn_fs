# sources/distributed-fs/ceph-client/arch/s390/include/asm/os_info.h

Purpose: This header defines the s390 OS-info memory block used to expose crash, re-IPL, KASLR, vmemmap, AMODE31, and image metadata to dump/reboot tooling.

Important APIs/types/functions: `OS_INFO_*` version, magic, entry indexes, `OS_INFO_FLAG_REIPL_CLEAR`, `struct os_info_entry`, `struct os_info`, `os_info_init()`, entry add helpers, `os_info_crashkernel_add()`, `os_info_csum()`, and crash-dump `os_info_old_entry()`/`os_info_old_value()` are exposed.

Control flow: Boot initializes an OS-info block, adds pointer or scalar entries with per-entry checksums, records crashkernel ranges, and crash kernels can query the old block for metadata from the previous kernel.

State and persistence: Persistent state is the packed OS-info block, referenced from lowcore, with checksummed entries and crashkernel address/size fields.

Dependencies and integration points: It depends on Linux uio types, lowcore OS-info pointer conventions, crash dump mode, IPL/re-IPL setup, and KASLR/VM layout producers.

Risks and test signals: Packed layout, magic, version, and checksums are external contracts with dump tools. Tests should include normal boot OS-info population, kdump old-entry reads, checksum validation, KASLR fields, and re-IPL clear flag behavior.
