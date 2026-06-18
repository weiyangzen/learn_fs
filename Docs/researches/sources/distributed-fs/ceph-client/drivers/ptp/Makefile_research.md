# sources/distributed-fs/ceph-client/drivers/ptp/Makefile Research

## Purpose
The PTP Makefile maps Kconfig symbols to built objects for the PTP framework and its PHC drivers.

## Important APIs, Types, And Functions
`ptp-y` builds the common `ptp` module from `ptp_clock.o`, `ptp_chardev.o`, `ptp_sysfs.o`, and `ptp_vclock.o`. `ptp_kvm-*` selects architecture-specific KVM PTP pieces. Object assignments connect symbols to drivers including `ptp_dte.o`, `ptp_clockmatrix.o`, `ptp_fc3.o`, `ptp_idt82p33.o`, and `ptp_dfl_tod.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries based on `.config`. If `PTP_1588_CLOCK=m`, `ptp-y` is linked into `ptp.ko`; if built in, it becomes part of vmlinux. Hardware driver objects follow their own tristate settings.

## State And Persistence
The Makefile has no runtime state. Its output persists as built modules or built-in objects in the kernel build tree.

## Dependencies And Integration Points
It is tightly coupled to `drivers/ptp/Kconfig` symbol names and source filenames. It also relies on Kbuild composite-object naming, especially for `ptp-y` and `ptp_kvm-*`.

## Risks
Missing an object from `ptp-y` can produce partially functional framework builds. A mismatch between Kconfig symbols and Makefile entries makes a selected driver silently not build. Adding a new PTP driver requires updating both files consistently.

## Test Signals
Build tests should cover `PTP_1588_CLOCK=y`, `m`, and disabled, plus module builds for each object in this subset. `make M=drivers/ptp` is a direct signal for missing object or symbol regressions.
