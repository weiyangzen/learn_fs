# sources/distributed-fs/ceph-client/arch/mips/dec/prom/init.c

Purpose: initializes DEC PROM callback vectors and performs earliest platform discovery.

Important APIs and state: global function pointers include REX callbacks (`__rex_bootinit`, `__rex_getbitmap`, `__rex_getsysid`, etc.), generic PROM callbacks (`__prom_getchar`, `__prom_getenv`, `__prom_printf`), and PMAX file callbacks. `prom_init()` is the architecture firmware entry point.

Control flow: `which_prom()` checks the REX magic and either copies callbacks from the PROM vector or installs fixed PMAX PROM addresses. `prom_init()` optionally clears cache through REX, registers the PROM console, validates CPU type against kernel config, initializes memory, identifies architecture, and builds command line.

State and integration: PROM function pointers persist for init-time users. CPU mismatch paths halt through `dec_machine_halt()`.

Risks and test signals: wrong PROM vector interpretation breaks all early services. Test REX and non-REX boot paths, early console output, CPU config mismatch handling, memory map creation, and command-line import.
