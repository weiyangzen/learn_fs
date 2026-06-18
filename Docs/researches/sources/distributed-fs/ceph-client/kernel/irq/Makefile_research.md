# sources/distributed-fs/ceph-client/kernel/irq/Makefile

## Purpose
`irq/Makefile` maps IRQ subsystem configuration symbols to object files. It always builds the generic descriptor, handler, management, spurious, resend, chip, dummy-chip, devres, and kexec code, then conditionally includes domain, simulation, proc, migration, PM, MSI, IPI, debugfs, matrix allocator, and KUnit test objects.

## Important APIs, types, and functions
Always-built objects are `irqdesc.o`, `handle.o`, `manage.o`, `spurious.o`, `resend.o`, `chip.o`, `dummychip.o`, `devres.o`, and `kexec.o`. Conditional objects include `generic-chip.o`, `autoprobe.o`, `irqdomain.o`, `irq_sim.o`, `proc.o`, `migration.o`, `cpuhotplug.o`, `pm.o`, `msi.o`, `ipi.o`, `ipi-mux.o`, `affinity.o`, `debugfs.o`, `matrix.o`, and `irq_test.o`.

## Control flow
The build system appends objects to `obj-y` according to configuration. This determines which APIs are compiled and whether internal fallback stubs in headers are used.

## State and persistence
The file is build metadata only. Its effects persist in the final kernel image or modules but it owns no runtime data.

## Dependencies and integration points
It integrates directly with `irq/Kconfig` symbols and the top-level kernel build. Object ordering matters for built-in linkage only insofar as all generic core pieces must be present before conditional extension code references them.

## Risks and test signals
Risks include missing an object for a selected symbol, compiling tests without required helpers, and stale object names after file moves. Test signals include configuration matrix builds for `GENERIC_IRQ_CHIP`, `IRQ_DOMAIN`, `IRQ_SIM`, `GENERIC_IRQ_IPI`, `GENERIC_IRQ_DEBUGFS`, and `IRQ_KUNIT_TEST`.
