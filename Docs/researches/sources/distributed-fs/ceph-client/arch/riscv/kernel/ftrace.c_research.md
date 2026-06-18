# sources/distributed-fs/ceph-client/arch/riscv/kernel/ftrace.c

Purpose: Implements RISC-V dynamic ftrace text patching, call-site management, direct-call ops encoding, and function graph return setup.

Important APIs/types/functions: Provides `ftrace_arch_code_modify_prepare/post_process`, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `arch_ftrace_update_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_init_nop`, `ftrace_update_ftrace_func`, `ftrace_modify_call`, `prepare_ftrace_return`, and `ftrace_graph_func`.

Control flow: Ftrace transitions patch `auipc/jalr` call pairs or NOPs under text modification guards. Runtime ftrace caller assembly dispatches through the selected function pointer, and graph tracing rewrites return addresses through `prepare_ftrace_return()`.

State and persistence: Persistent state lives in ftrace records, patched kernel/module text, and optional encoded ops stored at call sites for direct-call support.

Dependencies and integration points: Depends on RISC-V instruction encoding helpers, `patch_text`, ftrace core, module text, graph tracer, and `mcount*.S`.

Risks and test signals: Text patching must be atomic enough for live CPUs and must preserve call-site reachability. Test dynamic ftrace enable/disable, function graph tracing, module tracing, direct ftrace ops, concurrent tracing toggles, and instruction decode validation.
