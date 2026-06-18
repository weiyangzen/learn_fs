# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.c

Purpose: Instantiates CDNS3 tracepoints by defining `CREATE_TRACE_POINTS` and including `cdns3-trace.h`.

Important APIs, types, and functions: No functions are defined directly. The file causes tracepoint definitions declared in `cdns3-trace.h` to be emitted into `cdns3-trace.o` when tracing and gadget support are enabled by the Makefile.

Control flow: Build-time tracepoint instantiation only; runtime behavior is provided by the generated tracepoint code and call sites in `cdns3-gadget.c` and `cdns3-ep0.c`.

State and persistence behavior: No local state. Runtime trace buffers are managed by the kernel tracing subsystem.

Dependencies and integration points: Depends on `cdns3-trace.h`, kbuild `CFLAGS_cdns3-trace.o := -I$(src)`, `CONFIG_TRACING`, and CDNS3 trace call sites.

Risks: Exactly one compilation unit should define `CREATE_TRACE_POINTS` for this trace header. Include-path or conditional-build mistakes cause missing trace symbols or duplicate definitions.

Test signals: Build with `CONFIG_TRACING=y`, boot/load the module, enable CDNS3 trace events under tracefs, exercise endpoint and USB interrupts, and verify events are emitted without duplicate symbol errors.
