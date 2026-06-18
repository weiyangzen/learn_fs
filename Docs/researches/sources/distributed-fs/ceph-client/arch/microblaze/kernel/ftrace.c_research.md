# sources/distributed-fs/ceph-client/arch/microblaze/kernel/ftrace.c

Purpose: implements MicroBlaze dynamic ftrace and function-graph text patching support.

Important APIs and state: `prepare_ftrace_return()` patches the caller's return address to `return_to_handler`. `ftrace_modify_code()` writes one instruction with exception-table protection and flushes dcache/icache. Dynamic ftrace hooks include `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, and graph caller enable/disable. Static state saves original `imm`, optional `bralid`, and `old_jump` instructions.

Control flow: graph tracing safely reads/replaces the parent return address, stops graph tracing on fault, and registers the original return with ftrace core. Dynamic callsites are disabled by replacing the initial `imm` with `bri 12` (or NOPs under the disabled alternative), then restored from saved instructions.

State and persistence: persistent global saved instruction words affect all patched callsites, so this implementation assumes uniform compiler-generated mcount prologues.

Dependencies and integration: paired with `mcount.S`, cacheflush code, dynamic ftrace core, and MicroBlaze instruction encodings.

Risks and test signals: global saved instruction state is fragile if callsite prologues differ. Missing cache flushes break patched text execution. Test dynamic ftrace enable/disable, graph tracing, fault injection around patched addresses, and module callsites.
