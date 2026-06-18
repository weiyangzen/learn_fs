# sources/distributed-fs/ceph-client/samples/trace_printk/Makefile

## Purpose

This Kbuild file builds the `trace-printk` sample module when `CONFIG_SAMPLE_TRACE_PRINTK` is enabled.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_SAMPLE_TRACE_PRINTK) += trace-printk.o`.

## Control Flow

Kbuild includes the object as built-in or module depending on the config.

## State and Persistence Behavior

No runtime state is created by the Makefile.

## Dependencies and Integration Points

The C file depends on tracing and IRQ work APIs.

## Risks and Edge Cases

Only build selection is represented here; Kconfig must ensure tracing prerequisites.

## Test Signals

Enable the config and verify `trace-printk.o` or module output.
