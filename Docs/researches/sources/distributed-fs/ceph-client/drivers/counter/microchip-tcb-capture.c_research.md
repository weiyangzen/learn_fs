# sources/distributed-fs/ceph-client/drivers/counter/microchip-tcb-capture.c

Purpose: platform driver for Microchip/Atmel Timer Counter Block capture and optional quadrature decoder modes, exposing count, capture, compare, signal, and event functionality.

Important APIs/types/functions: `struct mchp_tc_data` stores SoC TCB capabilities, syscon regmap, qdec mode, number of channels, and selected channel IDs. Counter callbacks handle function read/write, signal level, action read/write, count read, capture array RA/RB read/write, compare RC read/write, and watch validation. IRQ path includes `mchp_tc_isr()`, `mchp_tc_irq_enable()`, and cleanup actions for IRQ mask and clocks.

Control flow: probe matches the parent TCB node to capability data, obtains parent syscon regmap, reads `reg` channel list, enables per-channel clocks, disables qdec, configures capture mode on channel 0, starts the counter, fills Generic Counter metadata, optionally wires the parent IRQ, and registers. Function writes switch between period capture/increase and quadrature X4; quadrature requires SoC support and channels 0 and 1. ISR reads status and interrupt mask, pushes change-of-state, capture RA/RB, threshold RC, and overflow events on UAPI-defined channels.

State and persistence: hardware registers hold mode, capture/compare values, counter value, and IRQ masks. Driver caches qdec mode and channel selection. Clocks and IRQ enables are devm cleaned up. Configuration is volatile.

Dependencies and integration: depends on AT91 TCB MFD/syscon/regmap, clocks, OF IRQ, `uapi/linux/counter/microchip-tcb-capture.h` event channel constants, and Generic Counter event cdev.

Risks: function/action writes do not use a mutex, so concurrent sysfs access could interleave regmap updates. QDEC mode requires an exact two-channel layout; invalid DT gives runtime `-EINVAL` on function write. Parent match lookup assumes `np->parent` matches a known TCB compatible. Shared TCB channels can conflict with other consumers if DT/resource ownership is wrong.

Test signals: DT with supported TCB parent and channel list, mode switches between increase and quadrature, signal reads reflect TIOA/TIOB, action writes change CMR edge bits, capture/compare sysfs reads/writes hit RA/RB/RC, IRQ events reach userspace for ETRGS/LDRAS/LDRBS/CPCS/COVFS, and invalid QDEC channel layouts fail.
