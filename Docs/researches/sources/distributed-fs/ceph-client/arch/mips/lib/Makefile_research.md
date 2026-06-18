# sources/distributed-fs/ceph-client/arch/mips/lib/Makefile

Purpose: selects MIPS-specific library objects for bit operations, checksum, delay, memory/string operations, atomic IRQ helpers, IO mapping, TLB dump support, and libgcc-style compiler intrinsics.

Important APIs/types/functions: builds `bitops.o`, `csum_partial.o`, `delay.o`, `memcpy.o`, `memset.o`, `mips-atomic.o`, `strncpy_user.o`, `strnlen_user.o`, `uncached.o`, `iomap_copy.o`, optional `iomap-pci.o`, `dump_tlb.o`, `r3k_dump_tlb.o`, and `bswapsi.o/bswapdi.o/multi3.o`.

Control flow: `CONFIG_GENERIC_CSUM` filters out assembly checksum; CPU/config symbols select PCI and TLB dump variants.

State and persistence: build-system only.

Dependencies and integration: feeds core kernel architecture library symbols and compiler runtime helpers.

Risks: wrong object selection can duplicate or omit fundamental symbols such as `memcpy`, checksum, or TLB dump routines.

Test signals: architecture build/link, boot smoke tests, network checksum tests, user-copy tests, and config matrix builds.
