# sources/distributed-fs/ceph-client/drivers/remoteproc/ingenic_rproc.c

## Purpose

`ingenic_rproc.c` is a compact remoteproc driver for the Ingenic JZ4770 VPU auxiliary processor. It maps VPU TCSM/SRAM memories, controls VPU/AUX clocks, starts and resets the AUX interface, and uses AUX message registers for virtqueue kicks and interrupts.

## Important APIs, types, and functions

- `auto_boot` is a module parameter that controls `rproc->auto_boot`.
- `struct vpu_mem_map` defines remote device base addresses for `tcsm0`, `tcsm1`, and `sram`.
- `struct vpu_mem_info` stores each mapped resource's table entry, length, and `ioremap` base.
- `struct vpu` stores IRQ, two clocks (`vpu`, `aux`), AUX register base, memory mappings, and device pointer.
- `ingenic_rproc_prepare()` enables clocks before firmware load; `ingenic_rproc_unprepare()` disables them.
- `ingenic_rproc_start()` enables the IRQ and writes AUX reset/NMI/message IRQ bits. `ingenic_rproc_stop()` disables the IRQ and holds AUX in software reset.
- `ingenic_rproc_kick()` writes the virtqueue id to `REG_CORE_MSG`.
- `ingenic_rproc_da_to_va()` maps remote addresses into the three memory regions.
- `vpu_interrupt()` reads `REG_AUX_MSG`, acknowledges with `REG_AUX_MSG_ACK`, and calls `rproc_vq_interrupt()`.

## Control flow

Probe allocates the rproc, stores `auto_boot`, maps the `aux` register bank, maps `tcsm0`, `tcsm1`, and `sram`, gets `vpu`/`aux` clocks, requests an initially disabled IRQ, and registers remoteproc. Prepare enables clocks so the loader can access TCSM. Start enables the IRQ and releases AUX with NMI reset semantics and message IRQs enabled. Kicks write to the core message register. Interrupts read the remote-provided vring id and pass it to remoteproc. Stop disables the IRQ and puts AUX back into reset.

## State and persistence behavior

Software state is limited to mapped memory descriptors and clock/IRQ handles. Hardware state persists in AUX control/message registers and memory contents while clocks and reset state allow access. Stop leaves AUX held in reset; unprepare turns clocks off after remoteproc no longer needs memory access.

## Dependencies and integration points

The driver uses platform resources named `aux`, `tcsm0`, `tcsm1`, and `sram`, two clocks named `vpu` and `aux`, a single IRQ, and the compatible `ingenic,jz4770-vpu-rproc`. It depends on remoteproc core, IRQ, clock, IO mapping, and `remoteproc_internal.h`.

## Risks and edge cases

- The address check uses `(da + len) < end`, so a buffer ending exactly at the region end is rejected.
- `platform_get_resource_byname()` is not checked before `devm_ioremap_resource()`, so missing named resources depend on that helper's error behavior.
- The IRQ payload is trusted as the vring id; unexpected values rely on `rproc_vq_interrupt()` handling.
- There is no custom firmware sanity/load path, so firmware must match the generic remoteproc expectations and the fixed memory map.

## Test signals

Build with Ingenic remoteproc enabled. DT tests should verify all resources/clocks/IRQ names. Runtime tests should cover `auto_boot`, firmware load into each mapped region, exact-end address translation, virtqueue kick/interrupt exchange, clock enable/disable around prepare/unprepare, and repeated start/stop leaving AUX reset asserted.
