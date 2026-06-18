# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.bpf.h

Purpose: generated BPF-side enum-value indirection header for sched_ext constants.

Important APIs/macros: declares weak `const volatile u64 __SCX_*` variables and maps public macro names such as `SCX_SLICE_DFL`, `SCX_DSQ_GLOBAL`, `SCX_DSQ_LOCAL`, task state constants, and rq flags to those weak variables.

Control flow: none; macros substitute constants with load-time initialized weak variables.

State and persistence: BPF rodata-style weak variables hold enum values supplied/relocated by the loader environment.

Dependencies and integration: included through `enums.bpf.h`. User-space generated enum initialization populates matching skeleton fields so BPF code can use current kernel enum values without hard-coding them.

Risks: if initialization is missing, constants may remain zero and cause severe scheduler misbehavior. Weak volatile variables also reduce compile-time constant folding.

Test signals: verify `SCX_ENUM_INIT()` in user-space loaders populates these fields and that BPF examples behave correctly on kernels with changed enum numeric values.
