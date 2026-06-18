# sources/distributed-fs/ceph-client/arch/x86/mm/testmmiotrace.c

## Purpose
`testmmiotrace.c` is a deliberately dangerous test module for mmiotrace. Given a caller-supplied MMIO address, it maps the region, performs known 8/16/32-bit writes and reads, optionally performs a far read, and stress-tests repeated ioremap/iounmap reuse.

## Important APIs, Types, and Functions
Module parameters are `mmio_address` and `read_far`. Test helpers are `v16()`, `v32()`, `do_write_test()`, `do_read_test()`, `do_read_far_test()`, `do_test()`, and `do_test_bulk_ioremapping()`. Module lifecycle functions are `init()` and `cleanup()`.

## Control Flow and State
`init()` checks lockdown policy with `security_locked_down(LOCKDOWN_MMIOTRACE)`, requires `mmio_address`, warns loudly, chooses 16 KiB or 8 MiB mapping size, runs the read/write tests, performs repeated one-page mappings, forces RCU synchronization, and exits. `do_test()` wraps `ioremap()`, logs the returned virtual mapping through `mmiotrace_printk()`, performs writes, reads back expected values, optionally performs the far read, and unmaps.

## State and Persistence
Persistent module state is limited to parameters. External state is intentionally affected: the module writes test patterns to the supplied MMIO/PCI address space and emits mmiotrace records and kernel logs.

## Dependencies and Integration Points
It depends on mmiotrace, `ioremap()`/`iounmap()`, `ioread*()`/`iowrite*()`, RCU deferred freeing, kernel lockdown policy, and module parameter infrastructure.

## Risks and Test Signals
Risks are explicit: loading against a real device BAR can corrupt hardware state. Other risks include invalid addresses, read side effects, and test assumptions about writable/readable MMIO. Test signals are mmiotrace logs for each access width, read error counters, successful far-read logging, no crash during bulk ioremap reuse, and lockdown preventing use when policy forbids mmiotrace.
