<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h

## Purpose
x86 ftrace integration for fentry address adjustment, dynamic direct-call metadata, graph tracing, syscall name matching, and compat syscall filtering. The header is 164 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/ptrace.h>`; `#include <linux/ftrace_regs.h>`; `#include <linux/compat.h>`

Notable constants/macros: `#define _ASM_X86_FTRACE_H`; `#define MCOUNT_INSN_SIZE 5 /* sizeof mcount call */`; `#define ARCH_SUPPORTS_FTRACE_OPS 1`; `#define ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`; `#define arch_ftrace_partial_regs(regs) do { \`; `#define arch_ftrace_fill_perf_regs(fregs, _regs) do { \`; `#define ftrace_regs_set_instruction_pointer(fregs, _ip) \`; `#define ftrace_graph_func ftrace_graph_func`; `#define FTRACE_GRAPH_TRAMP_ADDR FTRACE_GRAPH_ADDR`; `#define arch_ftrace_set_direct_caller(fregs, addr) \`; `#define ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; `#define ARCH_TRACE_IGNORE_COMPAT_SYSCALLS 1`

Notable declarations and inline helpers: `#define _ASM_X86_FTRACE_H`; `# define MCOUNT_ADDR ((unsigned long)(__fentry__))`; `#define MCOUNT_INSN_SIZE 5 /* sizeof mcount call */`; `# define FTRACE_MCOUNT_MAX_OFFSET ENDBR_INSN_SIZE`; `#define ARCH_SUPPORTS_FTRACE_OPS 1`; `extern void __fentry__(void);`; `static inline unsigned long ftrace_call_adjust(unsigned long addr)`; `static inline unsigned long arch_ftrace_get_symaddr(unsigned long fentry_ip)`; `#define ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`; `static __always_inline struct pt_regs *`; `#define arch_ftrace_partial_regs(regs) do { \`; `#define arch_ftrace_fill_perf_regs(fregs, _regs) do { \`; `#define ftrace_regs_set_instruction_pointer(fregs, _ip) \`; `static __always_inline unsigned long`; `struct ftrace_ops;`; `#define ftrace_graph_func ftrace_graph_func`; `void ftrace_graph_func(unsigned long ip, unsigned long parent_ip,`; `struct ftrace_ops *op, struct ftrace_regs *fregs);`; `#define FTRACE_GRAPH_TRAMP_ADDR FTRACE_GRAPH_ADDR`; `static inline void`; `#define arch_ftrace_set_direct_caller(fregs, addr) \`; `struct dyn_arch_ftrace {`; `void prepare_ftrace_return(unsigned long ip, unsigned long *parent,`; `unsigned long frame_pointer);`

## Control Flow
When dynamic ftrace is enabled, fentry IPs are adjusted around ENDBR, ftrace_regs are mapped to pt_regs, direct caller fields are filled, and graph return preparation hooks patch return paths.

## State and Persistence
State is dynamic ftrace records, per-call saved regs, dyn_arch_ftrace flags, and ftrace ops memory protection state managed elsewhere.

## Dependencies and Integration Points
Depends on ptrace regs, IBT ENDBR detection, function tracer config, ftrace_regs, graph tracer, syscall naming, and compat task detection.

## Risks
Risks include off-by-ENDBR symbol resolution, partial-register assumptions, incorrect direct-call IP storage, and tracing compat syscalls unexpectedly.

## Test Signals
Tests should run dynamic ftrace, function graph, direct trampolines, perf regs collection, IBT-enabled kernels, and compat syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h -->
