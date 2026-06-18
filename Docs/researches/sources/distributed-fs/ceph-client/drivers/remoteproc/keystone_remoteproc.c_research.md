# sources/distributed-fs/ceph-client/drivers/remoteproc/keystone_remoteproc.c

## Purpose

`keystone_remoteproc.c` controls TI Keystone C66x DSP remote processors. It maps internal L2/L1 memories, programs a boot address through a device-control syscon, manages DSP reset, handles vring and exception interrupts, uses a GPIO-backed kick mechanism, and registers the DSP with the remoteproc core.

## Important APIs, types, and functions

- `struct keystone_rproc_mem` describes internal DSP memory with CPU mapping, bus address, DSP device address, and size.
- `struct keystone_rproc` stores device/rproc pointers, memory table, syscon/reg offset, reset control, IRQs, kick GPIO, and work item.
- `keystone_rproc_dsp_boot()` validates 1 KiB boot-address alignment, writes the boot register, and deasserts reset.
- `keystone_rproc_exception_interrupt()` reports `RPROC_FATAL_ERROR`.
- `handle_event()` services vqid 0 and 1 because the vring interrupt has no payload.
- `keystone_rproc_start()` initializes work, enables vring/exception IRQs, and boots from `rproc->bootaddr`.
- `keystone_rproc_stop()` asserts reset, disables IRQs, and flushes pending vring work.
- `keystone_rproc_kick()` toggles the optional `kick` GPIO.
- `keystone_rproc_da_to_va()` translates both DSP-local addresses and SoC bus addresses for internal memories.
- Probe helpers parse `ti,syscon-dev` and map named memories `l2sram`, `l1pram`, and `l1dram`.

## Control flow

Probe requires DT and an alias id `rprocN`, builds a default firmware name `keystone-dspN-fw`, allocates the rproc, disables IOMMU use, locates the syscon boot register, gets reset, enables runtime PM so memories can be accessed, maps and zeroes internal memories, requests disabled `vring` and `exception` IRQs, obtains the `kick` GPIO, initializes reserved memory if present, forces the DSP into reset if needed, and registers remoteproc.

Start enables IRQs and writes the boot address before reset deassertion. If boot fails, pending work is flushed. Vring interrupts schedule work that services both virtqueues. Exception interrupts immediately report a fatal crash. Stop asserts reset, disables both IRQs, and flushes work. Address translation first treats addresses below `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK` as DSP-view addresses and otherwise compares against SoC bus addresses.

## State and persistence behavior

Driver state includes mapped internal memories, reset state, boot register offset, and IRQ/work state. Internal memories are zeroed at probe and persist while the DSP power domain/runtime PM keeps access enabled. The boot address persists in the syscon register until overwritten. Stop leaves the DSP in reset but does not clear memory.

## Dependencies and integration points

The driver integrates with DT compatibles `ti,k2hk-dsp`, `ti,k2l-dsp`, `ti,k2e-dsp`, and `ti,k2g-dsp`; OF aliases; syscon/regmap; reset controller; runtime PM; reserved memory/CMA; named memory resources; IRQs named `vring` and `exception`; and a `kick` GPIO. Remoteproc and rpmsg clients rely on the fixed two-vring interrupt assumption.

## Risks and edge cases

- The work handler assumes exactly two vrings and no interrupt payload. More vrings would require protocol changes.
- Missing OF alias fails probe because it is used for default firmware naming.
- `gpiod_set_value(kick_gpio, 1)` does not explicitly clear the GPIO; correct operation depends on the GPIO provider/IP block modeling a pulse or interrupt generation on set.
- `keystone_rproc_da_to_va()` uses `da < KEYSTONE_RPROC_LOCAL_ADDRESS_MASK`; the mask boundary itself falls into the bus-address path.
- The driver zeroes internal memories at probe, which is useful for clean boot but may destroy diagnostics if probing an already-running or crashed DSP were ever attempted.

## Test signals

Build with Keystone remoteproc and reset/syscon/GPIO support. DT tests should validate alias ids, syscon argument parsing, memory names, IRQ names, kick GPIO, and reserved memory. Runtime tests should check boot address alignment rejection, reset assert/deassert, vring interrupt scheduling, fatal exception recovery, local and bus address translation, memory zeroing, and repeated start/stop with pending work.
