# sources/distributed-fs/ceph-client/drivers/ntb/hw/Makefile

## Purpose

This Makefile descends into hardware-specific NTB driver directories based on Kconfig symbols.

## Important APIs, types, and functions

It maps `CONFIG_NTB_AMD` to `amd/`, `CONFIG_NTB_IDT` to `idt/`, `CONFIG_NTB_INTEL` to `intel/`, `CONFIG_NTB_EPF` to `epf/`, and `CONFIG_NTB_SWITCHTEC` to `mscc/`.

## Control flow and state behavior

There is no runtime behavior. It controls build traversal for selected hardware providers.

## Dependencies and integration points

The file must stay consistent with `drivers/ntb/hw/Kconfig` and each child directory Makefile.

## Risks and edge cases

Symbol/directory mismatches cause selected drivers not to compile or unselected directories to be traversed. This file also assumes child directories contain valid Makefiles.

## Test signals

Build matrix coverage that enables each NTB hardware symbol individually is the main validation signal.
