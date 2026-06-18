# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/trace.c

Purpose: hosts tracepoint definition linkage for Book3S64 MM-related tracing, currently pulling in transparent hugepage trace event definitions when THP is enabled.

Important APIs and control flow: there are no runtime functions; the file exists so trace/event headers can instantiate tracepoint data in exactly one compilation unit. Under `CONFIG_TRANSPARENT_HUGEPAGE`, it includes `<trace/events/thp.h>`.

State and dependencies: no persistent state beyond generated tracepoint objects. It depends on kernel tracing infrastructure, THP configuration, and build-system inclusion for Book3S64. Risks are mainly build/linkage risks: duplicate tracepoint definitions if moved incorrectly, or missing THP events if omitted. Test signals are successful THP-enabled builds and ftrace/perf visibility of THP events on Book3S64 kernels.
