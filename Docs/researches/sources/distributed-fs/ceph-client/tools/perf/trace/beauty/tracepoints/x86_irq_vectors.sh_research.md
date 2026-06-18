# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.sh

Purpose: Generates x86 IRQ vector names for tracepoint beautification.

Important APIs/types/functions: It emits `static const char *x86_irq_vectors[]` by reading `irq_vectors.h`.

Control flow: The script resolves `FIRST_EXTERNAL_VECTOR` to its numeric value, substitutes it into the header stream, matches `NAME_VECTOR 0xNN` definitions, sorts by vector number, and formats array entries without the `_VECTOR` suffix.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `x86_irq_vectors.c`.

Risks: It only handles simple hex defines. If useful vector definitions become expressions beyond `FIRST_EXTERNAL_VECTOR`, they may be omitted.

Test signals: Regenerate and verify expected vector names; compile tracepoint formatter and parse/format known values.
