# sources/distributed-fs/ceph-client/arch/sparc/lib/mcount.S

Purpose: SPARC64 ftrace/mcount instrumentation entry code.

Important APIs/functions: Exports `_mcount`, `mcount`, defines `ftrace_stub`, `ftrace_caller`, patch sites `ftrace_call` and `ftrace_graph_call`, plus `ftrace_graph_caller` and `return_to_handler`.

Control flow: Saves enough call-frame state, checks tracing recursion/patch state, calls dynamic ftrace or graph tracing hooks through patchable call sites, and restores return paths. Graph tracing can redirect returns through `return_to_handler`.

State and persistence: Interacts with ftrace runtime patch state and call graph return stacks; no private persistent data here.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; integrated with kernel ftrace and function graph tracer.

Risks/test signals: Register-window and return-address handling are delicate. Test dynamic ftrace enable/disable, graph tracing, module tracing, and recursion protection under load.
