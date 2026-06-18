# sources/distributed-fs/ceph-client/arch/s390/include/asm/physmem_info.h

Purpose: This header defines early physical memory detection metadata, reserved ranges, iterators, and source-name helpers for s390 boot memory setup.

Important APIs/types/functions: `enum physmem_info_source`, `struct physmem_range`, `enum reserved_range_type`, `struct reserved_range`, `struct physmem_info`, global `physmem_info`, `add_physmem_online_range()`, `__get_physmem_range()`, usable/online range iterators, `get_physmem_info_source()`, reserved range iterators, `get_physmem_reserved()`, and `AMODE31_START/END` are defined.

Control flow: Early detection records online ranges from SCLP, DIAG, storage limits, or binary search, tracks reserved ranges for decompressor/initrd/vmlinux/AMODE31/IPL report/cert lists/vmem, and later boot code iterates usable or all online ranges to initialize memory.

State and persistence: Persistent boot state is global `physmem_info`, including inline range storage and optional extended storage carved from known memory. Reserved ranges can chain additional nodes by physical addresses converted with `__va()`.

Dependencies and integration points: It depends on page translation helpers and integrates decompressor/boot memory detection, memblock setup, crash dump reservations, AMODE31, IPL report, certificate lists, and vmemmap allocation.

Risks and test signals: Range truncation at `usable`, chained reserved-range address conversion, and overlap handling are critical. Tests should cover each detection source, more than 255 memory ranges, reserved range iteration, usable limit enforcement, and crash/initrd/IPL report reservations.
