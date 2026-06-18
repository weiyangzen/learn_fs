<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c

## Purpose
`tracex3_user.c` loads the block I/O latency BPF programs and renders the per-CPU latency histogram as a colored or text heatmap.

## Important APIs, Types, And Functions
Important functions are `clear_stats()`, `print_banner()`, `print_hist()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__for_each_program()`, `bpf_program__attach()`, `bpf_map_lookup_elem()`, and `bpf_map_update_elem()`.

## Control Flow
It parses `-a` for full range and `-t` for text output, loads `<argv[0]>.bpf.o`, finds `lat_map`, attaches all programs, prints a legend, and loops every two seconds printing a heatmap and clearing the histogram.

## State And Persistence
Userspace maintains display flags and link handles. Kernel histogram state is cleared by writing zeroed per-CPU values for all slots after every print.

## Dependencies And Integration Points
It depends on libbpf, block tracepoints from the companion BPF object, terminal ANSI color support unless `-t` is used, and `bpf_num_possible_cpus()`.

## Risks And Edge Cases
The program runs forever until interrupted. ANSI color output may not be suitable for logs. It assumes exactly two programs when destroying `links[2]`.

## Test Signals
The heatmap should show nonzero event totals under block I/O, with banners every 20 intervals and successful attachment of both tracepoint programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c -->
