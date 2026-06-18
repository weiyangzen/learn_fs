# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Kconfig

## Purpose
Declares VirtualBox guest integration support.

## APIs, Types, and Functions
`VBOXGUEST` is a tristate depending on arm64/x86/compile-test, PCI, INPUT, and HAS_IOPORT.

## Control Flow and State
Build-time only. Enables the VirtualBox Guest PCI driver and related guest integration IPC.

## Dependencies and Integration
The help notes integration with vboxfs and recommends VBOXVIDEO for display support. The Makefile builds the Linux wrapper, core, and utility objects.

## Risks and Test Signals
Build-test on supported arches and `COMPILE_TEST`. Runtime tests are outside this file but should verify PCI probe, input device, misc devices, and vboxfs IPC consumers.
