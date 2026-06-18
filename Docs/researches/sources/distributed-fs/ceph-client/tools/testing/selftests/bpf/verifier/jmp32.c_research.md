# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jmp32.c

Purpose: comprehensive 32-bit jump semantics and verifier range-deduction suite.

Important APIs/types/functions: uses `BPF_JMP32_IMM`, `BPF_JMP32_REG`, predicates `JSET`, `JEQ`, `JNE`, unsigned `JGE/JGT/JLE/JLT`, signed `JSGE/JSGT/JSLE/JSLT`, packet data fixture macros, random extension macros (`BPF_RAND_UEXT_R7`, `BPF_RAND_SEXT_R7`), and map lookup fixups for range-bound memory access tests.

Control flow: for each predicate, BPF_K and BPF_X tests run multiple data inputs to prove upper 32 bits are ignored and signedness is correct. Min/max deduction tests use follow-up 64-bit checks or guarded invalid loads to ensure verifier pruning/range inference follows the 32-bit branch. Final cases verify bounded map-value offsets after 32-bit comparisons and JEQ/JNE bounds behavior.

State and persistence behavior: verifier abstract state is central: 32-bit comparisons must refine lower-word ranges without overtrusting upper bits. Runtime state comes from packet fixture data and helper-returned class IDs.

Dependencies and integration points: depends on scheduler classifier program type, direct packet fixture data, map hash fixups, and architecture flags for unaligned packet loads.

Risks: 32-bit branch range reasoning is easy to mix with 64-bit register state, causing false accepts or false rejects around bounds checks.

Test signals: all listed cases accept; many have `.runs` and `.retvals` arrays proving data-dependent branch behavior. Range tests use inserted nospec loads to expose bad verifier deductions.
