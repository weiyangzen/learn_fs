# sources/distributed-fs/ceph-client/drivers/input/misc/ab8500-ponkey.c

## Purpose

This platform child driver reports the ST-Ericsson AB8500 power-on key as `KEY_POWER`. It uses separate falling and rising transition IRQs from the AB8500 MFD parent to report press and release.

## Important APIs, Types, and Functions

`struct ab8500_ponkey` stores input, parent AB8500 pointer, falling IRQ, and rising IRQ. `ab8500_ponkey_handler()` compares the IRQ number with `irq_dbf` and `irq_dbr` to report true or false. `ab8500_ponkey_probe()` obtains named IRQs `ONKEY_DBF` and `ONKEY_DBR`, allocates input/state, requests both IRQs using `devm_request_any_context_irq()`, and registers input. OF matching uses `stericsson,ab8500-ponkey`.

## Control Flow

Probe is invoked for an AB8500 MFD child. It gets both transition IRQs by name, allocates an input device named `AB8500 POn(PowerOn) Key`, marks `KEY_POWER`, requests both IRQ lines, and registers input. Each IRQ directly maps to one key state and syncs input.

## State and Persistence Behavior

The driver does not cache key state; the active state is inferred from the IRQ source. Resources are devm-managed. There are no local PM hooks or wakeup calls in this file.

## Dependencies and Integration Points

It depends on the AB8500 MFD core for parent data and named IRQs, platform devices, input key events, and optional OF binding. It can run in hard or threaded context depending on `devm_request_any_context_irq()`.

## Risks and Edge Cases

If IRQ names are swapped or only one transition is present, key state becomes stuck or probe fails. The handler ignores unexpected IRQ numbers but still syncs. There is no explicit wakeup setup, so power-key wake behavior must be handled by AB8500 core/IRQ configuration. Parent pointer is used only for logging after allocation.

## Test Signals

Test both transition IRQs, missing named IRQs, press/release ordering, unexpected IRQ invocation, input registration failure, OF/platform matching, suspend wake behavior through the parent MFD, and repeated bounce events.
