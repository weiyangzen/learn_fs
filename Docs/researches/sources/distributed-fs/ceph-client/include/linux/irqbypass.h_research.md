# sources/distributed-fs/ceph-client/include/linux/irqbypass.h

## Purpose
`irqbypass.h` declares the IRQ bypass manager used to pair interrupt producers, such as assigned physical-device IRQs, with consumers, such as virtualization hardware, using a shared `eventfd_ctx` so delivery can be offloaded or bypass host handling.

## Important APIs, types, and functions
Core types are `struct irq_bypass_producer` and `struct irq_bypass_consumer`, with eventfd, peer pointer, callbacks for add/delete, and optional stop/start hooks. APIs are producer and consumer register/unregister functions.

## Control flow
Producers and consumers register independently. The manager matches unique eventfds, quiesces each side with `stop`, connects them through add callbacks, then restarts them. Unregistering reverses this through delete callbacks.

## State and persistence
State is runtime pairing metadata in registered producer/consumer structures and manager lists. No persistent state exists.

## Dependencies and integration points
It depends on list infrastructure and `eventfd_ctx`, and integrates with KVM/VFIO/MSI interrupt paths.

## Risks and test signals
Risks include non-unique eventfds, callback ordering failures, unregister races, and stale peer pointers. Tests should cover register order permutations, add callback failure, unregister while paired, duplicate eventfds, and stop/start ordering under concurrent VM/device teardown.
