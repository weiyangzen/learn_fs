# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.c

Purpose: udbg console implementation for USB Gecko EXI adapters on GameCube/Wii, including optional very-early debug setup.

Important APIs and control flow: `ug_io_transaction` performs one EXI chip-select/read-write transaction. Probe sends an adapter identify command on memory-card slots A and B. `ug_putc`, `ug_getc`, and poll variants retry FIFO readiness and install `udbg_putc`, `udbg_getc`, and `udbg_getc_poll` when an adapter is present. `ug_udbg_init` maps the OF `nintendo,flipper-exi` node for final udbg. Under early debug, `udbg_init_usbgecko` uses the fixmap BAT area, probes EXI, installs hooks, and programs BAT 1 to preserve access after MMU init.

State, dependencies, and risks: global state is `ug_io_base`. Dependencies include EXI register layout, OF EXI node, fixmap/BAT setup, udbg globals, and platform-specific physical EXI bases. Risks include busy-wait loops, silent transmit drops after retry exhaustion, fragile early mapping assumptions, and bypassing the normal EXI layer. Test signals are early and final console output, input polling, adapter detection in both slots, and continued output after MMU transition.
