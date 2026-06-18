# sources/distributed-fs/ceph-client/drivers/comedi/comedi_fops.c

## Purpose

`comedi_fops.c` is the COMEDI core character-device implementation. It owns board and subdevice minor allocation, open/close lifetime, ioctl dispatch, asynchronous command setup/cancel, read/write/poll/mmap behavior, compat ioctl translation, event delivery, sysfs buffer attributes, and module initialization.

## APIs And Flow

`struct comedi_file` tracks per-open device and selected read/write subdevices. Global minor tables map board and subdevice minors. Krefs manage `struct comedi_device` lifetime. Ioctl handlers cover device config, buffer config/info, device/subdevice/channel/range info, instruction execution, async command and command test, locks, cancel, poll, and per-file subdevice selection. `COMEDI_CMD` validates command and chanlist, runs `do_cmdtest`, resets buffers, initializes `run_active`, sets runflags and `s->busy`, then calls low-level `do_cmd()`. `read()`/`write()` use `attach_lock`, async wait queues, buffer helpers, nonblocking/signal handling, and stopped-command cleanup. `mmap()` maps buffer pages and pins map lifetime through VM open/close. `comedi_event()` processes interrupt-set events, wakes waiters, and sends SIGIO.

## State, Dependencies, Risks, Tests

Runtime state includes minor tables, krefs/use counts, file-selected subdevices, locks, busy owner, runflags, async buffer counters, wait queues, fasync queue, sysfs buffer limits, and module parameters. Detach protection uses `attach_lock` and `detach_count`. Dependencies include cdev/class/sysfs, uaccess, poll, mmap VM ops, fasync, compat ioctls, capabilities, low-level COMEDI callbacks, buffer helpers, range/chanlist validation, and proc support. Risks include user-copy bounds, detach races, mmap leaks, lock-order deadlocks, run_active completion bugs, ioctl ABI regressions, compat translation errors, and event-recursion/notification issues in the observed source. Test native and compat ioctls, async read/write, command-test correction, mmap partial failure, poll/SIGIO, subdevice minors, detach during blocked IO, privilege gating, and unload after open/close.
