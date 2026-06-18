# sources/distributed-fs/ceph-client/samples/bpf/fds_example.c

Purpose: demonstrates pinning and retrieving BPF map/program file descriptors from bpffs.

Important APIs/types/functions: defines mode/flag constants, `usage`, `bpf_prog_create`, `bpf_do_map`, `bpf_do_prog`, and `main`. Uses libbpf object loading, `bpf_obj_pin`, `bpf_obj_get`, map update/lookup, socket filter attach, and a tiny `BPF_PROG_TYPE_SOCKET_FILTER` instruction sequence.

Control flow: parses options selecting map or program mode and pin/get behavior. Map mode creates or retrieves a pinned map and optionally updates/reads a key/value. Program mode creates or retrieves a pinned program and can attach it to a socket.

State and persistence: bpffs paths persist pinned maps/programs beyond process lifetime. Map entries persist while the map pin exists.

Dependencies and integration: requires mounted bpffs, BPF syscall support, libbpf, root privileges, and the BPF sample build environment.

Risks: user must manage pinned object lifetime. The sample mixes demonstration flags, so invalid combinations must be caught by option handling. Program attach uses socket filter semantics and may not demonstrate all program types.

Test signals: pin a map, update a value, retrieve it in a second invocation, pin/retrieve a program, and verify cleanup by removing the bpffs files.
