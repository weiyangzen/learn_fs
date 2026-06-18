<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h

Purpose: Inline assembly helpers for PowerPC VAS copy and paste instructions used to submit accelerator work.

Important APIs and types: Defines instruction encodings `PPC_INST_COPY`/`PPC_INST_PASTE`, register-field macros, `PPC_COPY`, `PPC_PASTE`, CR0 extraction constants, and inline functions `vas_copy` and `vas_paste`.

Control flow: `vas_copy` emits a copy instruction for the CRB address and returns CR0 status. `vas_paste` emits a paste instruction to the mapped paste address and returns CR0 status so callers can distinguish accepted/retry cases.

State and persistence: No persistent state; only condition register bits and memory ordering around accelerator submission are affected.

Dependencies and integration points: Consumed by `gzip_vas.c`. Depends on compiler inline asm and raw instruction support for VAS instructions.

Risks: Raw instruction encoding must match the architecture. Incorrect CR0 interpretation changes retry behavior and can make jobs appear submitted when they were not.

Test signals: Passing NX gzip tests demonstrate that copy/paste status codes are interpreted correctly enough to drive hardware jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h -->
