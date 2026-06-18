<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h

## Purpose
This header defines SPARC ftrace support hooks and call-site conventions.

## Important APIs, Types, and Functions
It declares architecture-specific ftrace graph/call handling structures or macros used by dynamic function tracing.

## Control Flow
When ftrace is enabled, patched call sites and graph tracer paths use these definitions to route function entry/return events.

## State and Persistence Behavior
Runtime ftrace state is managed by generic tracing and patched text; the header declares architecture contracts.

## Dependencies and Integration Points
It integrates with dynamic ftrace, function graph tracing, module text patching, and SPARC instruction encoding.

## Risks
Wrong call-site size or return-address handling can crash traced functions.

## Test Signals
Enable function and graph tracing, trace module and built-in functions, and run ftrace selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h -->
