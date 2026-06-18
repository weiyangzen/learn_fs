<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S

### Purpose
`mcount.S` implements MIPS `_mcount`, `ftrace_caller`, function graph caller support, and `return_to_handler` assembly. It is the low-level callsite ABI used by `ftrace.c` for dynamic and non-dynamic function tracing.

### Important APIs, Types, And Functions
Exported labels include `_mcount`, `ftrace_caller`, `ftrace_call`, `ftrace_graph_call`, `ftrace_stub`, `ftrace_graph_caller`, and `return_to_handler`. Register save/restore macros are `MCOUNT_SAVE_REGS`, `MCOUNT_RESTORE_REGS`, and `RETURN_BACK`.

### Control Flow
In dynamic ftrace builds, `_mcount` initially branches to `ftrace_stub`; patched callsites jump into `ftrace_caller + 8`, save caller-saved registers, compute the traced function address, call the patched tracing function via `ftrace_call`, optionally call graph tracing, restore registers, and return with the original parent return address restored from `AT`. Non-dynamic builds call `ftrace_trace_function` directly when not equal to `ftrace_stub`, then check graph tracer hooks. Graph tracing passes the parent return-address slot, self return address, and frame pointer to `prepare_ftrace_return()`.

### State, Persistence, And Dependencies
State is on the temporary pt_regs-like stack frame, the caller's return address in `AT`/`ra`, optional `$12` return-address slot from `KBUILD_MCOUNT_RA_ADDRESS`, and patched instruction placeholders. Dependencies include `asm/ftrace.h`, `stackframe.h`, `ftrace.c`, and compiler-generated `_mcount` callsite layout.

### Integration Points
The assembly must match `ftrace_make_call()`/`ftrace_make_nop()` patch expectations and function graph return handling in `ftrace.c`. `return_to_handler` calls `ftrace_return_to_handler()` and jumps to the real parent address.

### Risks
The ABI is very narrow: wrong stack adjustment, saved-register set, module callsite offset, or return-address handling corrupts traced functions. 32-bit builds include legacy stack adjustment in delay slots, which dynamic patching removes.

### Test Signals
Enable function tracing and graph tracing on 32-bit and 64-bit MIPS, trace modules, test builds with and without `KBUILD_MCOUNT_RA_ADDRESS`, and compare callsite disassembly against `ftrace.c` patch comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S -->
