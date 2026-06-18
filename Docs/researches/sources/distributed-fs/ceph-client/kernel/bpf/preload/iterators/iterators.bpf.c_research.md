# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.bpf.c

Purpose: BPF-side iterator programs used by the preload module to print human-readable summaries of loaded BPF maps and programs. It is compiled into the generated skeleton headers embedded in the kernel module. The source was read as a complete 118-line file.

Important APIs/functions: `get_name`, `dump_bpf_map`, `dump_bpf_prog`, external kfunc symbol `bpf_map_sum_elem_count`, and GPL license section. It defines CO-RE-friendly shadow structs for iterator contexts, `bpf_map`, `bpf_prog`, `bpf_prog_aux`, `btf`, and BTF type/header data under `preserve_access_index`.

Control flow: `dump_bpf_map` receives a map iterator context, skips NULL end callbacks, prints a header at sequence number zero, and emits map ID, name, max entries, and summed current entries. `dump_bpf_prog` similarly skips NULL programs, prints a header, reads `prog->aux`, resolves a function name from BTF function info with `get_name` falling back to program name, and prints attached function/destination names. `get_name` validates BTF presence, probes the BTF type pointer, bounds-checks the name offset against BTF string length, and returns the string pointer or fallback.

State and persistence: BPF program state is transient per iterator callback. Output is written to the iterator `seq_file`; no maps are declared except skeleton rodata. The compiled object and skeleton persist as generated build artifacts.

Dependencies/integration: uses `bpf_helpers.h`, `bpf_core_read.h`, `BPF_SEQ_PRINTF`, `bpf_probe_read_kernel`, CO-RE relocation, BPF iterator attach types `iter/bpf_map` and `iter/bpf_prog`, and the kernel kfunc registered in `map_iter.c`.

Risks and edge cases: `dump_bpf_prog` dereferences `aux->func_info[0]`, `attach_func_name`, and `dst_prog->aux->name`; verifier/CO-RE assumptions must match iterator-visible program shapes. `get_name` only bounds-checks `name_off` against `str_len`; invalid BTF type arrays would rely on verifier/kernel read safety. Output format changes affect user-visible preload debug files.

Test signals: loading the generated iterator skeleton, reading `maps.debug` and `progs.debug`, CO-RE relocation tests across kernel BTF layouts, NULL end-callback behavior, and presence of sane table headers/rows under active maps/programs.
