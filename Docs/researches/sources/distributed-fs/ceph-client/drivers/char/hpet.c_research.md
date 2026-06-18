# sources/distributed-fs/ceph-client/drivers/char/hpet.c

## Purpose
This is the legacy `/dev/hpet` character driver for High Precision Event Timer comparators. It discovers HPET blocks via ACPI or platform allocation, exposes timer comparators to userspace, supports interrupt frequency programming, blocking reads/poll/fasync, optional mmap of the HPET page, and a sysctl for maximum unprivileged frequency.

## Important APIs, Types, and Functions
- `struct hpets` represents one HPET block; `struct hpet_dev` represents one comparator.
- `hpet_alloc()` registers an HPET block and initializes comparator devices.
- `hpet_open()`, `hpet_release()`, `hpet_read()`, `hpet_poll()`, `hpet_ioctl()`, `hpet_compat_ioctl()`, and `hpet_fasync()` implement `/dev/hpet`.
- `hpet_ioctl_common()` handles `HPET_IE_ON/OFF`, `HPET_INFO`, `HPET_EPI/DPI`, and `HPET_IRQFREQ`.
- `hpet_interrupt()` accounts interrupts and rearms nonperiodic comparators to emulate periodic behavior.
- `hpet_acpi_probe()` walks `_CRS` resources and calls `hpet_alloc()`.

## Control Flow
`hpet_init()` registers the misc device, `dev/hpet/max-user-freq` sysctl, and ACPI platform driver. ACPI probe maps MMIO and IRQ resources, then allocation verifies timer count, enables the main counter if needed, initializes per-comparator state, and calibrates comparator write latency. An open picks the first unused comparator. Ioctls set frequency, periodic mode, and interrupt enable. On interrupt, the handler increments pending event count, updates comparator state, wakes readers, and signals async listeners.

## State and Persistence Behavior
Global `hpets` is an append-only linked list of discovered HPETs. Per comparator state tracks open/interrupt/periodic/shared-IRQ flags, requested HPET-tick interval, pending interrupt count, IRQ assignment, wait queue, and fasync queue. `hpet_mutex` serializes ioctl/open transitions, while `hpet_lock` protects ISR-shared fields and MMIO programming. HPET hardware comparator configuration persists until release disables it.

## Dependencies and Integration Points
It depends on ACPI `PNP0103`, HPET register definitions, miscdevice minor `HPET_MINOR`, sysctl, wait queues, fasync, compat ioctl support, IRQ routing via ACPI GSI, optional `CONFIG_HPET_MMAP`, and platform code that may call exported `hpet_alloc()`.

## Risks
This exposes MMIO-backed timer programming to userspace, so frequency caps and `CAP_SYS_RESOURCE` checks are important. Shared IRQ handling depends on correct ISR bit clearing. The linked list is not removed on ACPI device removal, and mapped resources are effectively lifetime-long. Mmap is page-alignment dependent and disabled unless configured/boot-enabled.

## Test Signals
Test ACPI resource parsing, duplicate detection, comparator reservation state, open exhaustion, `HPET_IRQFREQ` privilege limits, periodic/nonperiodic interrupt delivery, read size differences under compat, fasync signals, poll readiness, release cleanup, sysctl writes, and optional `hpet_mmap=` boot behavior.
