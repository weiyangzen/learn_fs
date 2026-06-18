# sources/distributed-fs/ceph-client/arch/sparc/kernel/ftrace.c

## Purpose
`ftrace.c` implements SPARC dynamic ftrace and function graph tracer patching. It converts call sites between SPARC `call` instructions and NOPs and hooks return addresses for graph tracing.

## Important APIs, Types, and Functions
Key functions are `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, optional `ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`, and `prepare_ftrace_return()`. Internal helpers are `ftrace_call_replace()` and `ftrace_modify_code()`.

## Control Flow and State
Dynamic ftrace computes a PC-relative call displacement, atomically compares/exchanges the instruction word at the target IP, flushes the instruction address, and uses exception-table fixup to report faults. Graph tracing updates `ftrace_graph_call` to call either `ftrace_graph_caller` or `ftrace_stub`. `prepare_ftrace_return()` skips paused graph tracing, calls `function_graph_enter()`, and returns `return_to_handler` when the graph stack accepts the frame; otherwise it returns the original parent adjusted by SPARC call delay semantics.

## Persistence and Dependencies
State is patched kernel text and per-task graph tracing state. Dependencies include `asm/ftrace.h`, SPARC instruction encoding, exception tables, cache flush semantics, and ftrace core APIs.

## Integration Points, Risks, and Test Signals
Integration is with dynamic ftrace, modules, and function graph tracer assembly. Risks include displacement overflow/truncation on far calls, CAS failures if text differs from expected old/new values, instruction cache coherency bugs, and off-by-one return address adjustment. Test signals are enabling/disabling function tracing, tracing module functions, graph tracer call/return balance, and no unexpected `ftrace_modify_code()` fault result.
