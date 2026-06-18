# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-reset.h

Purpose: `rseq-bits-reset.h` cleans up template macros after a generated `*-bits.h` inclusion. It prevents one include pass from leaking suffix and CPU-id field definitions into the next pass.

Important APIs, types, and functions: it undefines `RSEQ_TEMPLATE_IDENTIFIER`, `RSEQ_TEMPLATE_CPU_ID_FIELD`, `RSEQ_TEMPLATE_CPU_ID_OFFSET`, and `RSEQ_TEMPLATE_SUFFIX`.

Control flow: there is no runtime behavior. The control-flow role is preprocessor-only: each architecture bits file includes this reset at the end so the parent architecture header can safely set a new `RSEQ_TEMPLATE_*` combination.

State and persistence: no runtime state exists. The only persistent effect is on the preprocessor macro namespace during compilation.

Dependencies and integration points: it is paired with `rseq-bits-template.h` and included at the end of architecture-specific `*-bits.h` files. All architecture headers rely on this cleanup because they intentionally include their bits files multiple times.

Risks and test signals: if this file misses a template macro, generated helper names or CPU-id field offsets can silently use stale state. Build failures or duplicate/missing symbols in architecture builds are the strongest test signals.
