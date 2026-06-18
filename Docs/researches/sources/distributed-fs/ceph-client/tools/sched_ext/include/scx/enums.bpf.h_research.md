# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.bpf.h

Purpose: lightweight BPF-side wrapper that exposes generated sched_ext enum indirections to BPF programs.

Important APIs/functions: includes `enums.autogen.bpf.h`; it does not define independent logic.

Control flow: none.

State and persistence: delegates weak enum-value variables to the generated header.

Dependencies and integration: included at the tail of `common.bpf.h` after compatibility declarations, so all BPF examples can use enum-like macros.

Risks: any issue is inherited from generated enum headers. The small wrapper is easy to overlook when regenerating files.

Test signals: BPF examples compile and link with generated enum variables available.
