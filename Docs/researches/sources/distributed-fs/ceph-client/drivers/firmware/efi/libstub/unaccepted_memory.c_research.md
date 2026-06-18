
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/unaccepted_memory.c

Purpose: creates and maintains the Linux EFI unaccepted-memory bitmap used by confidential-computing guests to defer memory acceptance until first use.

Important APIs/types/functions: exports `allocate_unaccepted_bitmap()`, `process_unaccepted_memory()`, and `accept_memory()`. Uses global `struct efi_unaccepted_memory *unaccepted_table`.

Control flow: allocation checks for an existing table, scans EFI memory descriptors for `EFI_UNACCEPTED_MEMORY`, computes the aligned covered physical range and bitmap size, allocates ACPI reclaim memory, initializes version/base/unit/size, and installs `LINUX_EFI_UNACCEPTED_MEM_TABLE_GUID`. Processing accepts too-small or unaligned edge pieces immediately, clamps to bitmap coverage, accepts out-of-bitmap ranges, and marks aligned 2 MiB units. Later `accept_memory()` maps a physical range to bitmap bits, calls `arch_accept_memory()` for set ranges, and clears those bits.

State and persistence behavior: the unaccepted table and bitmap persist into kernel boot through an EFI configuration table. Bitmap bits are mutable and track unaccepted ranges until accepted.

Dependencies and integration points: depends on EFI unaccepted memory descriptor type, bitmap helpers, architecture `arch_accept_memory()`, and x86 e820 setup calling `process_unaccepted_memory()`.

Risks and test signals: granularity can force immediate acceptance of small/unaligned ranges, and bitmap sizing must not under-cover high physical holes. Test signals include no-unaccepted-memory boot, preinstalled table version check, unaligned start/end ranges, ranges below/above bitmap coverage, repeated acceptance clearing bits, and SEV/TDX guest boots.
