# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Kconfig

## Purpose

This Kconfig file defines the AMD NTB hardware driver option.

## Important APIs, types, and functions

The single symbol is `NTB_AMD`, a tristate option named "AMD Non-Transparent Bridge support". It depends on `X86_64` and documents support for AMD NTB on capable Zeppelin hardware.

## Control flow and state behavior

There is no runtime behavior; selecting this symbol controls whether the AMD hardware driver directory builds.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/Makefile` plus `drivers/ntb/hw/amd/Makefile`.

## Risks and edge cases

The dependency is architecture-only; actual device support still depends on matching PCI IDs in `ntb_hw_amd.c`. If new AMD platforms are supported, help text and PCI IDs may need updates.

## Test signals

Config tests should verify visibility on x86_64 when NTB is enabled and hidden on non-x86_64 builds.
