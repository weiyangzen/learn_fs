# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.c

## Purpose
Provides the core libata bridge for parallel-port ATA adapters. It owns the `pata_parport` bus, parport discovery, protocol registration, sysfs manual device creation/removal, and ATA SFF operations backed by protocol callbacks.

## Important APIs, Types, And Functions
ATA operations include `pata_parport_dev_select()`, `pata_parport_set_devctl()`, `pata_parport_softreset()`, `pata_parport_tf_load()`, `pata_parport_tf_read()`, `pata_parport_exec_command()`, `pata_parport_data_xfer()`, and `pata_parport_drain_fifo()`. Discovery and lifecycle are handled by `pi_init_one()`, `pi_probe_unit()`, `pi_probe_mode()`, `pi_test_proto()`, `pata_parport_register_driver()`, `pata_parport_unregister_driver()`, `pata_parport_attach()`, `pata_parport_detach()`, `new_device_store()`, and `delete_device_store()`.

## Control Flow
Module init registers a bus, root device, sysfs attributes, and a parport driver. Parport attach records ports in an IDR and optionally probes every registered protocol. Protocol registration records the protocol and optionally probes every known parport. Successful `pi_init_one()` registers a child device, gets a protocol module ref, registers a parport device, probes unit/mode, allocates one ATA host, claims the parport, connects the protocol, and activates a polling SFF ATA host.

## State And Persistence
Global state uses `parport_list`, `protocols`, `pata_parport_bus_dev_ids`, `pata_parport_bus`, and `pi_mutex`. Each `pi_adapter` stores device identity, protocol pointer, port/mode/delay/unit, saved port registers, private protocol data, and `pardev`. The parport is intentionally claimed for the entire ATA host lifetime.

## Dependencies And Integration Points
Integrates libata SFF PIO polling, Linux parport, driver core buses/devices, sysfs bus attributes, IDR/IDA allocation, module refcounting, and protocol modules via exported GPL symbols.

## Risks And Edge Cases
Holding the parport prevents chained devices and printers from sharing it. Device/protocol enumeration is serialized by `pi_mutex`, but removal paths must balance ATA detach, disconnect, parport unregister, module refs, and device refs. Manual `new_device` parsing can scan many combinations. Softreset handles ghosty master/slave behavior where adapters return bogus values.

## Test Signals
Automatic probe on protocol load and parport attach, `probe=0`, sysfs `new_device` and `delete_device`, duplicate protocol/port rejection, master/slave reset, DRQ drain, module unload with active devices, and parport detach while devices exist.
