# sources/distributed-fs/ceph-client/drivers/soc/sophgo/Makefile

## Purpose

This Makefile maps Sophgo SoC Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SOPHGO_CV1800_RTCSYS) += cv1800-rtcsys.o` builds the CV1800 RTC subsystem MFD parent. `obj-$(CONFIG_SOPHGO_SG2044_TOPSYS) += sg2044-topsys.o` builds the SG2044 TOP syscon MFD parent.

## Control Flow

During kbuild, enabled or modular config symbols expand into built-in objects or modules according to standard `obj-*` rules.

## State and Persistence Behavior

There is no runtime state. The file controls build graph membership only.

## Dependencies and Integration Points

It depends on the Kconfig symbols in the same directory and integrates with the top-level `drivers/soc` build.

## Risks and Edge Cases

Object names must remain synchronized with source filenames and Kconfig module help. No ordering constraints are encoded; both drivers are independent.

## Test Signals

Build all four combinations of the two Sophgo symbols as built-in/modules and verify expected `.o` or `.ko` outputs.
