# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_loop_inline.c

Purpose: tests verifier/JIT handling of `bpf_loop` helper inlining decisions and stack layout for loop callback state.

Important APIs/types/functions: uses `BPF_FUNC_loop`, pseudo/subprogram call macros, tracepoint program type, callback function bodies, stack slots for callback context, and `F_NEEDS_JIT_ENABLED`.

Control flow: accepted cases include a simple inline loop call, non-inlined calls when flags are nonzero or callback is non-constant, a loop with a dead function, loop-variable stack-location checks, and a big-program inline case. The callback and main program bodies are encoded as instruction arrays with relative calls and exits.

State and persistence behavior: state is verifier stack-frame metadata and callback/callee state. The stack-location test is specifically about separating loop helper bookkeeping from program stack slots and preserving callback argument state.

Dependencies and integration points: requires tracepoint program type and JIT enabled because the feature under test is inline expansion. The harness marks `.runs = 0` for several verifier-only cases.

Risks: incorrect inlining can change verifier complexity, break callback identity checks, or corrupt stack slot layout. Non-constant callbacks and nonzero flags must remain accepted without forcing inline conversion.

Test signals: all listed cases accept under `BPF_PROG_TYPE_TRACEPOINT` with `F_NEEDS_JIT_ENABLED`; failures would surface as verifier rejection or runtime mismatch in loop variable handling.
