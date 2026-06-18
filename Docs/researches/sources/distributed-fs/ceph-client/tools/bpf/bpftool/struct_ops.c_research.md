# sources/distributed-fs/ceph-client/tools/bpf/bpftool/struct_ops.c

Purpose: Implements `bpftool struct_ops` subcommands for listing, dumping, registering, and unregistering BPF struct_ops maps.

Important APIs, types, and functions: `get_btf_vmlinux()` loads kernel BTF. `get_map_info_type_id()` finds BTF for `struct bpf_map_info` and sizes allocations to the running kernel's layout. `get_next_struct_ops_map()` iterates map ids and filters `BPF_MAP_TYPE_STRUCT_OPS`. `do_search()`, `do_one_id()`, and `do_work_on_struct_ops()` centralize selection by name/id/all. `__do_show()`, `__do_dump()`, and `__do_unregister()` perform per-map work. `do_register()` opens an object, loads it, attaches every struct_ops map with `bpf_map__attach_struct_ops()`, optionally pins BPF links, and reports map/link ids.

Control flow: Show/dump parse optional `id` or `name`, iterate selected struct_ops maps, and render either short metadata or BTF-dumped map info and value. Unregister requires a selector and deletes key zero from the map. Register loads an ELF, iterates maps, attaches struct_ops maps, obtains map/link info, optionally pins links under a bpffs directory, disconnects links so kernel state remains registered, and fails if no struct_ops maps exist.

State and persistence: Register can persist struct_ops state in the kernel and optionally pinned links in bpffs. Unregister removes the map element at key zero to unload. Static globals cache `btf_vmlinux`, `map_info_type`, allocation length, and type id for the command lifetime.

Dependencies and integration points: Depends on kernel BTF, libbpf struct_ops APIs, bpffs helpers, bpftool JSON/BTF dumper, BPF map/link syscalls, and `BPF_F_LINK` map flag semantics.

Risks: Requires `CONFIG_DEBUG_INFO_BTF`; without it most operations fail. Running-kernel `bpf_map_info` layout is handled via BTF allocation, but older kernels or missing fields can still affect dump fidelity. Register can partially attach maps while others fail, returning error after reporting successes.

Test signals: Exercise show/list all, show by name/id, dump JSON/plain, register object with and without `BPF_F_LINK`, link pinning, unregister by id/name, and kernels lacking BTF.
