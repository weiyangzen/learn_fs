# sources/distributed-fs/ceph-client/drivers/char/hw_random/s390-trng.c

Purpose: s390 CPACF TRNG driver providing both `/dev/trng` misc device and `hwrng` source.

Important APIs, types, and functions: `trng_read()`, sysfs `byte_counter`, `trng_hwrng_data_read()`, `trng_hwrng_read()`, debug init/exit, `trng_init()`, and `trng_exit()`.

Control flow: CPU-feature matched init registers debug support, verifies CPACF `PRNO TRNG`, registers misc device, then hwrng. Misc reads allocate a page for large reads, loop pagewise calling `cpacf_trng()`, handle scheduling/signals, copy to userspace, and update byte counters. hwrng reads cap to one page and update a separate counter.

State and persistence: global atomics count bytes served via misc and hwrng; `s390_arch_random_counter` is included in sysfs total. Debug feature state is global and removed on exit.

Dependencies and integration: s390 CPACF, CPU feature matching, miscdevice, debugfs/debug feature, sysfs attributes, hwrng, userspace copy helpers.

Risks and test signals: misc reads can be long-running and signal-interruptible; hwrng quality is implied high but not explicitly assigned here. Tests should cover missing CPACF function, misc/hwrng registration unwind, byte counters, large reads, signal interruption, copy fault, and module exit cleanup.
