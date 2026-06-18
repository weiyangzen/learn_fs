# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_abs.c

Purpose: validates legacy packet `LD_ABS` and `LD_IND` semantics, calling convention clobbers, packet reload after skb-mutating helpers, invalid sizes, arithmetic interaction, VLAN helper-generated programs, and jumping around absolute loads.

Important APIs/types/functions: uses `BPF_LD_ABS`, `BPF_LD_IND`, `BPF_FUNC_skb_vlan_push`, fill helpers `bpf_fill_ld_abs_vlan_push_pop` and `bpf_fill_jump_around_ld_abs`, packet `.data`, and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: calling-convention tests zero specific registers before `LD_ABS` and then read them to prove `R1`-`R5` are clobbered while `R7` survives. Valid helper tests save context in `R6/R7`, perform absolute loads, call VLAN push, reload context, and load again. Negative cases reject doubleword absolute/indirect loads. Other tests combine division with abs/ind loads, parse ARP-like data, and rely on fill helpers for generated VLAN/jump programs.

State and persistence behavior: packet data fixture is runtime input. Verifier state must model `LD_ABS` clobbers and context reload requirements after helpers that may adjust skb data.

Dependencies and integration points: scheduler classifier program type, packet data fixtures, and external fill helpers in the verifier harness.

Risks: `LD_ABS` is legacy but still security-sensitive because it has special implicit context and register-clobber semantics. Mis-modeling clobbers can allow use of invalid register state.

Test signals: expected rejections include `R1 !read_ok` through `R5 !read_ok` and `unknown opcode`; accepted cases return values such as `42`, `256`, `10`, `0`, `0xbef`.
