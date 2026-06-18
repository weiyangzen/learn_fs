<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c

## Purpose
`tracex4_user.c` loads the slab allocation tracking BPF sample and periodically prints objects that have remained allocated for more than one second.

## Important APIs, Types, And Functions
Key routines are `time_get_ns()`, `print_old_objects()`, and `main()`. It uses libbpf object/program attach APIs and BPF map iteration with `bpf_map_get_next_key()` and `bpf_map_lookup_elem()`.

## Control Flow
The program loads `<argv[0]>.bpf.o`, finds `my_map`, attaches all programs, then loops once per second clearing the terminal and iterating map entries. Entries older than one second are printed with age and allocation IP.

## State And Persistence
Userspace state is minimal. Kernel state is the outstanding allocation map maintained by the BPF programs.

## Dependencies And Integration Points
It depends on libbpf, terminal escape handling, the companion kprobe object, and a kernel with the probed slab symbols.

## Risks And Edge Cases
It loops forever and clears the screen with ANSI escapes. It assumes two programs when destroying links. Without symbolization, IPs are raw addresses.

## Test Signals
Expected output is periodic lines of old object pointers under allocation activity; no setup errors should occur during object load, map lookup, or program attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c -->
