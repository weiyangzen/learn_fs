# sources/distributed-fs/ceph-client/arch/s390/kernel/os_info.c

Purpose: maintains the page-aligned s390 OS info block used by firmware/crash kernels to discover kernel layout, crashkernel state, vmcoreinfo, and reipl data from lowcore.

Important APIs and state: static `os_info` is one page. `os_info_csum()` checksums the version-to-end range. Writers include `os_info_crashkernel_add()`, `os_info_entry_add_data()`, `os_info_entry_add_val()`, and `os_info_init()`. Under `CONFIG_CRASH_DUMP`, `os_info_old_entry()` lazily copies and validates entries from old memory.

Control flow: init fills magic/version, identity/KASLR/vmemmap/amode31/image addresses, computes checksum, and writes the physical OS info pointer into absolute lowcore. Runtime writers update entries and recompute checksum. Crash-dump old-info loading checks oldmem availability or dump IPL type, reads old lowcore pointer, validates alignment, magic, checksum, and version, then copies selected entries with per-entry checksums.

Dependencies and integration: used by IPL/reipl, kexec crash, vmcoreinfo, lowcore, oldmem access, checksum helpers, physical memory info, and KASLR/layout symbols.

Risks and test signals: checksum, physical-vs-virtual address handling, and alignment are critical for crash kernels. Test normal boot lowcore pointer, crash dump old-info discovery, corrupted checksums, missing oldmem, reipl block persistence, and crashkernel address updates after reserved memory changes.
