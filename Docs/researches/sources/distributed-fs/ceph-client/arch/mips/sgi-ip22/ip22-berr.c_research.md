# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-berr.c

Purpose: IP22 bus-error handling for Indy/Indigo2. It captures SGI memory-controller, GIO, external I/O, and HPC3 error state, prints diagnostics, and converts fatal errors to SIGBUS or kernel die.

Important APIs and control flow: `save_and_clear_buserr()` snapshots MC/HPC/IOC registers and clears MC status. `print_buserr()` decodes CPU, GIO, HPC3, MC, and EISA error bits. `ip22_be_interrupt()` handles the bus-error IRQ path, logs EPC/RA from current IRQ regs, then calls `die_if_kernel()` and `force_sig(SIGBUS)`. `ip22_be_handler()` supports MIPS fixups and fatal exceptions. `ip22_be_init()` installs the handler.

State, persistence, and integration: state is last-error globals used during one diagnostic path. Dependencies include initialized `sgimc`, `sgioc`, `sgint`, and `hpc3c0`. Risks include destructive register reads, limited recovery, and assuming continuing after most bus errors is unsafe. Test signals are correct registration via `board_be_init`, decoded logs during induced bad PIO access, and successful exception-table fixups.
