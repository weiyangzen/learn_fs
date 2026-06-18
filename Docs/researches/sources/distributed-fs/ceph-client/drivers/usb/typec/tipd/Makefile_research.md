# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/Makefile

## Purpose

This Makefile wires the Type-C TIPD TPS6598x driver objects into the kernel build. It builds the main `tps6598x` composite object from `core.o` and conditionally adds tracing support.

## Important APIs, Types, and Functions

The file sets `CFLAGS_trace.o := -I$(src)`, adds `tps6598x.o` to `obj-*` when `CONFIG_TYPEC_TPS6598X` is enabled, declares `tps6598x-y := core.o`, and adds `trace.o` through `tps6598x-$(CONFIG_TRACING)`.

## Control Flow

There is no runtime control flow. At build time, Kbuild evaluates `CONFIG_TYPEC_TPS6598X`; if built-in or module, it builds a composite target named `tps6598x.o` from `core.o`. If `CONFIG_TRACING` is enabled, `trace.o` is included in that composite object. The include flag for `trace.o` lets the trace source find headers in the same source directory, which is commonly needed for generated trace event headers.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the build graph selected by `.config`.

## Dependencies and Integration Points

It integrates directly with the sibling `Kconfig` symbol `TYPEC_TPS6598X` and with Kbuild's composite-object syntax. It assumes sibling sources `core.c` and, when tracing is enabled, `trace.c`/trace headers exist in the TIPD directory. The resulting module name matches the Kconfig help text: `tps6598x.ko` when built as a module.

## Risks

The build is small but sensitive to Kbuild naming. If source files are renamed or tracing support is reorganized, `tps6598x-y`, `tps6598x-$(CONFIG_TRACING)`, and `CFLAGS_trace.o` must be updated together. If tracing headers depend on include paths outside `$(src)`, the current trace CFLAGS may be insufficient.

## Test Signals

Build tests should cover `CONFIG_TYPEC_TPS6598X=y`, `CONFIG_TYPEC_TPS6598X=m`, and `CONFIG_TRACING=y/n`. Expected outputs are built-in driver objects for `y`, a `tps6598x.ko` module for `m`, and inclusion or exclusion of `trace.o` according to `CONFIG_TRACING`.
