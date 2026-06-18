# sources/distributed-fs/ceph-client/arch/mips/dec/tc.c

Purpose: provides DECstation TurboChannel bus callbacks.

Important APIs: `tc_preadb()` performs protected byte reads with `get_dbe()`; `tc_bus_get_info()` fills `struct tc_bus` from REX TC info and slot address; `tc_device_get_irq()` maps TC slot numbers to `dec_interrupt[]` entries.

Control flow and state: bus info is available only if `dec_tc_bus` was set by PROM identification. Slot count and extended slot geometry depend on `mips_machtype`. IRQ assignment switches on slot number, with DS5000/200 onboard slot quirks for slots 5 and 6.

Dependencies and integration: depends on REX PROM callbacks, DEC machine type, protected access helpers, and global IRQ mapping from setup.

Risks and test signals: protected reads must correctly survive empty slots. Test TC bus enumeration, option ROM reads, and IRQ assignment for TC slots on 3max/3min/maxine/3max+ systems.
