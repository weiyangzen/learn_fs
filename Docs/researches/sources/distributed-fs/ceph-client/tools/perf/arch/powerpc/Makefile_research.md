# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/Makefile

Purpose: Perf architecture make fragment for `powerpc` that advertises architecture capabilities such as JIT dump support.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Included by perf build logic to set `PERF_HAVE_JITDUMP` or architecture object selections.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf recursive make inclusion order.

Risks: A missing capability flag changes feature availability without compile errors.

Test signals: Architecture perf build and feature probe output.

Source coverage: researched from the complete local file (3 lines, 58 bytes).
