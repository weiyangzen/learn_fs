# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Kconfig

## Purpose

This Kconfig file defines the generic EPF-backed NTB host driver option.

## Important APIs, types, and functions

The single symbol is `NTB_EPF`, a tristate option named "Generic EPF Non-Transparent Bridge support". Its help text describes support for configurable endpoint-based NTB.

## Control flow and state behavior

There is no runtime behavior; the symbol controls whether the EPF NTB hardware driver builds.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/epf/Makefile`.

## Risks and edge cases

The Kconfig option has no explicit PCI dependency in this file, although the driver itself is PCI-based and parent NTB normally depends on PCI. If reused outside the parent menu, dependencies would need tightening.

## Test signals

Build configuration should verify `CONFIG_NTB_EPF=m/y` compiles the EPF driver when NTB is enabled.
