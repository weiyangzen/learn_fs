# sources/distributed-fs/ceph-client/drivers/watchdog/cpwd.c

## Purpose
`cpwd.c` drives the three hardware watchdog timers on Sun CP1400/CP1500 boards. It provides Solaris-compatible miscdevice interfaces for RIC, XIR, and POR watchdogs and handles a known CP1400 PLD interrupt-mask defect.

## Important APIs, types, and functions
`struct cpwd` holds the shared MMIO base, IRQ, options-derived policy, broken-PLD flag, and three subdevice descriptors. Important helpers include `cpwd_toggleintr`, `cpwd_starttimer`, `cpwd_stoptimer`, `cpwd_pingtimer`, `cpwd_getstatus`, `cpwd_brokentimer`, and `cpwd_interrupt`. User APIs are the `cpwd_fops` file operations and ioctls including Linux `WDIOC_*` and SPARC watchdog `WIOC*` commands.

## Control Flow
Probe maps the Open Firmware watchdog node, reads `/options` properties, detects the defective board model, registers three misc devices, and optionally initializes a timer workaround. The first open registers the shared IRQ. Writes and keepalive ioctls reload a selected timer by reading its downcounter. Start writes the limit register and enables interrupts; stop masks interrupt delivery or enters broken-stop maintenance.

## State and Persistence
Global `cpwd_device`, per-subdevice runstatus bits, default timeouts, IRQ registration state, and a workaround timer form runtime state. Firmware option properties influence default behavior but are not modified. The PLD counters and interrupt masks persist until reprogrammed or reset.

## Dependencies and Integration Points
The driver depends on SPARC/Open Firmware resources, `asm/watchdog.h` Solaris ioctl definitions, miscdevice registration, shared IRQ handling, timers, and endian-aware MMIO access.

## Risks and Test Signals
Risks include incorrect minor-to-index mapping in writes, global singleton lifetime, IRQ registration on first open, broken PLD rescheduling, and legacy ioctl compatibility. Tests should cover all three minors, CP1400 broken model behavior, `/options` combinations, interrupt service marking, compat ioctls, and unload with running/stopped timers.
