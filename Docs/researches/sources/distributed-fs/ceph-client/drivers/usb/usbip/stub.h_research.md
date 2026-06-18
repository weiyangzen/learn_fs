# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub.h

## Purpose

`stub.h` declares the host-side USB/IP private state shared by `stub_dev.c`, `stub_main.c`, `stub_rx.c`, and `stub_tx.c`. It models exported physical USB devices, in-flight remote URBs, unlink replies, and bus-id selection state.

## Important APIs, Types, and Functions

`struct stub_device` wraps the physical `usb_device`, common `usbip_device`, stable `devid`, URB lifecycle lists (`priv_init`, `priv_tx`, `priv_free`), unlink lists, locks, and TX waitqueue. `struct stub_priv` tracks one remote submit request, possibly split across multiple URBs, with SG state and unlinking status. `struct bus_id_priv` records user-selected bus IDs and binding status. Prototypes expose bus-id lookup, cleanup, RX/TX loops, completion, and unlink response enqueueing.

## Control Flow

The header defines list ownership: submit requests enter `priv_init`, completions move to `priv_tx`, sent completions move to `priv_free`, and cleanup can drain all lists. Unlink requests are queued separately for TX.

## State and Persistence Behavior

State is entirely in memory and tied to module/device lifetime. Bus-id names persist only while the module is loaded and are manipulated through driver sysfs files.

## Dependencies and Integration Points

It depends on USB core, common USB/IP transport definitions, spinlocks, lists, wait queues, and slab allocation. It is the internal ABI for the host export module.

## Risks and Test Signals

Risks include list-state invariants, lock ordering around `priv_lock`, refcount/lifetime bugs for physical devices, and bus-id status transitions. Test signals are compile coverage of all stub objects, export/import attach cycles, unlink races, SG splitting cleanup, and module unload rebind behavior.
