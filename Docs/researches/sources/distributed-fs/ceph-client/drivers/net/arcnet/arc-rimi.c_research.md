# sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rimi.c

Purpose: hardware driver for ARCNET COM90xx RIM I cards, which are entirely memory-mapped and require explicit module or boot parameters for shared memory, IRQ, and station ID.

Important APIs and functions: `arcrimi_probe()` validates required parameters and reserves a provisional memory window. `check_mirror()` maps candidate memory regions to detect mirrored card memory. `arcrimi_found()` maps the card, requests IRQ, determines mirror range, fills `arcnet_local` hardware callbacks, remaps the final memory span, reads station ID, and registers the netdevice. Hardware callbacks implement reset, interrupt mask, status, command, and memory copies. Module init allocates an ARCNET device and calls probe; exit unregisters and releases mappings, IRQ, and memory.

Control flow: no autoprobe is attempted. Init creates `arc%d` or requested name, applies node/io/irq params, normalizes IRQ 2 to 9, probes, then leaves the registered device to use shared ARCNET core open/interrupt/transmit paths. The reset path performs a fake reset write when requested, otherwise clears reset/config flags and enables extended packets.

State and dependencies: state includes module parameters, global `my_dev`, reserved memory region, `lp->mem_start`, device IRQ, and callbacks in `arcnet_local`. Dependencies are ARCNET core, COM9026 register definitions, MMIO accessors, and legacy boot `__setup` when built-in. Risks include untested hardware path, required manual parameters, mirror probing around physical memory windows, and cleanup correctness after partial failures. Test signals are parameter parsing, memory reservation/remap failures, IRQ request failures, reset/status/command register access, and unload resource release.
