<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c

## Purpose
`test_tag.c` verifies that kernel-reported BPF program tags match the SHA-256-derived tag computed over the program instruction stream. It exercises both immediate-only programs and programs containing map-FD pseudo instructions.

## Important APIs, Types, And Functions
- Global `prog[BPF_MAXINSNS]` holds generated instruction streams.
- `bpf_gen_imm_prog()` fills programs with random `BPF_MOV` immediates and an exit.
- `bpf_gen_map_prog()` fills alternating `BPF_LD_MAP_FD` instruction pairs and terminates with an exit.
- `bpf_try_load_prog()` loads generated programs with `bpf_test_load_program()`, then regenerates map programs with fd zero to compute the normalized tag.
- `tag_from_fdinfo()` parses `prog_tag:` from `/proc/<pid>/fdinfo/<progfd>`.
- `tag_from_alg()` computes SHA-256 through the kernel AF_ALG hash API and reads the first 8 bytes.
- `do_test()` iterates instruction counts up to `BPF_MAXINSNS` and compares tags.

## Control Flow
`main()` enables libbpf strict mode, creates a small hash map, and repeats two test sweeps five times: immediate programs starting at two instructions and map-FD programs starting at three instructions. Each generated program is loaded, its fdinfo tag is read, the normalized instruction stream is hashed through AF_ALG, and mismatches call `tag_exit_report()` with both tags.

## State And Persistence
State is local to the process except for a transient BPF hash map, loaded BPF programs, AF_ALG sockets, and `/proc` fdinfo reads. Program fds are closed per iteration; the map fd is closed at exit.

## Dependencies And Integration Points
The test uses Linux BPF instruction macros, libbpf/bpf syscalls, `testing_helpers.c`, AF_ALG `sha256`, `/proc/<pid>/fdinfo`, and scheduler yields to avoid monopolizing CPU during large sweeps.

## Risks And Edge Cases
`assert()` is used for expected system support and load success, so unsupported AF_ALG/BPF environments abort rather than report graceful skips. The random immediate stream is seeded with current time, so exact generated programs vary. Map-FD normalization is essential; hashing real fd values would make tags unstable.

## Test Signals
Success prints `test_tag: OK (<count> tests)`. Any tag mismatch prints the instruction count, whether a map was used, fdinfo tag, AF_ALG tag, and exits with failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c -->
