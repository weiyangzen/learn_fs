# sources/distributed-fs/ceph-client/drivers/char/tlclk.c

## Purpose
`tlclk.c` implements the telecom clock driver for Intel NetStructure MPCBL0010 ATCA hardware. It exposes a single-reader misc device `/dev/telco_clock` for alarm event structures and a sysfs interface for reading status and programming clock selection, output enables, reset, filtering, reference alignment, and hardware switching.

## Important APIs, Types, and Functions
- `struct tlclk_alarms` is the user-visible event counter block returned by reads.
- I/O registers are fixed at `TLCLK_BASE` through `TLCLK_REG7`, with `SET_PORT_BITS()` used for read-modify-write updates.
- `tlclk_open()` enforces single use with `useflags`, clears pending events, and requests the hardware IRQ read from `TLCLK_REG7`.
- `tlclk_read()` waits for `got_event`, copies `alarm_events` to userspace, clears it, and resets `got_event`.
- Sysfs show methods expose `current_ref`, `telclock_version`, and `alarms`.
- Numerous store methods parse hex input with `sscanf()` and update register bitfields for received references, clock outputs, AMC transmit clock selection, redundant clock, reference frequency, filters, hardware switching, mode select, refalign, and reset.
- `tlclk_interrupt()` reads and clears interrupt causes, updates alarm counters, switches reference selection on clock-back events, and either wakes readers or starts a short switchover timer.
- `switchover_timeout()` detects primary/secondary switchover after holdover and wakes readers.
- `tlclk_init()` reserves I/O ports, registers char and misc devices, creates a faux device with sysfs groups, and initializes the timer.

## Control Flow
Init reads the IRQ nibble, allocates alarm storage, registers a char major and misc device, reserves the fixed 8-port range, rejects non-MPCBL0010 hardware signaled by IRQ `0x0f`, and creates sysfs attributes. Opening the misc device requests the IRQ. Interrupts update counters under `event_lock`; holdover starts a 10 ms timer to classify switchover, while other events wake readers immediately. Reads block until an event and then consume accumulated counters.

## State and Persistence
State includes fixed hardware registers, allocated `alarm_events`, `int_events`, `got_event`, `useflags`, IRQ number, timer data, wait queue, and sysfs device. Hardware configuration written through sysfs persists in device registers until changed or reset by hardware. Alarm counters are cleared after each successful read.

## Dependencies and Integration Points
The file depends on raw I/O ports, a BIOS-provided IRQ value, interrupt handling, timers, misc and char device registration, faux devices for sysfs, wait queues, and userspace consuming `struct tlclk_alarms`.

## Risks
- Fixed I/O base and hardware-specific IRQ assumptions make the driver unsafe outside its target platform.
- Sysfs store methods do not validate `sscanf()` success or restrict values beyond local switch handling.
- `tlclk_read()` uses `wait_event_interruptible()` but does not check its return before copying, so signals may not be propagated as expected.
- `alarm_events` is updated from interrupt/timer contexts and read under `tlclk_mutex`; timer path does not take `event_lock`.
- The driver registers both a char major and a misc device with the same fops, which is unusual and can complicate ABI expectations.

## Test Signals
Tests should verify non-target IRQ rejection, I/O region conflict handling, single-open `-EBUSY`, IRQ request/free lifecycle, sysfs attribute creation and register bit updates, alarm counter increments for every interrupt mask, holdover switchover timer behavior, blocking read wakeup, and cleanup deleting timer, sysfs device, misc device, char major, and I/O region.
