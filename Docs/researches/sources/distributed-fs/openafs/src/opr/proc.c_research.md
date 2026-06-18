# sources/distributed-fs/openafs/src/opr/proc.c

Purpose: process-size reporting helper.

Important APIs/types/functions: `opr_procsize()` returns an approximate process size in kilobytes. On NT it returns -1. Where `struct rusage` has `ru_idrss`, it uses `getrusage`; otherwise it approximates with `sbrk(0) >> 10`.

Control flow: simple platform conditional selection.

State and persistence: reads process resource/heap state only. No persistence.

Dependencies/integration: includes unistd and optionally sys/resource. Declared by `opr/proc.h`.

Risks and test signals: metric semantics differ by platform and can be unavailable. It is useful only for relative logging on the same host. Tests should tolerate -1 and platform variation.
