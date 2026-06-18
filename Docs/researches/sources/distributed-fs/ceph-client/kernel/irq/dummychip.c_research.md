# sources/distributed-fs/ceph-client/kernel/irq/dummychip.c

## Purpose
`dummychip.c` defines generic placeholder IRQ chips used when an interrupt has no real controller or is backed by a very simple dummy source. It prevents NULL chip callbacks and provides diagnostic behavior for illegal vectors.

## Important APIs, types, and functions
The file defines `no_irq_chip` and exported `dummy_irq_chip`. Helpers are `ack_bad()`, `noop()`, and `noop_ret()`. Both chips set `IRQCHIP_SKIP_SET_WAKE`.

## Control flow
`no_irq_chip` uses no-op startup/shutdown/enable/disable and an ack path that prints descriptor diagnostics and calls `ack_bad_irq()`. `dummy_irq_chip` uses no-op startup, shutdown, enable, disable, ack, mask, and unmask callbacks. The generic IRQ core installs `no_irq_chip` by default and drivers may use `dummy_irq_chip` for software/simple sources.

## State and persistence
The chip structures are static global runtime objects. They hold no mutable per-IRQ state.

## Dependencies and integration points
This file integrates with descriptor default initialization, bad IRQ handling, and drivers/tests that need a simple chip implementation. It depends on `print_irq_desc()` and architecture `ack_bad_irq()`.

## Risks and test signals
Risks include accidentally leaving production IRQs on `no_irq_chip`, hiding missing hardware operations behind dummy no-ops, and bad-ack diagnostics firing in paths that should have been masked earlier. Test signals include descriptor defaults, bad IRQ injection, dummy-chip request/startup paths, and no wake callback attempts because of `IRQCHIP_SKIP_SET_WAKE`.
