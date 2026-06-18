# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.c

Purpose: standalone helper program to attach or detach a BPF flow dissector program and pin the loaded object.

Important APIs and functions: global config variables hold pin path, prog-array map name, attach flag, section name, and object path. `parse_opts()` handles `-a`, `-d`, `-p`, and `-s`. `load_and_attach_program()` uses `bpf_flow_load()`, `bpf_prog_attach(..., BPF_FLOW_DISSECTOR)`, and `bpf_object__pin()`. `detach_program()` detaches and removes the pin directory.

Control flow: main parses options, then either loads/attaches/pins or detaches/unpins. Attach requires both object path and section name.

State and persistence: attaching persists a flow dissector program in kernel state and pins object under `/sys/fs/bpf/flow_dissector`; detach removes both.

Dependencies and integration points: depends on libbpf strict mode, `flow_dissector_load.h`, bpffs, and kernel flow dissector attach support.

Risks: `detach_program()` uses `system("rm -r ...")` with a global path; attach/detach are privileged operations; pin path is fixed; `error(1, ...)` exits immediately on failure.

Test signals: successful attach leaves pinned object and active flow dissector; successful detach removes it.
