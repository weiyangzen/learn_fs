# Research Group subset-b-006572

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/gen.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/gen.c

`gen.c` implements the `bpftool gen` command family: BPF object linking, C skeleton generation, C subskeleton generation, and minimal CO-RE BTF generation. Its main public integration point is `do_gen()`, which dispatches `object`, `skeleton`, `subskeleton`, `min_core_btf`, and `help` through the shared `cmd_select()` table from `main.c`.

Important helpers normalize generated C identifiers (`sanitize_identifier()`, `get_obj_name()`, `get_map_ident()`, `get_datasec_ident()`), emit indentation-trimmed templates with `codegen()`, and print binary payloads as C escaped strings. Skeleton generation opens an ELF object with libbpf, counts maps/programs, emits `struct <obj>`, map/program/link handles, mmapable data-section structs, struct_ops shadow types, and open/load/attach/detach/destroy helpers. In `--use-loader` mode it calls `bpf_object__gen_loader()` and emits a loader-backed header that embeds generated instructions, loader data, optional program signatures, and map mmap finalization logic.

Subskeleton generation follows a different control flow: it opens the object with an empty object name, requires BTF, enumerates exported variables from mmapable data sections, and emits a `bpf_object_subskeleton` wrapper that resolves maps, programs, and variables against an already-open source object at runtime. `do_object()` uses `bpf_linker__new()`, `bpf_linker__add_file()`, and `bpf_linker__finalize()` for static object linking.

The BTF minimization lane builds a `btfgen_info` with original and markable BTF copies, records each object's CO-RE relocations via `bpf_core_calc_relo_insn()`, marks required types and selected composite members, then creates a compact BTF object with remapped type IDs and saves raw BTF bytes. State is mostly transient process memory plus generated stdout or output files; persistence is limited to linker output and minimized BTF output. Dependencies include libbpf object, BTF, BTF.ext, linker, loader, hashmaps, mmap, and optional signing. Main risks are generated C ABI drift, identifier collisions after sanitization, incorrect data-section padding on unusual BTF, loader/signing failures, and kernel/libbpf feature skew. Test signals should include compiling generated skeletons/subskeletons, loading sample objects with data/rodata/bss/kconfig/arena/struct_ops maps, `bpftool gen object` link tests, and `min_core_btf` validation against CO-RE relocation fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/iter.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/iter.c

`iter.c` implements `bpftool iter`, currently centered on `bpftool iter pin OBJ PATH [map MAP]`. The command loads an iterator-capable BPF object, attaches the first program as a BPF iterator, and pins the resulting `bpf_link` into bpffs. Its exported entry point is `do_iter()`, which dispatches `pin` and `help` through the common bpftool command selector.

The important control path is `do_pin()`. It requires an object file and pin path, optionally parses `map MAP` with `map_parse_fd(..., BPF_F_RDONLY)`, populates `union bpf_iter_link_info` for map-targeted iterators, opens the object with `bpf_object__open()`, loads it with `bpf_object__load()`, selects the first program via `bpf_object__next_program()`, attaches with `bpf_program__attach_iter()`, ensures bpffs is mounted for the target with `mount_bpffs_for_file()`, and pins the link with `bpf_link__pin()`.

State is short-lived: object, link, and optional map file descriptors are owned by this function and released on all labeled exit paths. Persistent state is only the pinned link at the requested bpffs path after success; the in-process `bpf_link` is destroyed after pinning. Dependencies include libbpf object/program/link APIs, `main.h` argument macros, map fd parsing from `map.c`/shared helpers, and bpffs mount helpers.

Risks are mostly operational: only the first program in the object is used, so multi-program objects depend on layout; map iterator setup only accepts one optional map target; attach failures are reported after load, so verifier diagnostics depend on global debug flags; and pinning needs bpffs permissions and mount behavior controlled by global options. Test signals include successful pinning of a simple task iterator, a map iterator using `map id` and `map pinned`, failure paths for objects with no programs, invalid map specs, bpffs mount refusal, and JSON help behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/jit_disasm.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/jit_disasm.c

`jit_disasm.c` provides the optional native disassembly backend used by program dump paths declared in `main.h` as `disasm_init()` and `disasm_print_insn()`. It supports two compile-time providers: LLVM disassembler (`HAVE_LLVM_SUPPORT`) and libbfd/opcodes (`HAVE_LIBBFD_SUPPORT`). If neither is enabled, `main.h` supplies a stub.

The LLVM path normalizes an explicit or default target triple, enables all AArch64 features for broad JIT instruction coverage, creates an `LLVMDisasmContextRef`, and disassembles instruction bytes with `LLVMDisasmInstruction()`. The libbfd path opens `/proc/self/exe` as the BFD context, optionally overrides architecture for offload targets, initializes `disassemble_info`, sets a custom address printer that adds `func_ksym`, and calls the selected opcode disassembler.

`disasm_print_insn()` is the shared loop. It creates the provider context, optionally starts a JSON array, finds source line records with `bpf_prog_linfo__lfind_addr_func()`, emits line info through BTF dump helpers, prints the current PC, disassembles one instruction, optionally emits raw opcodes, advances by the returned instruction length, and closes JSON/plain formatting. JSON output splits operation and operands with provider-specific print callbacks and uses the global `json_wtr`.

State is temporary except for the file-static `oper_count`, which tracks whether the current JSON instruction has operands. Dependencies include LLVM C APIs or BFD/dis-asm, libbpf BTF line-info helpers, `json_writer`, and bpftool globals. Risks include provider-specific operand tokenization, count values of zero causing loop termination after a partially emitted object, missing architecture support for offloaded images, and address formatting differences across binutils/LLVM versions. Test signals should compare JSON and plain output for JITed programs, opcodes on/off, BTF line-number emission, explicit architecture strings, zero-length images, and builds with LLVM-only, BFD-only, and no-disassembler configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/jit_disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.c

`json_writer.c` is a small streaming JSON emitter used throughout bpftool. It owns syntax mechanics: commas, object/array depth, optional pretty indentation, string escaping, scalar output, and common name/value helpers. The implementation backs the opaque `json_writer_t` from `json_writer.h` with `FILE *out`, `depth`, `pretty`, and `sep`.

Core helpers are `jsonw_eor()` for comma insertion, `jsonw_eol()`/`jsonw_indent()` for pretty whitespace, `jsonw_puts()` for C-style JSON string escapes, `jsonw_begin()` for `{`/`[`, and `jsonw_end()` for `}`/`]`. Public functions allocate and destroy writers, toggle pretty output, reset top-level separators, write property names, write raw formatted fragments, and write typed scalar values. Field helpers simply call `jsonw_name()` followed by the matching scalar writer.

Control flow is intentionally linear: callers must start/end objects and arrays in a balanced way, with `jsonw_destroy()` asserting `depth == 0`, appending a final newline, flushing, freeing, and nulling the caller's pointer. State is entirely in the writer instance, but many bpftool modules share the global `json_wtr`. The writer does not validate full JSON grammar beyond separator/depth mechanics and trusts `jsonw_printf()` callers to emit valid JSON fragments.

Dependencies are only libc, `stdio`, `stdarg`, `inttypes`, and the public header annotations. Risks include no Unicode escaping for control bytes beyond selected C escapes, assertions rather than recoverable errors on unbalanced output, raw `jsonw_printf()` misuse producing invalid JSON, and non-thread-safe shared output. Test signals include nested object/array formatting, pretty and compact output, all string escape cases, reset after a completed top-level value, scalar widths for signed/unsigned 64-bit fields, and intentionally unbalanced usage in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.h

`json_writer.h` declares bpftool's opaque streaming JSON writer API. It exposes `typedef struct json_writer json_writer_t;` without revealing layout, so callers can create, use, and destroy writers while implementation state remains private to `json_writer.c`.

The API groups into lifecycle (`jsonw_new()`, `jsonw_destroy()`), formatting (`jsonw_pretty()`, `jsonw_reset()`), property naming (`jsonw_name()`), values (`jsonw_string()`, `jsonw_bool()`, integer and floating writers, `jsonw_null()`, `jsonw_printf()`, `jsonw_vprintf_enquote()`), field shortcuts (`jsonw_string_field()`, `jsonw_uint_field()`, and related helpers), and collection delimiters (`jsonw_start_object()`, `jsonw_end_object()`, `jsonw_start_array()`, `jsonw_end_array()`). The `__printf` annotations allow compile-time checking of printf-style wrappers.

This header is an integration point for most command modules: maps, links, netlink dumping, perf, disassembly, PID references, and `main.c` all use the same writer contract when `json_output` is enabled. It also defines `jsonw_err_handler_fn`, but this implementation does not currently expose a setter, so it is effectively reserved compatibility surface.

There is no persistence or global state in the header itself; it defines the contract used by the global `json_wtr` in `main.c`. Dependencies include standard C bool/stdint/stdarg/stdio and Linux compiler attributes. Risks are API misuse rather than header behavior: mismatched start/end calls assert in the implementation, raw formatted JSON can bypass escaping, and callers must honor the writer lifetime. Test signals should compile modules with format-string warnings enabled, verify all declared functions have implementation or intentional conditional exclusion, and exercise representative bpftool JSON paths to catch contract drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/json_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/link.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/link.c

`link.c` implements `bpftool link` operations: listing/showing BPF links, pinning links, and detaching links. Its entry point `do_link()` dispatches `show`, `list`, `pin`, `detach`, and `help`. The module translates `bpf_link_info` into plain or JSON output for many link types, including raw tracepoints, tracing, cgroup, iter, netns, netfilter, TCX, netkit, sockmap, XDP, struct_ops, kprobe/uprobe multi, and perf-event links.

The main show path builds optional pinned-path and PID-reference tables, opens a requested link by `id` or `pinned`, or enumerates IDs with `bpf_link_get_next_id()`. `do_show_link()` calls `bpf_link_get_info_by_fd()` repeatedly, first discovering variable-length fields, then supplying buffers for target names, kprobe addresses/cookies, uprobe offsets/ref-counter offsets/cookies/path, and perf-event names. The final rendering splits into `show_link_close_json()` and `show_link_close_plain()`.

Important support APIs resolve associated program info, map iterator/cgroup/task target details, netfilter names, perf-event names, and multi-kprobe symbols. Multi-kprobe output sorts address/cookie pairs and maps them through kernel symbols, with a special x86 IBT adjustment that treats `symbol + 4` as an entry match when kernel IBT is enabled. Persistent behavior is limited to `pin` creating bpffs pins and `detach` mutating kernel link attachment state; show paths are read-only aside from opening fds and loading symbol tables.

Dependencies include libbpf link/prog APIs, hashmaps for pin/reference tables, `pids.c`, pinned object helpers, kernel symbol helpers from the xlated dumper path, netfilter constants, perf event constants, and JSON writer. Risks include variable-length info retry errors, stale IDs disappearing during enumeration, symbol matching gaps for kprobe multi, JSON array closure if helper returns early, and global `errno` influencing final return. Test signals should cover every supported link type, pinned and unpinned output, PID references, detach failure/success, kprobe multi with and without IBT, unknown enum values, and old kernels lacking newer `bpf_link_info` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.c

`main.c` is the bpftool process entry point and global command dispatcher. It defines global options and state declared in `main.h`, including `json_wtr`, `json_output`, `pretty_output`, pinned/path display flags, verifier logging, relaxed map compatibility, loader/signing flags, base BTF, and object reference tables.

Startup sets line-buffered stdout, resets libcap-induced `errno` noise when relevant, initializes defaults, then parses global options with `getopt_long()`. `-j/-p` allocate and configure the shared JSON writer, `-d` enables libbpf debug logging and verifier logs, `-B` parses base BTF, `-L` enables loader skeleton generation, `-S` enables signing and implies loader mode, and `-i/-k` provide signing material. It validates signing option combinations before dispatching either `version` or the selected object command.

`cmd_select()` implements prefix-based command matching and handles weak commands missing in bootstrap builds. It records the last argv/help function so `usage()` can call context-appropriate help before exiting through `clean_and_exit()`. `do_batch()` reads command files or stdin, strips comments, handles backslash continuations, tokenizes whitespace and quoted words with `make_args()`, optionally wraps each command and output in JSON, then reuses the same dispatcher.

State persists only for the process lifetime except commands invoked through batch may mutate kernel/BPF state. Dependencies include libbpf, BTF, hashmaps, generated weak command symbols from other modules, JSON writer, and helper functions declared in `main.h`. Risks include permissive prefix matching ambiguity, simple batch parsing without shell-like escaping, JSON output integrity when nested commands emit top-level values, global state reuse across batch commands, and signing option validation drift. Test signals include help/version in plain and JSON modes, bootstrap builds, ambiguous prefixes, batch files with comments/continuations/quotes, invalid global options, base BTF parse failure, and signed loader option validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.h

`main.h` is the shared internal contract for bpftool command modules. It normalizes feature macros, includes libbpf/BPF/BTF/hashmap and JSON writer headers, poisons kernel-only integer typedefs, and exposes small pointer conversion helpers for UAPI fields that pass user pointers as `__u64`.

The header defines command-line macros (`NEXT_ARG`, `NEXT_ARGP`, `GET_ARG`, `REQ_ARGS`, `BAD_ARG`) used throughout command implementations, common help grammar strings, `enum bpf_obj_type` synchronized with the PID iterator BPF program, global process state from `main.c`, logging functions, command dispatch APIs, object pin/open helpers, parsing helpers for programs/maps/links, JSON/plain device printing helpers, and optional disassembly hooks. It also declares weak command entry points so bootstrap builds can omit nonessential objects while retaining a common dispatch table.

Important shared types include `struct cmd`, `struct obj_ref`, and `struct obj_refs`. `obj_refs` carries PID reference arrays plus optional BPF cookie data for map/link/prog/BTF references collected through `pids.c`. The disassembly declarations are conditionally real when LLVM or BFD support is compiled in and stubbed otherwise, keeping callers buildable.

There is no direct persistence in the header, but it defines access to persistent kernel state through pinning, object fd opening, map/prog parsing, and command entry points. Dependencies are broad by design: most command files include this header. Risks include macro side effects on local `argc/argv`, weak symbol behavior differing between bootstrap and full builds, accidental use of poisoned typedefs in included implementation files, and global state coupling. Test signals should include full and bootstrap builds, modules compiled with the poisoned typedefs, argument parser edge cases, command dispatch against weak-null functions, disassembler-disabled builds, and PID reference output integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/map.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/map.c

`map.c` implements `bpftool map`: show/list, create, dump, update, lookup/peek, getnext, delete, pin, event_pipe, push/enqueue, pop/dequeue, freeze, and help. `do_map()` dispatches these subcommands. The module is both an inventory renderer and a mutation interface for kernel BPF maps.

Map type helpers classify per-CPU maps, map-in-map maps, and program arrays. Element parsing supports `key`, `value`, optional `hex`, and update flags `any`, `exist`, `noexist`. For map-in-map and prog-array values, `parse_elem()` resolves nested map or program fds and writes the fd into the value slot; per-CPU values are duplicated across all possible CPUs with correct 8-byte stride. `alloc_value()` and `alloc_key_value()` size buffers according to map type.

Show paths enumerate map IDs or selected fds, optionally build pinned-path and PID-reference tables, fetch fdinfo memlock/frozen/owner metadata, and render plain or JSON output. Dump/lookup paths can use BTF formatting: `get_map_kv_btf()` loads kernel or map BTF, `do_dump_btf()` walks typed key/value data, and plain BTF output creates a temporary pretty JSON writer. Mutation paths call `bpf_map_update_elem()`, `bpf_map_delete_elem()`, `bpf_map_lookup_and_delete_elem()`, `bpf_map_freeze()`, and `bpf_map_create()` followed by pinning.

Persistent effects include creating pinned maps, changing map elements, popping/dequeuing queue/stack data, and freezing maps. Dependencies include libbpf map/BTF APIs, shared fd parsers, JSON writer, `pids.c`, pinned object tables, `map_perf_ring.c`, CPU/page helpers, and bpffs helpers. Risks include double-close hazards around fd ownership, BTF fallback differences between JSON/plain output, races while enumerating IDs, unsupported map value reads such as reuseport sockarray sizing, fd lifetime warnings for prog arrays, and global `btf_vmlinux` cleanup. Test signals should cover all subcommands, per-CPU maps, BTF and no-BTF maps, map-in-map/prog-array updates, JSON/plain parity, pinned/PID metadata, queue/stack operations, invalid byte parsing, and old-kernel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/map_perf_ring.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/map_perf_ring.c

`map_perf_ring.c` implements `bpftool map event_pipe`, exposed as `do_event_pipe()` and dispatched from `map.c`. It subscribes to a `BPF_MAP_TYPE_PERF_EVENT_ARRAY` and prints BPF perf-event output records until interrupted.

The command first parses a map fd and `bpf_map_info` with `map_parse_fd_and_info()`, verifies the map type, then parses optional paired `cpu N index M` arguments. Without explicit CPU/index it subscribes to all CPUs; with explicit values it configures a one-entry raw perf buffer using `perf_buffer_raw_opts.cpus` and `map_keys`. The perf event attributes request software `PERF_COUNT_SW_BPF_OUTPUT` with raw data and timestamps.

`print_bpf_output()` handles the callback. It interprets records as `PERF_RECORD_SAMPLE` or `PERF_RECORD_LOST`, computes the map index from either callback CPU or requested index, and emits JSON objects or plain text. Samples include timestamp and raw data bytes; lost records include ID and count. `do_event_pipe()` installs SIGINT/SIGHUP/SIGTERM handlers that set a volatile `stop` flag, starts a JSON array if needed, polls with `perf_buffer__poll()` every 200 ms, and frees the perf buffer and map fd on exit.

State persists only while the process runs; the map is not mutated except perf-event-array slots may be opened by libbpf for polling. Dependencies include libbpf raw perf buffer APIs, Linux perf event structures, shared map parsers, `fprint_hex()`, JSON writer, and signal handling. Risks include signal safety of the handler's `fprintf()`, indefinite blocking until a signal, strict requirement that CPU and index are specified together, event type assumptions when casting the header, and JSON arrays not closing on poll error paths. Test signals include all-CPU and single-CPU subscriptions, sample and lost events, invalid CPU/index parsing, wrong map type, interrupted termination in plain and JSON modes, and poll errors such as map closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/map_perf_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/net.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/net.c

`net.c` implements `bpftool net`: network attachment inventory plus attach/detach for XDP and TCX programs. `do_net()` dispatches `show`, `list`, `attach`, `detach`, and `help`. It covers XDP, classic TC BPF filters/actions, TCX, netkit, flow dissector, and netfilter link inventory.

Inventory starts by optionally parsing `dev <devname>`, querying flow dissector attachment through `/proc/self/ns/net`, opening a NETLINK_ROUTE socket with extended ACKs, and emitting a root object/array. `netlink_get_link()` dumps interfaces and delegates to `dump_link_nlmsg()`, which records devices and calls `do_xdp_dump()` from `netlink_dumper.c`. For each device, `show_dev_tc_bpf()` uses `bpf_prog_query_opts()` for TCX/netkit locations, while `show_dev_tc_bpf_classic()` walks classes, qdiscs, root/ingress/egress handles, and filters through route netlink. `show_link_netfilter()` enumerates all BPF links, filters netfilter links, sorts them by pf/hook/priority/flags, and renders them with link.c helpers.

Attach/detach parsing maps string prefixes to `enum net_attach_type`. XDP attach uses `bpf_xdp_attach()` with overwrite/generic/driver/offload flags. TCX attach uses `bpf_prog_attach_opts()` with optional `BPF_F_BEFORE` for prepend, or `bpf_prog_attach()` otherwise; detach uses `bpf_prog_detach()` on the interface index.

Persistent effects are limited to attaching or detaching programs from network devices. Show mode is read-only aside from temporary sockets/fds. Dependencies include route netlink, libbpf netlink attribute parsing, BPF prog query/attach APIs, `netlink_dumper`, `main.h` program parsers, and link netfilter renderers. Risks include sequence numbers based on `time(NULL)`, disappearing devices/programs during scans, classic TC handle coverage gaps, prefix ambiguity in attach types, wrong signedness in error reporting from libbpf APIs, and feature skew on old kernels. Test signals include JSON/plain `show`, filtered device show, XDP mode flags, TCX prepend, detach behavior, flow dissector old-kernel fallback, netfilter sorting, and netlink parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.c

`netlink_dumper.c` contains focused renderers for BPF-related netlink attributes discovered by `net.c`: XDP attachment data on links and classic TC BPF filter/action data. It exports `do_xdp_dump()` and `do_filter_dump()`.

The XDP path parses nested `IFLA_XDP` attributes, skips missing or `XDP_ATTACHED_NONE` state, and emits device name, ifindex, attachment mode, and program IDs. Multi-attachment mode produces generic/driver/offload entries in a JSON array or plain nested output; single mode emits one mode/id pair. This relies on `libbpf_nla_parse_nested()` and `libbpf_nla_getattr_*()` helpers.

The TC path handles classifier and action metadata. `do_filter_dump()` checks that `TCA_KIND` is `bpf`, starts a formatted object, emits device identity and kind, then calls `do_bpf_filter_dump()` for filter name, ID, and optional action list. Actions are parsed by priority through `TCA_ACT_*`; only action kind `bpf` is rendered, with action name and ID taken from `TCA_ACT_BPF_*` attributes.

There is no persistence; the file only translates netlink snapshots to stdout/JSON. Dependencies are Linux rtnetlink and tc BPF attribute definitions, libbpf netlink attribute helpers, shared `json_output`/`json_wtr`, and formatting macros from `netlink_dumper.h`. Risks include silent skips for unsupported non-BPF actions, parse failures returning libbpf netlink parse errors, plain formatting tightly coupled to macro punctuation, and assumptions that string attributes are present and NUL-terminated. Test signals should include XDP none/single/multi modes, TC BPF filters with and without actions, mixed non-BPF actions, malformed nested attributes, and JSON/plain parity under `bpftool net show`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.h

`netlink_dumper.h` is a macro formatting layer shared by `net.c` and `netlink_dumper.c`. It hides the repeated branch between JSON output through `json_wtr` and plain text output through `fprintf(stdout, ...)`.

The macros cover object and nested-object delimiters (`NET_START_OBJECT`, `NET_START_OBJECT_NESTED`, `NET_START_OBJECT_NESTED2`, `NET_END_OBJECT*`), array delimiters (`NET_START_ARRAY`, `NET_END_ARRAY`), and scalar emitters for named or bare unsigned integers and strings (`NET_DUMP_UINT`, `NET_DUMP_UINT_ONLY`, `NET_DUMP_STR`, `NET_DUMP_STR_ONLY`). Each macro references the global `json_output` flag and global `json_wtr` declared in `main.h`.

State and persistence are absent; macro expansion writes immediately to the active output stream. The header is an integration point that keeps net-related plain and JSON structures close enough that the implementation can call one macro in each logical output position. Dependencies are implicit: including files must already have access to `json_output`, `json_wtr`, `json_writer` functions, and `stdout`.

Risks are typical of multi-statement macros: no `do { } while (0)` wrapper, possible surprising control-flow interactions if used under unbraced `if` statements, no type checking for format/value pairs beyond compiler printf checks on `fprintf`, and tight coupling of plain punctuation to call-site order. Test signals should focus on net command output shape, especially nested arrays/objects, empty arrays, plain newline placement, and compiling with warnings around macro call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/perf.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/perf.c

`perf.c` implements `bpftool perf show|list`, which scans process file descriptors and reports perf-event fds that have BPF programs attached. Its entry point is `do_perf()`.

Before scanning, `has_perf_query_support()` probes `bpf_task_fd_query()` on an arbitrary directory fd. The code treats errno 524 (`ENOTSUPP`) from a query with no attachment as evidence that the syscall feature exists, caches support in `perf_query_supported`, and emits a hint for non-root or unsupported kernels otherwise. `do_show()` then starts a JSON array if requested and calls `show_proc()`.

`show_proc()` opens `/proc`, filters numeric PID directories, opens each `/proc/<pid>/fd`, filters numeric fd entries, and calls `bpf_task_fd_query(pid, fd, ...)`. Successful queries are rendered by `print_perf_json()` or `print_perf_plain()`. The output distinguishes raw tracepoint, tracepoint, kprobe/kretprobe, uprobe/uretprobe, and includes function/file names, offsets, addresses, and program IDs according to fd type.

State is process-local cache plus transient directory scans; no persistent kernel state is changed. Dependencies include procfs visibility, `bpf_task_fd_query()`, JSON writer, pid/fd parsing via ctype, and bpftool globals. Risks include permission-sensitive visibility, processes/fds disappearing during scan, the hard-coded errno 524 portability assumption, silent skipping of query errors after the initial probe, and incomplete output for unknown fd types. Test signals include root and non-root runs, kernels with and without task fd query support, live kprobe/uprobe/tracepoint attachments, disappearing processes during scan, JSON/plain output, and fd names with large numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/pids.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/pids.c

`pids.c` builds and emits tables of processes that reference BPF objects. When skeleton support is disabled, it provides no-op or `-ENOTSUP` implementations. In full builds it uses the generated `pid_iter.bpf` skeleton to run a BPF iterator over kernel state and collect references into a libbpf hashmap.

The main API is `build_obj_refs_table(struct hashmap **map, enum bpf_obj_type type)`. It creates a hashmap keyed by object ID, raises rlimits, opens the PID iterator skeleton, sets `skel->rodata->obj_type`, suppresses libbpf output unless verifier logging is enabled, loads and attaches the iterator, creates a read fd with `bpf_iter_create()`, then reads fixed-size `pid_iter_entry` records until EOF. Each record is merged by `add_ref()`, which deduplicates by PID for the same object ID, grows a `struct obj_refs` array, stores command names, and preserves optional BPF cookie data.

`delete_obj_refs_table()` frees nested arrays and hashmap entries. `emit_obj_refs_json()` and `emit_obj_refs_plain()` look up a specific object ID and emit optional `bpf_cookie` plus PID/comm pairs in the calling module's output format. This integrates with map/link/prog show paths through weak declarations in `main.h`.

State is transient and derived from a snapshot stream; no persistent state is changed. Dependencies include generated BPF skeletons, `skeleton/pid_iter.h`, libbpf BPF iterator support, hashmaps, global verifier logging, and JSON writer. Risks include kernels without BPF iterator support silently producing no refs, memory allocation failures dropping individual refs, fixed comm truncation, deduplication by PID only, invalid iterator record sizes, and cleanup leaks if early skeleton open failures leave the hashmap allocated. Test signals include builds with and without skeletons, supported and unsupported kernels, refs for maps/links/progs/BTF, duplicate PID records, BPF cookie output, malformed short reads, and JSON/plain callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/pids.c -->
