# sources/distributed-fs/ceph-client/arch/mips/rb532/setup.c

Purpose: RB532 platform setup, restart/halt hooks, PCI register mapping, and system type reporting.

Important APIs and control flow: `plat_mem_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`, sets KSEG1 I/O base, maps PCI registers, clears a PCI control bit, optionally unmasks EPLD PCI interrupts, and clears wired TLB entries. `rb_machine_restart()` writes the reset register and jumps to the boot ROM vector. `get_system_type()` reports RB532A or RB532 from `mips_machtype`.

State, persistence, and integration: state includes exported `pci_reg`, global reboot hooks, and PCI controller register programming. Dependencies include PROM board detection, rc32434 PCI/EPLD symbols, and MIPS boot setup. Risks include a likely mask constant typo (`0xFFFFFF7`), halt as a tight loop, no recovery on PCI mapping failure beyond logging, and direct ROM jump reset. Test signals are PCI availability, reboot behavior, and correct `/proc/cpuinfo` machine string.
