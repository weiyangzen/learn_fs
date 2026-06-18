# sources/distributed-fs/ceph-client/include/linux/irqreturn.h

## Purpose
`irqreturn.h` defines standard return values for interrupt handlers.

## Important APIs, types, and functions
It defines `enum irqreturn` values `IRQ_NONE`, `IRQ_HANDLED`, and `IRQ_WAKE_THREAD`, typedefs `irqreturn_t`, and provides `IRQ_RETVAL(x)`.

## Control flow
Primary IRQ handlers return these values so the IRQ core can update spurious-interrupt accounting and optionally wake a threaded handler.

## State and persistence
No state exists in the header.

## Dependencies and integration points
It is used by virtually all drivers registering interrupt handlers and by IRQ core action dispatch.

## Risks and test signals
Risks include returning `IRQ_HANDLED` for unrelated shared IRQs, forgetting `IRQ_WAKE_THREAD`, and boolean conversion hiding nuanced outcomes. Tests should cover shared IRQ behavior, threaded IRQ wakeups, spurious interrupt detection, and driver error paths.
