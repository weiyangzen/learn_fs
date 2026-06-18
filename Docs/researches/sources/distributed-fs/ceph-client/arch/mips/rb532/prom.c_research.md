# sources/distributed-fs/ceph-client/arch/mips/rb532/prom.c

Purpose: RB532 PROM initialization. It parses firmware arguments, determines board variant and CPU frequency, maps DDR registers, and adds RAM to memblock.

Important APIs and control flow: `prom_setup_cmdline()` scans `fw_arg0/fw_arg1` argv, consumes `HZ=` for `idt_cpu_freq`, optionally filters `mem=`, sets `mips_machtype` from the board tag, and appends existing `arcs_cmdline`. `prom_init()` maps DDR registers, derives base and size from register field addresses, calls the command-line setup, and adds RAM excluding a small low and high reserved area.

State, persistence, and integration: state includes exported `idt_cpu_freq`, `mips_machtype`, `arcs_cmdline`, and memblock RAM. Dependencies include firmware tag syntax, rc32434 DDR structures, and later time/UART code using `idt_cpu_freq`. Risks include trusting raw firmware argv pointers, unusual DDR size calculation via register-address interpretation, and returning without memory setup if DDR mapping fails. Test signals are correct board name, CPU clock, command line, and usable RAM range.
