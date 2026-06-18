# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Makefile

Purpose: builds the Thunderbolt/USB4 networking driver.

Important APIs/types/functions: `obj-$(CONFIG_USB4_NET) := thunderbolt_net.o` creates the driver object; `thunderbolt_net-objs := main.o trace.o` links implementation and tracepoint definition; `CFLAGS_trace.o := -I$(src)` lets tracepoint generation include local `trace.h`.

Control flow: Kbuild compiles the composite object according to `CONFIG_USB4_NET` and applies the include path only for tracepoint compilation.

State and persistence: no runtime state; build graph only.

Dependencies and integration: depends on Kbuild composite-object semantics and local tracepoint header layout.

Risks: omitting `trace.o` would leave tracepoint definitions unresolved; omitting `CFLAGS_trace.o` can break `TRACE_INCLUDE_PATH .` lookup.

Test signals: build with tracing enabled, run `modinfo thunderbolt_net`, and verify trace events under the `thunderbolt_net` system are generated.
