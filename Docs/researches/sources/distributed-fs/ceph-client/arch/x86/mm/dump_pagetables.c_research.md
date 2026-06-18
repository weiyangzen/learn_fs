# sources/distributed-fs/ceph-client/arch/x86/mm/dump_pagetables.c

## Purpose
Walks x86 page tables and formats contiguous ranges with common attributes, optionally checking for writable-and-executable mappings.

## Important APIs, Types, And Functions
Core state is `struct pg_state`; range labels use `struct addr_marker`. Public functions include `ptdump_walk_pgd_level_core()`, `ptdump_walk_pgd_level()`, `ptdump_walk_pgd_level_debugfs()`, `ptdump_walk_user_pgd_level_checkwx()`, and `ptdump_walk_pgd_level_checkwx()`. `pt_dump_init()` fills runtime marker addresses.

## Control Flow
The ptdump walker calls note/effective-protection callbacks for each page-table level. `note_page()` groups ranges until permissions, effective permissions, level, or marker boundaries change, then prints address span, size, attributes, and level. WX checking counts ranges whose effective protection is writable and executable, with a PCI BIOS exception. Debugfs and boot-time callers select init, current, PTI user, or EFI page tables.

## State And Persistence
Most state is per-walk. Static `address_markers[]` is initialized at boot with dynamic address-space boundaries. No page-table entries are modified.

## Dependencies And Integration Points
Uses generic `ptdump_walk_pgd()`, x86 page-table flag definitions, KASAN, EFI, PTI, and architecture virtual-address constants. Debugfs exposure is in `debug_pagetables.c`.

## Risks
Effective permissions across page-table levels are easy to report incorrectly, especially for NX and user/RW inheritance. WX warnings can be noisy or security-sensitive. Marker max-line truncation must not hide important regions unexpectedly.

## Test Signals
Read debugfs dumps, run boot-time WX checks, compare marker ordering on 32/64-bit with KASAN/PTI/EFI/LDT/ESPFIX, verify large-page level labeling, and inject known WX mappings in test kernels.
