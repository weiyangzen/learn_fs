# sources/distributed-fs/ceph-client/kernel/events/Makefile

## Purpose

This Makefile selects perf event subsystem objects for the kernel events directory. The listed file in this work item builds core perf event support, the ring buffer, callchain handling, and optional hardware breakpoint/uprobe support.

## Important APIs, Types, And Functions

- `obj-y := core.o ring_buffer.o callchain.o` always builds the main perf event components for this directory.
- `obj-$(CONFIG_HAVE_HW_BREAKPOINT) += hw_breakpoint.o` includes hardware breakpoint support when the architecture supports it.
- `obj-$(CONFIG_HW_BREAKPOINT_KUNIT_TEST) += hw_breakpoint_test.o` includes KUnit tests for hardware breakpoints.
- `obj-$(CONFIG_UPROBES) += uprobes.o` includes uprobes integration.

## Control Flow

Kbuild evaluates configuration symbols and includes the matching objects. `callchain.o` is always part of the directory build, which makes the callchain research in this work item part of the core perf event build.

## State And Persistence Behavior

The Makefile has no runtime state. It determines which objects are compiled into the kernel build.

## Dependencies And Integration Points

It integrates with Kbuild, perf events, ring buffers, architecture hardware breakpoint support, KUnit, and uprobes.

## Risks And Edge Cases

- Misconfigured object selection can omit required perf functionality or compile optional code without required architecture support.
- Optional KUnit test inclusion must remain guarded so production builds do not accidentally include test-only objects unless configured.

## Test Signals

Build with perf events, uprobes, hardware breakpoint, and KUnit hardware breakpoint configurations. Confirm object inclusion through build logs and run perf callchain, breakpoint, and uprobe tests where available.
