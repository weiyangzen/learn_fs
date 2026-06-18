# sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_resource.c

Purpose: Implements 16-bit PCMCIA resource management and driver-facing configuration APIs. It allocates/release I/O ports, memory windows, IRQs, maps card memory pages, accesses configuration registers, enables/disables devices, and offers post-enable Vpp/I/O-width fixups.

Important APIs and functions: Exports `pcmcia_validate_mem()`, `pcmcia_find_mem_region()`, `pcmcia_read_config_byte()`, `pcmcia_write_config_byte()`, `pcmcia_map_mem_page()`, `pcmcia_fixup_iowidth()`, `pcmcia_fixup_vpp()`, `pcmcia_enable_device()`, `pcmcia_request_io()`, `pcmcia_request_irq()`, `pcmcia_request_window()`, `pcmcia_release_window()`, and `pcmcia_disable_device()`. Internal helpers include `alloc_io_space()`, `release_io_space()`, `pcmcia_access_config()`, ISA IRQ probing, and `pcmcia_setup_irq()`.

Control flow: Drivers usually call `pcmcia_loop_config()`, request I/O/window/IRQ resources, then `pcmcia_enable_device()`. I/O allocation asks the socket resource manager for a parent range, requests it, and tracks shared socket windows. Enable sets Vpp, I/O-card/speaker/IRQ flags, writes CIS configuration registers, programs I/O maps, marks configuration locked, and increments socket lock count. Disable releases windows, configuration, I/O, and IRQ. Memory windows choose a free socket window, allocate or use static mapping, call `set_mem_map()`, then return a resource with encoded window id.

State and persistence: Mutates per-device private flags (`_io`, `_irq`, `_locked`, `_win`), shared `config_t` resource arrays/state, socket I/O/window state, `lock_count`, `pcmcia_irq`, and physical socket registers through socket ops. Hardware configuration persists until disabled, card removal, or socket reset.

Dependencies and integration points: Depends on socket resource ops from `pcmcia_rsrc`, low-level CIS memory access, Linux resource management, IRQ APIs, and PCMCIA device flags defined in public headers.

Risks: Resource accounting is shared between multifunction devices and scarce socket windows, making release ordering important. ISA IRQ probing can conflict with platform IRQ policy. Configuration register writes assume valid `config_base/config_regs`. A visible double `mutex_lock(&s->ops_mutex)` in `pcmcia_fixup_iowidth()` should be treated as a deadlock risk unless this source variant has external context explaining it.

Test signals: PCMCIA drivers requesting I/O, IRQ, and memory windows; multifunction cards sharing config; enable/disable cycles; bad resource requests; ISA and PCI IRQ fallback; Vpp and 8-bit I/O fixups; and lockdep around fixup and teardown paths.
