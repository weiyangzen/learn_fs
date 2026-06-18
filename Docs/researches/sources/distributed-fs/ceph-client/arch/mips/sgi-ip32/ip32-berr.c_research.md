# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-berr.c

Purpose: IP32 bus-error exception handling. It installs a fatal MIPS bus-error handler with fixup support.

Important APIs and control flow: `ip32_be_handler()` returns `MIPS_BE_FIXUP` for fixup-capable accesses. Otherwise it logs instruction/data bus-error type and EPC, dumps registers and all TLB entries, then loops forever before the unreachable SIGBUS path. `ip32_be_init()` installs this handler.

State, persistence, and integration: state is the global MIPS bus-error handler set through `board_be_init`. Dependencies include setup assigning `board_be_init = ip32_be_init` and MIPS trap code. Risks include fatal infinite loop for non-fixup errors and minimal CRIME-specific context compared with error IRQ handlers. Test signals are safe exception-table probing and verbose dumps on bad bus access.
