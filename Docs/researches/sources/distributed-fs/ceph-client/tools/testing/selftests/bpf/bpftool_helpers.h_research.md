# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.h

Purpose: declares the bpftool helper interface for selftests.

Important APIs and macros: `MAX_BPFTOOL_CMD_LEN`, `run_bpftool_command(char *args)`, and `get_bpftool_command_output(char *args, char *output_buf, size_t output_max_len)`.

Control flow: header only.

State and persistence: no state in the header; implementation caches bpftool path.

Dependencies and integration points: includes stdlib/stdio/stdbool and pairs with `bpftool_helpers.c`.

Risks: exposes mutable `char *` argument type even though implementations do not intend to mutate; max command length constant is smaller than implementation's full command buffer and may only guide callers.

Test signals: compile-time inclusion and successful command execution through the C file.
