# sources/distributed-fs/ceph-client/drivers/usb/early/ehci-dbgp.c

Purpose: implements a standalone EHCI debug-port early console and optional KGDB transport that can print over a USB debug device before normal USB host/device drivers are running.

Important APIs/functions: `early_dbgp_init` locates and initializes the EHCI debug port; `early_dbgp_console` provides the console write callback; `dbgp_reset_prep` and `dbgp_external_startup` integrate with later USB HCD reset/startup; KGDB support adds `kgdbdbgp_parse_config`, read/write callbacks, and a polling thread. Internal helpers scan PCI capabilities, map MMIO with fixmap, perform BIOS handoff, reset/start EHCI, wait/reset ports, issue debug-port control/bulk transfers, and handle vendor debug-port remapping.

Control flow: boot parameter parsing checks early PCI access, finds an EHCI controller with the debug capability, maps BAR0, computes capability/register/debug-port addresses, performs BIOS handoff, optionally remaps NVIDIA debug port selection, starts/reset EHCI, waits for a debug device, claims the debug port, enumerates the USB debug descriptor, assigns address 127, enables debug mode, and sends an initial sync write. Console writes split output into 8-byte packets, inject carriage returns before newlines, recover if EHCI stopped, and call debug bulk writes.

State and persistence: global static pointers track EHCI caps, operational regs, and debug regs. Other global state stores physical debug port, unsafe flag, IN/OUT endpoint numbers, and selected PCI device. KGDB state holds an 8-byte read buffer and polling controls. State persists from early boot into later USB handoff when `keep` or KGDB modes require it.

Dependencies and integration: uses early PCI direct access, fixmap, MMIO accessors, EHCI register definitions, USB control definitions, console infrastructure, optional KGDB, kthreads, and Xen debug hooks. It intentionally avoids relying on the normal USB stack for early output.

Risks: direct hardware ownership can conflict with BIOS or later EHCI HCD if handoff/reset sequencing is wrong. The code supports only simple 32-bit BAR0 debug ports. Unplug or timeouts set `dbgp_not_safe` to avoid hangs. Transfer loops are polling and can delay boot. The debug device must support the EHCI debug descriptor and tiny max packet size. Reset paths must release ownership unless the early console or KGDB still needs it.

Test signals: the source comment lists required boot cases: `earlyprintk=dbgp`, `earlyprintk=dbgp,keep`, `earlyprintk=dbgp console=ttyUSB0`, and combined VGA/dbgp modes, with EHCI HCD built in or absent. Additional signals are KGDB over dbgp, successful late HCD handoff, no boot hangs on unplug, and continued output across controller reset when `keep` is used.
