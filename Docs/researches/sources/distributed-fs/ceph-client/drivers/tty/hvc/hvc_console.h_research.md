# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.h

## Purpose
`hvc_console.h` is the shared contract between the generic HVC core and low-level hypervisor console backends. It declares the maximum early-console/tty adapter counts, the `hvc_struct` runtime object, the `hv_ops` backend callback table, and the exported HVC lifecycle and notifier APIs.

## Important APIs, Types, and Functions
`struct hvc_struct` embeds `struct tty_port`, per-device spinlock, tty index, virtual terminal number, backend ops/data, IRQ-requested state, output buffer metadata, current window size, resize work, list linkage, backend flags, and flexible `outbuf[]`.

`struct hv_ops` is the main transport interface. Required operations are usually `get_chars()` and `put_chars()`. Optional operations are `flush()`, `notifier_add()`, `notifier_del()`, `notifier_hangup()`, `tiocmget()`, `tiocmset()`, and `dtr_rts()`. The exported allocation path is `hvc_instantiate()` for early console registration and `hvc_alloc()`/`hvc_remove()` for tty runtime.

The inline `hvc_resize()` acquires `hp->lock` and delegates to `__hvc_resize()`. IRQ-based transports can reuse `notifier_add_irq()`, `notifier_del_irq()`, and `notifier_hangup_irq()`.

## Control Flow
Backends include this header, define one or more `hv_ops` instances, optionally instantiate an early console slot, and allocate runtime HVC devices when their platform bus probes. For resize events, backends call `hvc_resize()` or `__hvc_resize()` depending on whether they already hold `hp->lock`.

## State and Persistence Behavior
The header defines in-memory state only. `MAX_NR_HVC_CONSOLES` is the number of first-stage console adapters, while `HVC_ALLOC_TTY_ADAPTERS` is the tty driver allocation count for hotplug-capable devices.

## Dependencies and Integration Points
It depends on tty, kref, spinlock, and optional xmon headers. It is consumed by all HVC backends in this directory and by the generic core.

## Risks and Edge Cases
Backend implementers must obey locking expectations: several callbacks are called while HVC locks are held, `__hvc_resize()` requires `hp->lock`, and notifier callbacks run during tty open/close/hangup. `HVC_ALLOC_TTY_ADAPTERS` is smaller than `MAX_NR_HVC_CONSOLES`, which is an unusual contract inherited by the core and platform drivers.

## Test Signals
Build coverage for every backend is the main signal. Runtime signs include correct tty index assignment, correct modem-control passthrough when optional callbacks exist, and successful IRQ notifier use by backends that pass a real IRQ number.
