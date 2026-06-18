# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_legacy.h

Purpose: exposes legacy BPF absolute/indirect packet load builtins under common names for GCC and Clang BPF program builds.

Important APIs and macros: `load_byte`, `load_half`, and `load_word` map to GCC `__builtin_bpf_load_*` or Clang `llvm.bpf.load.*` asm symbols.

Control flow: compile-time compiler branch only; no runtime logic in the header.

State and persistence: no state.

Dependencies and integration points: used by legacy socket-filter style BPF tests needing `BPF_LD_ABS`/`BPF_LD_IND` instruction emission.

Risks: these builtins are compiler-specific and not general memory loads; the skb argument is ignored under GCC mapping; misuse outside supported program contexts can fail verification.

Test signals: generated BPF bytecode should contain expected ABS/IND load instructions.
