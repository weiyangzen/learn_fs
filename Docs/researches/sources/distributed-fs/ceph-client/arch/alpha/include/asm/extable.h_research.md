# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/extable.h

This header defines Alpha exception table entries and fixup behavior. `struct exception_table_entry` stores a PC-relative faulting instruction offset and a packed fixup word containing next-instruction offset, error register, and value register.

The key API is `fixup_exception(map_reg, _fixup, pc)`: it zeros `valreg` unless it is register 31, writes `-EFAULT` to `errreg` unless it is register 31, and returns `pc + nextinsn`. `ARCH_HAS_RELATIVE_EXTABLE` declares relative table entries. `swap_ex_entry_fixup` swaps fixup units during sorting.

State is exception-table metadata consumed by fault handlers and uaccess fixups. Risks are packed bitfield layout, Alpha register numbering, and the assembler emission format described by the comments. Tests include user access fault fixups, exception-table sorting, and sparse/compile checks for `EXC()` users.
