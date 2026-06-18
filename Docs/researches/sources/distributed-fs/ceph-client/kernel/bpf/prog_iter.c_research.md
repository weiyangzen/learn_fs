# sources/distributed-fs/ceph-client/kernel/bpf/prog_iter.c

Purpose: registers the `bpf_prog` BPF iterator target so iterator programs can walk loaded BPF programs through seq_file. The source was read as a complete 106-line file.

Important APIs/functions: `bpf_prog_seq_start`, `bpf_prog_seq_next`, `bpf_prog_seq_show`, `bpf_prog_seq_stop`, `bpf_prog_iter_init`, and iterator context `struct bpf_iter__bpf_prog`. It defines `bpf_prog_seq_ops`, `bpf_prog_seq_info`, and `bpf_prog_reg_info`.

Control flow: seq start gets the current or next program ID and returns a referenced `struct bpf_prog`; next increments the ID cursor, drops the previous program, and fetches the next; show builds iterator metadata/context and runs the attached iterator BPF program; stop either runs the end callback with NULL or drops the current program reference. Late init fills the BTF ID for `struct bpf_prog` and registers the target.

State and persistence: each iterator file has private `prog_id` cursor state. Program refs persist only while a seq item is active. The iterator target registration persists for kernel lifetime after late init.

Dependencies/integration: uses BPF program ID registry helpers, BPF iterator registration, BTF ID lookup for `struct bpf_prog`, seq_file operations, and the preload `dump_bpf_prog` iterator program.

Risks and edge cases: the end callback passes NULL `prog`, so iterator programs must check it. Program deletion during iteration relies on ref acquisition. The context pointer is not marked trusted unlike map iterator, so verifier expectations differ.

Test signals: BPF iterator selftests over loaded programs, preload `progs.debug` output, program deletion while iterating, and BTF target registration at late init.
