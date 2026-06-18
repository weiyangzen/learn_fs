# sources/distributed-fs/ceph-client/drivers/bus/moxtet.c

## Purpose

`moxtet.c` implements the Turris MOX module configuration bus over SPI. It discovers the physical module topology, registers a `moxtet` bus and child devices for modules, exposes module identity through sysfs, exports read/write helpers for client drivers, optionally exposes debugfs raw input/output views, and maps module interrupt bits into a nested IRQ domain.

## Important APIs, Types, And Functions

- Bus/driver integration: `moxtet_bus_type`, `__moxtet_register_driver()`, `moxtet_match()`, `moxtet_add_device()`, and child unregister helper.
- Topology/device creation: `moxtet_find_topology()`, `moxtet_set_irq()`, `of_register_moxtet_devices()`, `of_register_moxtet_device()`, and `moxtet_register_devices_from_topology()`.
- Exported device IO: `moxtet_device_read()`, `moxtet_device_write()`, and `moxtet_device_written()`.
- Debugfs: `input_read()`, `output_read()`, `output_write()`, `moxtet_register_debugfs()`, and `moxtet_unregister_debugfs()`.
- IRQ support: `moxtet_irq_domain_map()`, `moxtet_irq_domain_xlate()`, mask/unmask/print callbacks, `moxtet_irq_read()`, `moxtet_irq_thread_fn()`, `moxtet_irq_setup()`, and `moxtet_irq_free()`.
- SPI lifecycle: `moxtet_probe()`, `moxtet_remove()`, `moxtet_init()`, and `moxtet_exit()`.

## Control Flow

Module init registers the `moxtet` bus and the SPI driver. Probe sets up SPI, allocates `struct moxtet`, initializes the mutex, obtains the parent IRQ from device tree, reads topology bytes from SPI, validates the CPU module byte, records downstream module ids until `0xff`, logs known modules, and builds IRQ bit positions for modules with interrupt lines. If interrupts exist, it creates an IRQ domain, maps existing hardware IRQs, initializes all as masked, and requests a shared oneshot threaded parent IRQ.

Child device creation happens from device tree children first and then from discovered topology. DT children use their `reg` index and the discovered module id at that index; topology-created devices fill gaps without DT nodes. Duplicate detection is protected by a static mutex and compares bus instance, module id, and index. Remove frees the parent IRQ, tears down IRQ mappings/domain, removes debugfs, unregisters child devices, and destroys the mutex.

The exported IO helpers lock the bus mutex around SPI operations. Reads return the upper nibble of the module's topology/status byte. Writes store an output value into `tx[count - idx]` and write the whole chain, reflecting shift-register ordering. `moxtet_device_written()` reports the cached output byte for a module.

## State And Persistence Behavior

`struct moxtet` stores discovered module ids, module count, transmit shadow buffer, mutex, parent IRQ, IRQ-domain data, and debugfs root. Each `struct moxtet_device` holds bus pointer, module id, index, and optional OF node. Module metadata is static in `mox_module_table` and order-sensitive because IDs index directly into it. IRQ existence, mask, and hardware positions persist in `moxtet->irq`.

## Dependencies And Integration Points

The driver depends on `dt-bindings/bus/moxtet.h`, `<linux/moxtet.h>`, SPI core, OF device matching, OF IRQ lookup, generic IRQ domains, nested IRQ handling, debugfs, and Linux driver core. Client module drivers bind by OF compatible string or Moxtet module id table and use the exported read/write helpers.

## Risks

`moxtet_remove()` unconditionally calls `free_irq()` and `moxtet_irq_free()` even when no child IRQs existed; probe requires a valid parent IRQ, but `moxtet_irq.domain` may be null if no module advertised IRQ bits. The module table order must never drift from hardware IDs. The SPI output index reversal is easy to break when changing topology handling. IRQ handling repeatedly reads until no unmasked pending bits remain; a stuck asserted module IRQ can keep the threaded handler busy. DT child registration must clear `OF_POPULATED` and drop node refs on all failure/remove paths.

## Test Signals

Expected signals include topology logs for MOX A and downstream modules, child devices named `moxtet-<module>.<idx>`, sysfs module id/name/description, successful binding by OF and id table, debugfs hex input/output matching SPI state, nested IRQs delivered for PCI/Topaz/Peridot/USB3 modules, mask/unmask behavior, duplicate child rejection, and clean remove without OF node leaks or IRQ-domain mappings left behind.
