# sources/distributed-fs/ceph-client/drivers/counter/Makefile

## Purpose
This Makefile maps Counter subsystem Kconfig symbols to core and driver objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_COUNTER) += counter.o` builds the composite Counter core, with `counter-y := counter-core.o counter-sysfs.o counter-chrdev.o`. Individual driver mappings include `i8254.o`, `104-quad-8.o`, `interrupt-cnt.o`, `rz-mtu3-cnt.o`, `stm32-timer-cnt.o`, `stm32-lptimer-cnt.o`, `ti-eqep.o`, `ftm-quaddec.o`, `microchip-tcb-capture.o`, `intel-qep.o`, and `ti-ecap-capture.o`.

## Control Flow
Kbuild links the core composite object when `CONFIG_COUNTER` is enabled and includes driver objects according to their config symbols. `counter.o` combines core, sysfs, and character-device support.

## State And Persistence
No runtime state exists. The file controls compilation and linkage only.

## Dependencies And Integration Points
It depends on symbols declared in `Kconfig` and source files in the same directory. `104-quad-8.o` corresponds to the `CONFIG_104_QUAD_8` driver.

## Risks And Edge Cases
Adding or renaming drivers requires keeping Kconfig, Makefile, and help-text module names synchronized. The core object composition means sysfs and chrdev support are always linked with `CONFIG_COUNTER`.

## Test Signals
Build tests should verify object inclusion for each config symbol, module names, and the composite contents of `counter.o`.
