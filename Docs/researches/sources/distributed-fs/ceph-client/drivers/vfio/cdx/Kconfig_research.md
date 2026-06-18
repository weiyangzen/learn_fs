# sources/distributed-fs/ceph-client/drivers/vfio/cdx/Kconfig

## Purpose

This Kconfig file defines VFIO support for devices on the CDX bus.

## Important APIs, Types, and Functions

The only symbol is `VFIO_CDX`, a tristate option depending on `CDX_BUS` and selecting `EVENTFD`.

## Control Flow

When selected, the CDX VFIO driver is built and can bind CDX devices for userspace access through VFIO. If `CDX_BUS` is unavailable, the option is hidden.

## State and Persistence Behavior

It provides build-time state in `.config`; no runtime state is declared here.

## Dependencies and Integration Points

It integrates the CDX bus with VFIO and eventfd-backed interrupts. The Makefile maps it to `vfio-cdx.o`.

## Risks and Edge Cases

The feature is useless without CDX bus support and generic MSI support affects whether the interrupt implementation is included. Userspace expectations depend on VFIO core options selected at the top level.

## Test Signals

Build with `CDX_BUS=y/m`, `VFIO_CDX=y/m`, and without `CONFIG_GENERIC_MSI_IRQ` to verify interrupt stubs compile.
