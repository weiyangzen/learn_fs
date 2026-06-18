# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Kconfig

## Purpose
Declares Amazon Nitro Enclaves lifetime-management driver and KUnit tests.

## APIs, Types, and Functions
`NITRO_ENCLAVES` is a tristate depending on arm64 or x86, CPU hotplug, PCI, and SMP. `NITRO_ENCLAVES_MISC_DEV_TEST` is a bool for KUnit tests depending on `NITRO_ENCLAVES` and `KUNIT=y`.

## Control Flow and State
Build-time only. Enables the PCI and misc-device driver pair.

## Dependencies and Integration
Runtime depends on CPU hotplug and PCI; tests are compiled into `ne_misc_dev.c` when selected.

## Risks and Test Signals
Build-test module and built-in variants on x86 and arm64. KUnit should be enabled in UML/qemu-style test kernels only.
