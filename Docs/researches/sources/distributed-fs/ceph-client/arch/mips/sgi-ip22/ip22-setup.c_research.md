# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-setup.c

Purpose: top-level IP22 memory/platform setup. It wires bus-error handling, initializes HPC and MC hardware, configures EISA I/O ports, and chooses the preferred console from ARCS variables.

Important APIs and control flow: `plat_mem_setup()` sets `board_be_init`, calls `sgihpc_init()` before `sgimc_init()`, optionally enables board cache, maps the EISA I/O port window, reads `console`, `ConsoleOut`, and `dbaud` ARCS variables, then selects ttyS or ARC console behavior.

State, persistence, and integration: state includes global platform hardware mappings, console preference, and `prom_flags`. Dependencies include ARCS firmware variables, SGI memory/HPC init ordering, and MIPS console setup. Risks include a fixed huge I/O remap range, reliance on firmware strings, and console selection corner cases when graphics lacks keyboard. Test signals are correct early console, successful MC/HPC logs, and boot on Indy/Indigo2 variants.
