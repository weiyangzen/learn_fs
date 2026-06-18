# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.c lines 9444-14771

## Scope

This chunk covers the tail half of the tools-side `libbpf.c` implementation bundled under `sources/distributed-fs/ceph-client`. The range starts inside `bpf_object__unpin()` and then covers object teardown, public object/program/map accessors and mutators, section-definition dispatch, BTF attach-target lookup, map operation wrappers, `bpf_link` lifecycle and attach helpers, probe/tracepoint/cgroup/network/iterator/struct_ops attachment, perf-buffer consumption, CPU mask parsing, and BPF skeleton/subskeleton lifecycle helpers.

The code is generic libbpf infrastructure, not Ceph-specific filesystem logic. Its importance to this tree is that any in-tree BPF tooling built from this copy gets its object lifetime, loading/attachment behavior, map manipulation, perf-buffer event delivery, and skeleton behavior from this implementation.

## Purpose

The chunk provides the high-level user-space API surface that turns opened BPF objects into loaded programs, attached links, usable maps, perf event consumers, and generated skeleton handles. It bridges ELF/BTF metadata and `SEC()` section naming conventions to concrete kernel operations such as `bpf_prog_load()`, `bpf_link_create()`, `bpf_map_update_elem()`, `perf_event_open()`, tracefs probe registration, and bpffs pinning.

It also centralizes many state-transition rules. Program and map definitions can be changed before load or map creation but become immutable after kernel objects exist. Link objects own detach/close behavior unless explicitly disconnected. Skeleton helpers populate generated C structs with libbpf object pointers, mmap addresses, and link slots so callers can use generated BPF skeletons without manually resolving every map and program.

## Important APIs, Types, and Functions

Object and map teardown is handled by `bpf_map__destroy()` and `bpf_object__close()`. Map destruction recursively frees inner-map templates, initial slots, mmaped data, struct_ops backing data, names, pin paths, and map FDs. Object close performs post-load cleanup, frees the USDT manager, generated loader, ELF state, BTF/BTF.ext objects, maps, extern descriptors, programs, feature cache, token path/FD, arena data, jump table data, and jump-table map FDs.

Object accessors include `bpf_object__name()`, `bpf_object__kversion()`, `bpf_object__token_fd()`, `bpf_object__btf()`, `bpf_object__btf_fd()`, `bpf_object__set_kversion()`, and `bpf_object__gen_loader()`. `bpf_object__gen_loader()` allocates a `struct bpf_gen`, records caller options, and tracks cross-endian generation.

Program APIs include iteration (`bpf_object__next_program()`, `bpf_object__prev_program()`), name/section/autoload/autoattach accessors, instruction access and replacement, FD/type/expected attach type/flags/log buffer accessors, BTF func/line info accessors, and `bpf_program__clone()`. Mutators such as `bpf_program__set_autoload()`, `bpf_program__set_type()`, `bpf_program__set_expected_attach_type()`, `bpf_program__set_flags()`, `bpf_program__set_log_level()`, and `bpf_program__set_log_buf()` reject changes after the object is loaded. `bpf_program__clone()` loads another copy of an already prepared program, merging caller-provided load options with program/object defaults and intentionally avoiding object-state mutations such as RODATA map binding.

Section dispatch is built around `struct bpf_sec_def`, the `SEC_DEF()` macro, the built-in `section_defs[]` table, custom handler globals, and `libbpf_register_prog_handler()` / `libbpf_unregister_prog_handler()`. Built-in section families cover socket filters, reuseport, kprobes, uprobes, syscall probes, USDT, tc/tcx/netkit, tracepoints, raw tracepoints, BTF tracing, LSM, iterators, syscall, XDP, perf events, LWT, cgroup, sockmap/sk_msg/sk_lookup, lirc, flow dissector, struct_ops, and netfilter. `sec_def_matches()` implements exact, `type/`, and `type+` matching; `find_sec_def()` prefers custom handlers, then built-ins, then an optional fallback handler.

Type-name helpers include `libbpf_prog_type_by_name()`, `libbpf_attach_type_by_name()`, and string conversion functions for attach, link, map, and program types. BTF attach resolution is handled by `btf_get_kernel_prefix_kind()`, `find_attach_btf_id()`, `libbpf_find_vmlinux_btf_id()`, `libbpf_find_prog_btf_id()`, `find_kernel_btf_id()`, and `libbpf_find_attach_btf_id()`. These functions map attach names to vmlinux, module, or target-program BTF type IDs, with generated-loader handling recording deferred attach targets.

Struct_ops support in this range includes `find_struct_ops_map_by_offset()`, `bpf_object__collect_st_ops_relos()`, `bpf_map__attach_struct_ops()`, `bpf_link__update_map()`, and `bpf_program__assoc_struct_ops()`. Relocation collection maps ELF relocations in struct_ops data to `struct bpf_program *` entries and shadow data. Attachment writes prepared kernel struct_ops data to map key zero and, when `BPF_F_LINK` is used, creates a real `BPF_STRUCT_OPS` link.

Map APIs include FD/name/type/flag/extra/NUMA/key-size/value-size/BTF-ID/initial-value/internal/ifindex accessors and mutators, inner-map FD configuration, exclusive-program configuration, map iteration and lookup by name, and typed wrappers for lookup, update, delete, lookup-and-delete, and get-next-key. `map_btf_datasec_resize()` adjusts BTF datasec and trailing array metadata when resizing an mmaped array map. `validate_map_op()` protects public map operations with created-map checks and key/value-size validation, including per-CPU map value sizing and `BPF_F_CPU` / `BPF_F_ALL_CPUS` handling.

Link APIs include `libbpf_get_error()`, `bpf_link__update_program()`, `bpf_link__disconnect()`, `bpf_link__destroy()`, `bpf_link__fd()`, `bpf_link__pin_path()`, `bpf_link__open()`, `bpf_link__detach()`, `bpf_link__pin()`, and `bpf_link__unpin()`. Link implementations use detach/dealloc callbacks to abstract perf-event links, fd-backed kernel links, bpffs-pinned links, and struct_ops pseudo-links.

Attachment helpers cover a broad set of program types. Perf-event attachment uses `bpf_program__attach_perf_event_opts()` and can choose real BPF links or legacy `PERF_EVENT_IOC_SET_BPF`. Kprobe and uprobe attachment support modern perf event source PMUs, explicit attach modes, legacy tracefs event registration, cookies, return probes, offsets, syscall-wrapper naming, and generated auto-attach from `SEC()` strings. Multi-kprobes and multi-uprobes use `bpf_link_create()` with symbol/address arrays, glob pattern resolution, optional uniqueness checks, cookies, sessions, and return-probe flags.

The probe support code depends on helpers for tracefs/debugfs paths, event ID parsing, syscall architecture prefixes, glob matching, `available_filter_functions` or `available_filter_functions_addrs` parsing, kallsyms fallback, binary path resolution, ELF symbol offset resolution, and archive member handling for uncompressed ZIP/APK-style files.

Other attach APIs include USDT (`bpf_program__attach_usdt()` and `attach_usdt()`), tracepoints, raw tracepoints, BTF tracing/LSM/fentry/fexit/fmod_ret/freplace, cgroup, netns, sockmap, XDP, cgroup options, TCX, netkit, iterators, netfilter, and generic `bpf_program__attach()`. `bpf_program__set_attach_target()` configures attach BTF IDs for freplace/tracing-style programs before load.

Perf-buffer support defines `struct perf_buffer_params`, `struct perf_cpu_buf`, and `struct perf_buffer`, plus `perf_buffer__new()`, `perf_buffer__new_raw()`, `perf_buffer__free()`, `perf_buffer__poll()`, `perf_buffer__consume()`, per-buffer consume/accessor helpers, and the internal `perf_event_read_simple()` ring parser. It opens one perf event per selected CPU, mmaps ring buffers, stores FDs into a `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, adds FDs to epoll, dispatches raw events or higher-level sample/lost callbacks, and cleans up map slots and FDs on free.

CPU helpers include `parse_cpu_mask_str()`, `parse_cpu_mask_file()`, and `libbpf_num_possible_cpus()`. Skeleton helpers include `populate_skeleton_maps()`, `populate_skeleton_progs()`, `bpf_object__open_skeleton()`, `bpf_object__open_subskeleton()`, `bpf_object__destroy_subskeleton()`, `bpf_object__load_skeleton()`, `bpf_object__attach_skeleton()`, `bpf_object__detach_skeleton()`, and `bpf_object__destroy_skeleton()`.

## Control Flow

Object lifetime flows from open/prepare/load in earlier code into this chunk's close path. `bpf_object__close()` is defensive against partially prepared objects by invoking `bpf_object_post_load_cleanup()` before freeing resources that normal load completion would otherwise release. It then unloads kernel programs/maps, frees metadata, destroys each map, exits each program, closes token and jump-table FDs, and finally frees the object.

Program cloning starts with a prepared original program. `bpf_program__clone()` validates options, fills a `bpf_prog_load_opts` structure from caller values or program/object defaults, conditionally supplies BTF func/line records when supported, allows section-specific prepare hooks to adjust attach fields, reapplies caller attach overrides, and calls `bpf_prog_load()`.

Section matching and auto-attach flow is table driven. During object initialization, a program's `SEC()` name is mapped to a `bpf_sec_def`. Later, skeleton or explicit attach code calls the definition's `prog_attach_fn`. Some functions intentionally return success with `*link == NULL` when a section is syntactically valid but lacks enough target information for auto-attach, such as bare `SEC("kprobe")` or `SEC("uprobe")`.

Probe attachment generally follows this pattern: validate options and loaded program FD, resolve target identity from section strings or explicit arguments, choose modern or legacy attach mode, create a perf event or BPF link, attach the BPF program, enable the perf event if needed, and return a `bpf_link` with detach/dealloc callbacks. Legacy kprobe/uprobe paths append events to tracefs, open the generated tracepoint perf event, and remove the tracefs event during detach or error cleanup.

Multi-kprobe attachment either passes an exact symbol name directly to the kernel or resolves a wildcard pattern to addresses through tracefs and kallsyms. Multi-uprobe attachment resolves explicit symbol names or function patterns to ELF offsets, then calls `bpf_link_create()` with path, offset arrays, optional ref-counter offsets, optional cookies, and PID scoping.

Map operation wrappers flow through `validate_map_op()` before invoking raw BPF syscalls. This catches uncreated maps, key-size mismatches, missing FDs, regular value-size mismatches, and per-CPU value-size rules before the kernel call. The wrappers then call the corresponding `bpf_map_*` syscall wrapper.

Perf-buffer creation verifies `page_cnt` is a nonzero power of two, performs a best-effort map-type check, creates an epoll instance, determines CPU count, allocates buffer/event arrays, reads online CPUs, opens and mmaps per-CPU perf events, stores each perf FD into the BPF map, and registers each FD with epoll. Polling waits on epoll and processes records from ready CPU buffers. Consuming skips epoll and directly drains one or all buffers.

Skeleton flow starts by opening an embedded object from `s->data`, populating generated map/program pointers by name, loading the object, refreshing mmap pointers after load, and auto-attaching programs or struct_ops maps that are marked for autoattach. Destruction always detaches generated links, closes the object, and frees generated arrays.

## State and Persistence Behavior

This code owns both user-space state and kernel object references. `struct bpf_object`, `struct bpf_map`, `struct bpf_program`, `struct bpf_link`, and `struct perf_buffer` contain heap pointers and FDs that must be released exactly once through the matching close/free/destroy helpers. `bpf_link__disconnect()` changes ownership semantics by preventing destruction from detaching the underlying kernel resource.

Program and map mutators are state-gated. Program type, attach type, flags, instructions, autoload, log buffer, and kversion changes are rejected after load or preparation boundaries. Map type, flags, extra, NUMA node, key/value size, ifindex, inner-map FD, and exclusive program are rejected after map creation. These checks prevent divergence between libbpf's cached metadata and kernel-created objects.

Pinning state is represented by `pin_path` strings on maps and links, with filesystem persistence in bpffs managed through `bpf_obj_pin()`, `bpf_obj_get()`, and `unlink()`. Opened pinned links are represented as `bpf_link` objects whose detach callback closes the FD.

Perf-buffer state persists until `perf_buffer__free()`: per-CPU perf FDs are stored in the perf-event-array map, ring buffers remain mmaped, and epoll tracks readiness. Freeing deletes the map entries, disables and closes perf events, unmaps memory, closes epoll, and frees callback storage.

CPU possible-count caching persists in a static `cpus` variable populated from `/sys/devices/system/cpu/possible` with `READ_ONCE()` / `WRITE_ONCE()`. Online CPU masks are read at perf-buffer creation time and are not dynamically updated.

Skeleton state is split between generated caller-owned `struct bpf_object_skeleton` fields and libbpf-owned object/link resources. `open_skeleton()` fills map/program pointers; `load_skeleton()` fills mmap addresses; `attach_skeleton()` fills link pointers; `detach_skeleton()` clears links to `NULL`.

## Dependencies and Integration Points

The chunk depends heavily on Linux BPF syscalls and libbpf internal wrappers: `bpf_prog_load()`, `bpf_link_create()`, `bpf_link_update()`, `bpf_link_detach()`, `bpf_obj_get()`, `bpf_obj_pin()`, `bpf_map_*()` operations, `bpf_prog_get_info_by_fd()`, `bpf_map_get_info_by_fd()`, `bpf_raw_tracepoint_open_opts()`, and `bpf_prog_assoc_struct_ops()`.

BTF integration uses `btf__load_vmlinux_btf()`, `btf_load_from_kernel()`, `btf__find_by_name_kind()`, `btf__type_by_id()`, datasec/array/member helpers, module BTF loading, and object-local `btf_vmlinux` / module BTF caches. Attach-target resolution connects section metadata to kernel, module, or target-program BTF IDs.

Probe and trace attachment integrate with `perf_event_open()`, `ioctl(PERF_EVENT_IOC_SET_BPF/ENABLE/DISABLE)`, `/sys/bus/event_source/devices/{kprobe,uprobe}`, tracefs/debugfs `kprobe_events`, `uprobe_events`, `available_filter_functions`, `available_filter_functions_addrs`, tracepoint event ID files, kallsyms parsing, ELF symbol resolution, ZIP archive parsing, environment path lookup, and architecture-specific syscall naming.

Network and cgroup attachment helpers integrate with kernel link types for cgroup, netns, sockmap, XDP, TCX, netkit, netfilter, and iterator targets. Relative attach options and expected revisions are forwarded through `bpf_link_create_opts`.

USDT attachment integrates with a lazily allocated `usdt_manager` stored on the object. The manager is freed by `bpf_object__close()`, so USDT links and object lifetime are coupled.

Generated skeleton helpers integrate with bpftool-style generated C skeleton structures: `struct bpf_object_skeleton`, `struct bpf_map_skeleton`, `struct bpf_prog_skeleton`, `struct bpf_object_subskeleton`, and `struct bpf_var_skeleton`. They rely on map/program names and BTF datasec variable metadata remaining consistent with generated code.

## Risks and Edge Cases

The chunk starts inside `bpf_object__unpin()`, so full-file reconciliation should combine it with the preceding chunk for the complete pin/unpin story.

Lifetime bugs are high impact. Missing detach callbacks, double destruction, forgetting to clear skeleton link pointers, or closing a perf FD still used as a link FD can detach programs unexpectedly or leak kernel resources. The perf link detach path has special handling for `perf_event_fd != link->fd` and for legacy tracefs event cleanup.

State gating must remain strict. Allowing program or map metadata changes after load/map creation can make libbpf's cached type, size, BTF, or attach metadata inconsistent with kernel objects. Conversely, overly strict checks can break callers that legitimately configure objects between open, prepare, and load.

Section matching is order sensitive. Custom definitions override built-ins, built-ins rely on longest/specific entries appearing before broader aliases, and fallback handlers catch all unmatched sections. Incorrect matching can load a program with the wrong type, expected attach type, sleepable flag, or auto-attach handler.

Probe attachment has many environment-sensitive failure modes: missing tracefs/debugfs, unsupported kprobe/uprobe PMUs, kernels without perf-link support, unavailable syscall wrapper naming, unresolved symbols, duplicate wildcard matches when uniqueness is requested, stripped or LTO-renamed symbols, compressed archive members, missing execute/read permissions, and unsupported reference counters in legacy uprobes.

Multi-probe option validation is subtle. Pattern mode is mutually exclusive with explicit arrays; address and symbol arrays are mutually exclusive; `cnt` must be nonzero for explicit arrays; return-probe and session modes are mutually exclusive. Violating these combinations should fail early rather than passing ambiguous options to the kernel.

Perf-buffer parsing assumes valid perf ring records. Wrapped records are copied into a temporary buffer, and `page_cnt` must be a power of two. Bad map type, offline CPUs, stale online masks, insufficient map entries, epoll registration failures, or malformed record types all produce errors or skipped buffers.

`parse_cpu_mask_str()` reallocates to `end + 1` bytes for a `bool` mask and uses range filling based on previous mask size. It expects monotonically sensible CPU mask ranges from sysfs; malformed, descending, negative, oversized, or empty masks produce errors.

Map value resizing for mmaped array maps depends on BTF datasec shape: the map value type must be a datasec, have at least one var, and end with an array whose element size divides the requested new size. If BTF adjustment fails after mmap resizing, the code clears map BTF key/value IDs to avoid stale metadata.

Skeleton helpers depend on generated skeleton ABI sizes. Older skeletons without map link fields skip struct_ops map auto-attachment. Subskeleton variable population does not report an error when a requested variable name is not found after scanning a datasec, so consumers must be aware that unresolved addresses could remain unchanged.

## Test Signals

Useful validation signals for this chunk include:

- Object lifecycle tests that open, prepare-only, load, unload, close, and error-close objects with programs, maps, externs, BTF, tokens, arena data, jump tables, USDT manager state, and mmaped map data.
- Program API tests for pre-load and post-load mutator behavior, program iteration skipping subprograms, instruction replacement including zero-length replacement, log buffer validation, func/line info access, and clone loading with caller option overrides.
- Section resolution tests for all built-in `SEC()` families, exact versus `+` versus trailing-slash matching, custom handler registration/unregistration, fallback handlers, and type/attach-name string helpers.
- BTF attach tests for vmlinux, module-qualified names, target-program BTF IDs, freplace targets, generated-loader deferred attach recording, missing BTF, missing symbols, and token-FD propagation.
- Map API tests for map FD/name lookup, internal real-name handling for `.data.*`/`.rodata.*`, resize of mmaped arrays with BTF datasec metadata, initial value sizing, inner-map FD replacement, exclusive-program validation, and typed map operation size checks including per-CPU maps and CPU flags.
- Link lifecycle tests for open/pin/unpin/destroy/disconnect/update-program, bpffs path errors, close-only detached links, and legacy perf links that must remove tracefs kprobe/uprobe events.
- Kprobe/uprobe tests covering modern PMU attach, forced perf attach, forced link attach, forced legacy attach, return probes, offsets, cookies, syscall wrapper detection, auto-attach section parsing, missing targets, wildcard multi-kprobe resolution, unique-match failures, and session mode.
- Uprobe path and symbol tests for PATH/LD_LIBRARY_PATH resolution, architecture library fallback paths, ELF symbol offsets, function patterns, explicit offsets, archive member offsets, compressed archive rejection, PID scoping, and ref-counter offset handling.
- Tracepoint/raw tracepoint/BTF tracing/LSM/freplace/iterator/cgroup/netns/sockmap/XDP/TCX/netkit/netfilter attach tests for loaded-FD validation, expected attach type, relative attach options, revision/options propagation, and unsupported kernel behavior.
- Struct_ops tests for relocation collection into function-pointer members, non-static or wrong-type program rejection, map update idempotence with `-EBUSY`, `BPF_F_LINK` and non-link attach modes, link map update, and associate-struct-ops errors.
- Perf-buffer tests for invalid page counts, wrong map types, CPU subset options, offline CPU skipping, map slot updates, epoll readiness, wrapped record copying, raw event callback precedence, sample/lost callbacks, consume without polling, buffer FD/accessor bounds, and cleanup deleting perf-event-array slots.
- CPU mask tests for single CPUs, ranges, comma/newline separation, empty masks, invalid ranges, descending ranges, malformed strings, too-large sysfs file reads, and cached possible CPU counts.
- Skeleton tests for open/load/attach/detach/destroy, missing generated map/program names, mmap pointer refresh after load including arena offset handling, autoattach disabled programs/maps, manually prefilled links, old skeleton map sizes, subskeleton BTF datasec variable lookup, and cleanup after partial failures.

## Cross-Chunk Notes

Earlier chunks for the same file contain object opening, ELF/BTF collection, relocation, map creation, program loading, and most pin/unpin definitions. This chunk should be reconciled with those earlier ranges because many functions here call helpers defined earlier, especially `bpf_object_post_load_cleanup()`, `bpf_object_unload()`, `bpf_map_mmap_sz()`, `kernel_supports()`, `load_module_btfs()`, ELF symbol resolution helpers, and section setup during object initialization.

The final per-file report should treat this range as libbpf's public API and runtime integration tail: it is where prepared object metadata becomes attached kernel links, map operations, perf-buffer consumers, and generated skeleton state.
