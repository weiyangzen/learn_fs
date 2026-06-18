# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-template.h

Purpose: `rseq-bits-template.h` maps preprocessor mode flags to generated rseq helper suffixes and ABI CPU/mm-cid field offsets. It is the common naming and field-selection layer for all architecture bits headers.

Important APIs, types, and functions: it defines `RSEQ_TEMPLATE_CPU_ID_OFFSET`, `RSEQ_TEMPLATE_CPU_ID_FIELD`, `RSEQ_TEMPLATE_SUFFIX`, and `RSEQ_TEMPLATE_IDENTIFIER(x)`. Modes include `RSEQ_TEMPLATE_CPU_ID`, `RSEQ_TEMPLATE_MM_CID`, and `RSEQ_TEMPLATE_CPU_ID_NONE`, combined with `RSEQ_TEMPLATE_MO_RELAXED` or `RSEQ_TEMPLATE_MO_RELEASE`.

Control flow: there is no runtime control flow. The preprocessor selects one branch and constructs identifiers such as `_relaxed_cpu_id`, `_release_cpu_id`, `_relaxed_mm_cid`, `_release_mm_cid`, or `_relaxed`.

State and persistence: no runtime state. The generated values select whether helpers compare `cpu_id`, `mm_cid`, or no CPU-like ABI field, which affects runtime validation inside critical sections.

Dependencies and integration points: it depends on architecture headers defining offsets such as `RSEQ_CPU_ID_OFFSET` and `RSEQ_MM_CID_OFFSET`, and on `RSEQ_COMBINE_TOKENS` from the compiler helper stack. Every `*-bits.h` file includes it first.

Risks and test signals: misuse by direct include is explicitly rejected. Incorrect suffixes or offsets would cause link failures or, worse, helpers comparing the wrong ABI field. Test signals include successful multi-variant builds and passing CPU-id/mm-cid variants in `run_param_test.sh`.
