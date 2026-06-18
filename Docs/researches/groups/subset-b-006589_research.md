# Research: subset-b-006589

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.c -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.c

Purpose: Implements libbpf/kernel shared BPF CO-RE relocation logic. It parses `struct bpf_core_relo` access strings against local BTF, matches them against target BTF candidate types, computes relocation values, and patches BPF instructions.

Important APIs/functions: `bpf_core_parse_spec()` converts raw access strings into low-level and high-level `bpf_core_spec` forms. `bpf_core_calc_relo_insn()` is the main relocation resolver. `bpf_core_patch_insn()` mutates ALU, LDIMM64, LDX, ST, and STX instructions or poisons unreachable instructions. `__bpf_core_types_are_compat()` and `__bpf_core_types_match()` implement compatibility and exact-match relations. `bpf_core_format_spec()` creates diagnostic text.

Control flow: relocation starts by parsing the local spec, handling `TYPE_ID_LOCAL` specially, then iterating candidate target BTF types. Candidates are pruned to those matching by essential name and structural/accessor compatibility. Each matching candidate yields a candidate relocation result; all candidates must agree on offset and value to avoid ambiguity. Missing candidates may intentionally produce zero/existence false or poison-on-use depending on relocation kind.

State/persistence: No durable storage; it mutates candidate lists in memory and patches BPF instruction arrays. Scratch specs and result structs are caller-owned.

Dependencies/integration: Depends on BTF helpers, libbpf logging/error conventions, Linux BPF instruction encoding, CO-RE relocation enums, and endian behavior. Used by libbpf object loading and by kernel verifier-side code under `__KERNEL__`.

Risks: Candidate ambiguity, anonymous type rejection, too-deep access specs, bitfield layout uncertainty, unsafe memory-size adjustment, and poisoned instructions that only fail if reachable. A duplicated comment terminator is present before `bpf_core_patch_insn()` in this checkout and should be compile-tested.

Test signals: CO-RE selftests should cover field offsets/sizes, type existence/matches, enum64 values, anonymous types, flexible arrays, bitfields, 32-bit pointer-size adjustments, unsupported reloc kinds, and verifier rejection of reachable poisoned instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.h -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.h

Purpose: Declares the CO-RE relocation data structures and internal resolver/patcher APIs shared by libbpf and kernel builds.

Important APIs/types: `struct bpf_core_cand` and `struct bpf_core_cand_list` model target BTF type candidates. `struct bpf_core_accessor` and `struct bpf_core_spec` represent high-level and raw accessor paths, capped by `BPF_CORE_SPEC_MAX_LEN`. `struct bpf_core_relo_res` carries original/new relocation values, validation flags, poison decision, and memory-size adjustment metadata. Public declarations expose parse, format, calculate, patch, and type-compatibility helpers.

Control flow: The header has no runtime flow, but it defines the contract used by `relo_core.c`: parse a local spec, match candidates, compute a `bpf_core_relo_res`, then patch an instruction.

State/persistence: All state is transient and caller-owned. `bpf_core_spec` embeds fixed-size arrays, so callers avoid allocation but must honor the maximum depth.

Dependencies/integration: Includes `<linux/bpf.h>` for relocation kinds and BPF instruction types. It is consumed by libbpf object relocation code and by kernel-side BPF verifier support.

Risks: ABI/layout drift between this header and implementation can corrupt relocation behavior. `BPF_CORE_SPEC_MAX_LEN` rejects very deep access paths with `-E2BIG`. Callers must supply enough scratch `bpf_core_spec` storage for resolver internals.

Test signals: Build tests should include user and kernel include contexts. Relocation tests should validate all declared result flags, especially `poison`, `validate`, and memory-size fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/ringbuf.c -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/ringbuf.c

Purpose: Implements libbpf ring buffer consumers for `BPF_MAP_TYPE_RINGBUF` and user-space producers for `BPF_MAP_TYPE_USER_RINGBUF`.

Important APIs/functions: `ring_buffer__new()`, `ring_buffer__add()`, `ring_buffer__poll()`, `ring_buffer__consume[_n]()`, `ring_buffer__free()`, `ring__*()` accessors, `user_ring_buffer__new()`, `user_ring_buffer__reserve[_blocking]()`, `user_ring_buffer__submit()`, and `user_ring_buffer__discard()`.

Control flow: Consumer setup validates map type, mmaps the writable consumer page and read-only producer/data pages, and registers map FDs with epoll. Consumption reads producer/consumer positions with acquire/release barriers, walks committed records, skips discarded records, invokes callbacks, and advances consumer position. User ring buffer setup mmaps consumer read-only plus producer/data read-write pages; reserve checks size, available space, writes a busy header, advances producer position, and submit/discard clears busy with optional discard.

State/persistence: State is in mmapped kernel ring pages plus heap arrays of rings/events. No disk persistence. Epoll FDs and map FDs tie lifetime to kernel objects.

Dependencies/integration: Uses BPF map info syscalls, `mmap`, `epoll`, memory barriers, libbpf option validation, and BPF ring buffer header/flag constants.

Risks: Correctness depends on memory ordering and exact kernel ring layout. Large `max_entries` is guarded against `size_t` overflow. In this checkout `ringbuf_process_ring()` calls `sample_cb` twice for each non-discarded sample, which can duplicate side effects and should fail callback-count tests.

Test signals: Tests should cover wrong map types, wraparound records, busy/discarded records, callback errors, epoll wakeups, user reserve ENOSPC/E2BIG paths, blocking timeout behavior, and callback invocation count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/ringbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/skel_internal.h -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/skel_internal.h

Purpose: Provides the runtime support header embedded by generated lightweight BPF skeletons (`*.lskel.h`) for both user-space and kernel/preload contexts.

Important APIs/types: `struct bpf_map_desc`, `struct bpf_prog_desc`, `struct bpf_loader_ctx`, and `struct bpf_load_and_run_opts` define loader I/O. Inline wrappers include `skel_sys_bpf()`, map operations, raw tracepoint/link creation, map data preparation/finalization/freeing, and `bpf_load_and_run()`.

Control flow: Generated skeletons allocate context/data, create a loader array map, populate/freeze it in user space, load a `BPF_PROG_TYPE_SYSCALL` loader program, run it with `BPF_PROG_RUN`, then close transient FDs. Map data handling differs by build: kernel uses `kvmalloc` and direct array value access, user space uses anonymous mmap then MAP_FIXED remap to the BPF map.

State/persistence: Loader state is transient. File descriptors keep maps/programs alive while open. Generated skeleton structures store map/prog FDs and mapped data pointers.

Dependencies/integration: Integrates with raw `bpf()` syscall, generated bpftool skeleton code, optional signatures/keyrings, kernel-only close/allocation APIs, and userspace mmap.

Risks: This is explicitly feature/layout dependent. Incorrect `union bpf_attr` sizing, MAP_FIXED misuse, unsupported signatures in kernel mode, or map-data lifetime confusion can break skeleton loading. `skel_closenz()` ignores fd 0, which is intentional but can surprise callers.

Test signals: Generated skeleton load/run tests should exercise user and kernel modes, rodata/bss remapping, loader error strings, signature/keyring paths, map freeze/info calls, and cleanup after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/skel_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/strset.c -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/strset.c

Purpose: Implements a compact string set backed by contiguous NUL-terminated string data and a hashmap from string offset to itself.

Important APIs/functions: `strset__new()` optionally imports existing string data and indexes unique strings. `strset__add_str()` appends if unique and returns the offset. `strset__find_str()` returns an existing offset without committing the temporary appended bytes. `strset__data()` and `strset__data_size()` expose the packed data.

Control flow: Hash/equality callbacks interpret keys as offsets into `strs_data`. Adds temporarily copy the candidate string to the current end so the hashmap can compare by offset, then either return an existing offset or commit by increasing `strs_data_len`.

State/persistence: Heap-owned buffer and hashmap persist until `strset__free()`. Returned offsets are stable as long as the set lives, even if the backing buffer reallocates.

Dependencies/integration: Uses libbpf `hashmap`, `str_hash()`, and `libbpf_add_mem()` growth limits. Used by libbpf code needing BTF/string-table style deduplication.

Risks: Initial data must be a valid sequence of NUL-terminated strings; malformed data can walk past the buffer during `strlen`. `strset__find_str()` may grow capacity even on misses. Offset 0 is documented as found only by `>0`, but valid string tables often use offset 0 for empty string, so callers must interpret return values carefully.

Test signals: Cover duplicate import, duplicate add, max-size exhaustion, malformed init data, empty strings, offset stability after realloc, and `find` miss behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/strset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/strset.h -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/strset.h

Purpose: Declares the opaque libbpf string-set interface implemented by `strset.c`.

Important APIs/types: `struct strset` is opaque. `strset__new()` creates a set with maximum data size and optional initial data. `strset__free()` releases it. `strset__data()`/`strset__data_size()` expose packed storage. `strset__find_str()` and `strset__add_str()` return offsets or negative errors.

Control flow: Header-only flow is limited to lifecycle contract: allocate, add/find strings, consume packed data, free.

State/persistence: The set owns all data internally. Callers should not retain the `strset__data()` pointer across operations that may grow the buffer unless the implementation contract is checked.

Dependencies/integration: Includes `<stdbool.h>` and `<stddef.h>`; paired with libbpf hashmap internals in the C file.

Risks: API uses integer offsets and negative errno values; offset 0 and error handling need caller care. Opaque type hides mutation/growth behavior.

Test signals: Compile users against the header alone and test error handling for `ERR_PTR` returns from `strset__new()` plus negative returns from find/add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/strset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.bpf.h -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.bpf.h

Purpose: Provides BPF-side helpers, maps, and macros for libbpf USDT probe programs.

Important APIs/types: `struct __bpf_usdt_arg_spec` and `struct __bpf_usdt_spec` mirror user-space `usdt.c`. Weak maps `__bpf_usdt_specs` and `__bpf_usdt_ip_to_spec_id` hold argument specifications and fallback IP-to-spec mappings. Helpers include `bpf_usdt_arg_cnt()`, `bpf_usdt_arg_size()`, `bpf_usdt_arg()`, `bpf_usdt_cookie()`, and `BPF_USDT()` handler wrapper.

Control flow: Runtime lookup obtains a spec ID from BPF cookie when available, otherwise from current IP. Argument fetch validates bounds, decodes constant/register/register-deref/SIB modes, reads pt_regs or user memory, applies endian-size normalization and sign extension, and returns a `long`.

State/persistence: Persistent state is in BPF maps populated by libbpf during attach. The header itself is weak-map based so user objects include support maps automatically.

Dependencies/integration: Depends on BPF helpers, tracing register macros, kernel config extern `LINUX_HAS_BPF_COOKIE`, and exact layout agreement with `usdt.c`.

Risks: Layout drift between BPF and user-space structs breaks argument decoding. Unsupported arch/register encodings are rejected in user space. Without BPF cookie support, IP map sizing and collisions matter. BPF verifier bounds are protected by `barrier_var()`.

Test signals: USDT selftests should cover all arg modes, signed and unsigned 1/2/4/8-byte values, big/little endian behavior, BPF cookie and IP-map paths, cookie retrieval, argument count/size helpers, and `BPF_USDT()` macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.c -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.c

Purpose: Implements libbpf user-space USDT discovery, argument-spec parsing, BPF map population, and uprobe attachment.

Important APIs/functions: `usdt_manager_new/free()` creates per-`bpf_object` state and feature probes. `usdt_manager_attach_usdt()` is the attach entry point. `collect_usdt_targets()` parses ELF notes and resolves probe/semaphore offsets. `parse_usdt_note()`, `parse_usdt_spec()`, and architecture-specific `parse_usdt_arg()` convert SystemTap notes into BPF-side specs. `bpf_link_usdt_*()` handles detach/deallocation.

Control flow: Attach opens and validates ELF, normalizes PID, scans `.note.stapsdt`, resolves ET_EXEC/ET_DYN file offsets and optional process VMAs, handles `.stapsdt.base` prelink correction, validates semaphore support, parses argument specs, deduplicates specs within one logical attach, updates spec and IP maps, then attaches either uprobe-multi or individual uprobes. Detach destroys links, removes IP map entries when needed, and returns spec IDs to the manager free list.

State/persistence: `usdt_manager` persists per object, tracking maps, feature flags, next/free spec IDs. `bpf_link_usdt` persists per attach with spec IDs and child links. BPF maps persist spec/IP data for loaded programs.

Dependencies/integration: Uses libelf/gelf, `/proc/<pid>/maps`, BPF map APIs, uprobe attach APIs, kernel feature probes, hashmap, architecture-specific `pt_regs` layouts, and SystemTap SDT note format.

Risks: Unsupported ELF class/endianness/type, missing notes, shared-library attachment without cookies and PID, semaphore refcount kernel support, IP collisions, spec-map exhaustion, arch parser gaps, and SIB/register syntax coverage. NOP optimization adjusts offsets on x86_64 and needs instruction validation.

Test signals: Tests should cover ET_EXEC and ET_DYN, PID 0/-1, container `/proc/<pid>/root` paths, prelink base adjustment, semaphore probes, uprobe-multi and fallback links, spec dedup/free-list reuse, map-update failures, each supported architecture parser, too many args, invalid sizes, and unsupported arch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/zip.c -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/zip.c

Purpose: Implements a small read-only ZIP archive reader for locating entries in simple non-ZIP64 archives.

Important APIs/functions: `zip_archive_open()` opens, sizes, mmaps, and parses central-directory metadata. `zip_archive_find_entry()` scans central-directory records for a named file and returns local-file data. `zip_archive_close()` unmaps and frees. Internal helpers validate EOCD, central-directory headers, local-file headers, and bounds via `check_access()`.

Control flow: Open searches backwards from the end for EOCD, validates comment length and central-directory range, rejects multi-disk/ZIP64 markers, then records central-directory offset and record count. Lookup iterates central-directory file headers, filters encrypted/data-descriptor entries, compares exact non-NUL names, and resolves the local header to data pointer/length.

State/persistence: Archive state is a private mmap plus central-directory coordinates. Entry results point into the mmap and are valid until close.

Dependencies/integration: Uses POSIX open/lseek/mmap/munmap and libbpf error-pointer style. `zip.h` exposes the archive and entry types.

Risks: No decompression is performed; callers must inspect `compression`. ZIP64, streaming descriptors, encryption, and multi-part archives are unsupported. All offset arithmetic is guarded, but packed unaligned structs rely on compiler attributes and host endian matching ZIP little-endian assumptions.

Test signals: Test empty/corrupt archives, EOCD comments, unsupported ZIP64/multi-disk/data-descriptor/encrypted entries, duplicate names, compressed vs stored entries, truncated central/local headers, large sizes near `UINT32_MAX`, and result pointer lifetime after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/zip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/zip.h -->
## sources/distributed-fs/ceph-client/tools/lib/bpf/zip.h

Purpose: Declares the minimal libbpf ZIP reader API.

Important APIs/types: Opaque `struct zip_archive`; `struct zip_entry` with compression method, non-NUL entry name/length, data pointer/length, and data offset; lifecycle functions `zip_archive_open()`, `zip_archive_close()`, and lookup `zip_archive_find_entry()`.

Control flow: Callers open an archive, find entries by exact name, then close the archive after using returned data pointers.

State/persistence: Entry pointers are borrowed from the archive mapping and are not independently owned.

Dependencies/integration: Includes Linux integer types and pairs with `zip.c`. Comments document unsupported features.

Risks: Header comment says open returns NULL on error, while implementation returns `ERR_PTR()`. Callers must follow implementation/libbpf error-pointer conventions or risk dereferencing error values. Entry names are explicitly not NUL-terminated.

Test signals: Compile tests should validate callers use `IS_ERR`/`PTR_ERR`; API tests should check non-NUL names and compression handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/zip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/cmdline.c -->
## sources/distributed-fs/ceph-client/tools/lib/cmdline.c

Purpose: Provides `memparse()`, a kernel-style parser for numeric memory-size strings with binary suffixes.

Important APIs/functions: `memparse(const char *ptr, char **retptr)` parses a base-0 integer using `strtoll`, then applies cascading left shifts for suffixes `K`, `M`, `G`, `T`, `P`, and `E` in either case.

Control flow: After parsing the numeric prefix, a switch deliberately falls through from larger suffixes to smaller suffixes, shifting by 10 each step. It advances `endptr` only when a recognized suffix is consumed, then optionally returns the final parse position.

State/persistence: Stateless.

Dependencies/integration: Uses libc `strtoll` and local `fallthrough` annotation. Tools can use it to parse kernel-like size options.

Risks: Overflow is unchecked during shifts. Negative text can pass through `strtoll` and then convert to unsigned result. Suffixes are binary powers, not decimal SI.

Test signals: Cover bare values, hex/octal prefixes, each suffix and case, trailing garbage and `retptr`, overflow/negative inputs, and empty strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/ctype.c -->
## sources/distributed-fs/ceph-client/tools/lib/ctype.c

Purpose: Provides the kernel `_ctype` lookup table for tools code using Linux ctype macros.

Important APIs/types: Defines global `const unsigned char _ctype[]` with classification flags such as control, space, punctuation, digit, uppercase/lowercase, and hex.

Control flow: No executable flow; consumers index the table through `<linux/ctype.h>` macros.

State/persistence: Read-only global data.

Dependencies/integration: Includes Linux ctype/compiler headers. Supports tools code that wants kernel-compatible character classification without libc ctype locale behavior.

Risks: Classification is fixed and ASCII-oriented. Values above 127 are classified according to this table, not locale. Table length/order must match kernel macro expectations.

Test signals: Unit tests should compare digits, hex letters, spaces, punctuation, control characters, and high-bit bytes against expected Linux macro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/ctype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/find_bit.c -->
## sources/distributed-fs/ceph-client/tools/lib/find_bit.c

Purpose: Implements generic bitmap search helpers for tools builds lacking architecture overrides.

Important APIs/functions: `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `_find_next_and_bit()`, and `_find_next_zero_bit()`. Macros `FIND_FIRST_BIT` and `FIND_NEXT_BIT` share word-scanning logic.

Control flow: Search scans bitmap words until it finds a non-zero candidate word after optional preprocessing. Next-bit search masks off bits before `start`, increments word index, and returns `size` when not found.

State/persistence: Stateless and read-only over caller-provided bitmaps.

Dependencies/integration: Uses Linux bitops, bitmap masks, `BITS_PER_LONG`, `__ffs`, `min`, and `unlikely`. Functions are conditionally compiled only when macro versions are absent.

Risks: Callers must supply enough memory for the requested bit count. Behavior is word-size dependent. `_and` variants require both bitmaps to be equally valid for the range.

Test signals: Cover zero-sized and boundary-sized bitmaps, starts at/after size, first/last bits, zero-bit searches, cross-word searches, and 32/64-bit word builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/find_bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/hweight.c -->
## sources/distributed-fs/ceph-client/tools/lib/hweight.c

Purpose: Provides software Hamming-weight/popcount implementations for 8-, 16-, 32-, and 64-bit values.

Important APIs/functions: `__sw_hweight8()`, `__sw_hweight16()`, `__sw_hweight32()`, and `__sw_hweight64()`.

Control flow: Each function applies standard SWAR bit-count reductions. Fast-multiplier builds use multiply-by-byte-sum constants for 32/64-bit cases; otherwise they use staged additions. 64-bit behavior splits into two 32-bit halves on 32-bit `BITS_PER_LONG`.

State/persistence: Stateless.

Dependencies/integration: Uses Linux bitops, asm types, `BITS_PER_LONG`, and optional `CONFIG_ARCH_HAS_FAST_MULTIPLIER`.

Risks: Correctness depends on unsigned arithmetic widths and constants matching word size. Build configuration determines implementation path. The 64-bit function has no explicit fallback outside 32/64-bit `BITS_PER_LONG`.

Test signals: Compare against compiler builtin popcount for all 8-bit values, representative 16/32/64-bit patterns, all-zero/all-one values, alternating bits, and both fast/non-fast configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/hweight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/list_sort.c -->
## sources/distributed-fs/ceph-client/tools/lib/list_sort.c

Purpose: Implements stable in-place sorting for Linux `struct list_head` doubly-linked lists using bottom-up mergesort.

Important APIs/functions: Public `list_sort(void *priv, struct list_head *head, list_cmp_func_t cmp)`. Internal `merge()` merges null-terminated singly-linked runs, and `merge_final()` performs final merge while restoring `prev` links and circular list structure.

Control flow: The input circular doubly-linked list is converted to a null-terminated singly-linked list. The algorithm maintains pending sorted sublists controlled by the bit pattern of an element count, eagerly merging balanced runs. At end it merges remaining runs from smallest to largest and restores the canonical doubly-linked ring.

State/persistence: Mutates the caller-owned list links only; no allocation.

Dependencies/integration: Uses Linux list APIs, compiler annotations, export symbol macro, and a caller-supplied comparator that returns positive when `a` sorts after `b`.

Risks: Comparator contract is subtle: returning `<=0` preserves input order and enables stability. Corrupt input list links can loop or crash. The algorithm temporarily invalidates `prev` links until final merge.

Test signals: Cover empty/single lists, already sorted/reverse lists, duplicate keys preserving order, boolean and tri-state comparators, large lists, and list integrity after sort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/list_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/Makefile -->
## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/Makefile

Purpose: Builds and installs libperf documentation, man pages, HTML pages, and example sources.

Important targets/variables: `MAN3_TXT`, `MAN7_TXT`, generated XML/HTML/man variables, `ASCIIDOC`, `XMLTO`, `install-man`, `install-html`, `install-examples`, `clean`, and pattern rules from `.txt` to `.xml`, `.3`, `.7`, and `.html`.

Control flow: `all` depends on man and HTML outputs. XML is generated with asciidoc using `asciidoc.conf`; man pages are generated with `xmlto` and selected XSL customizations. Install targets create destination directories under `DESTDIR`/`prefix` and copy artifacts.

State/persistence: Generated docs live under `$(OUTPUT)`. Install copies into man/doc/example directories.

Dependencies/integration: Includes tools make helpers and supports legacy asciidoc/docbook XSL conditionals such as `ASCIIDOC8`, `DOCBOOK_XSL_172`, and `ASCIIDOC_NO_ROFF`.

Risks: Toolchain-version compatibility is fragile. `EVENT_PARSE_VERSION` is referenced for document attributes and may need to be defined by the parent build. Output path handling depends on `OUTPUT` and DESTDIR quoting.

Test signals: Run `make -C tools/lib/perf/Documentation` with and without `OUTPUT`, install into a temporary `DESTDIR`, and test asciidoc/xmlto version conditionals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/asciidoc.conf -->
## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/asciidoc.conf

Purpose: Customizes asciidoc conversion for libperf documentation.

Important sections: Defines `linktep` inline macro, special character attributes, docbook link rendering, listing/verse block workarounds for roff/docbook XSL behavior, manpage header template, and XHTML link rendering.

Control flow: Asciidoc conditionals select docbook vs XHTML output and compatibility behavior based on attributes like `tep-asciidoc-no-roff` and `doctype-manpage`.

State/persistence: No runtime state; affects generated documentation output.

Dependencies/integration: Consumed by `Documentation/Makefile` through `ASCIIDOC_EXTRA`. Integrates with docbook manpage generation and libperf manual metadata.

Risks: The macro name/comments mention TEP in a libperf file, suggesting copied configuration and possible stale naming. The header enumerates many `mannameN` fields and depends on asciidoc filling them correctly. Incorrect conditionals can produce malformed man XML.

Test signals: Generate docbook and XHTML outputs, validate manpage headers, link macro rendering, listing blocks, and no-roff variants across supported asciidoc/docbook versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/asciidoc.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/counting.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/counting.c

Purpose: Demonstrates libperf counting mode using two software events.

Important APIs/functions: Initializes libperf logging, creates a dummy thread map, creates an evlist, allocates two evsels for CPU clock and task clock, sets maps, opens/enables/disables events, reads counts, and cleans up.

Control flow: Main sets two disabled perf event attributes with time-enabled/time-running read format. It creates a thread map for pid 0, adds evsels to the evlist, opens all FDs, enables, spins in a loop, disables, reads each evsel at CPU/thread index 0/0, prints values, closes and deletes resources.

State/persistence: Runtime-only perf FDs and reference-counted maps/evlist objects. No persistent output beyond stdout.

Dependencies/integration: Uses public libperf headers, Linux perf event types, and the `libperf_init()` print callback.

Risks: Busy-loop workload can be optimized away or behave differently under compiler settings. Error paths jump to cleanup but do not close partially opened evlist unless open succeeds. Requires perf_event permissions.

Test signals: Build example against installed libperf, run under permissive perf settings, verify two count lines with enabled/running fields, and run under restricted permissions to check failure messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/counting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/sampling.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/sampling.c

Purpose: Demonstrates libperf sampling mode over online CPUs using an mmaped perf ring buffer.

Important APIs/functions: Uses `perf_cpu_map__new_online_cpus()`, evlist/evsel setup, `perf_evlist__mmap()`, enable/sleep/disable, `perf_evlist__for_each_mmap()`, `perf_mmap__read_init()`, `perf_mmap__read_event()`, `perf_mmap__consume()`, and `perf_mmap__read_done()`.

Control flow: Main creates a hardware CPU cycles sampling event at frequency 10 with IP/TID/CPU/PERIOD sample fields. After opening and mmaping, it samples for three seconds, then iterates mmap buffers, decodes raw sample arrays in the declared sample order, prints fields, and consumes events.

State/persistence: Runtime perf FDs, CPU map, evlist, mmap ring buffers. No persistent storage.

Dependencies/integration: Depends on public libperf mmap/event APIs and kernel perf sampling permissions/hardware PMU support.

Risks: Raw sample decoding assumes the exact sample_type order and native layout. Hardware cycles may be unavailable in containers or restricted by `perf_event_paranoid`. Cleanup path on evsel creation failure jumps to `out_cpus` via `out_cpus`/`out_evlist` and should be checked for evlist leaks in edits.

Test signals: Build and run with adequate permissions, verify samples decode without overruns, test no-PMU/restricted-permission failures, and validate mmap cleanup with sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/sampling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Makefile -->
## sources/distributed-fs/ceph-client/tools/lib/perf/Makefile

Purpose: Builds, tests, installs, and packages libperf static/shared libraries, headers, pkg-config file, docs, and tests.

Important targets/variables: Version triplet `0.0.1`, `LIBPERF_A`, `LIBPERF_SO`, `LIBPERF_PC`, `LIBAPI`, `libs`, `tests`, `install_*`, and generated object targets via tools build system.

Control flow: Determines `srctree`, includes make helpers, sets includes/CFLAGS, builds `libapi`, compiles `libperf-in.o`, archives static library, links shared library with version script and symlinks, builds tests static/shared, substitutes pkg-config template, and installs libraries/headers/docs.

State/persistence: Outputs are under `$(OUTPUT)` or current dir. Install writes under `DESTDIR`/`prefix`.

Dependencies/integration: Integrates with Linux tools build infrastructure, `tools/lib/api`, arch include discovery, version script, and documentation makefile.

Risks: `prefix ?=` defaults empty, so install paths require caller care. Clean removes broad local patterns. Shared link depends on `libapi` and version script. Header install includes internal headers, exposing unstable internals.

Test signals: Run `make libs`, `make tests`, shared-library load with `LD_LIBRARY_PATH`, `make install DESTDIR=... prefix=/usr`, and verify symlinks/pkg-config contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/core.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/core.c

Purpose: Provides libperf global initialization and logging hook.

Important APIs/functions: `libperf_init()` initializes global `page_size` and installs a caller-supplied print callback. `libperf_print()` formats variadic messages and dispatches to the current callback. `__base_pr()` is the default stderr printer.

Control flow: Before initialization, logging uses `__base_pr`. `libperf_init()` sets `page_size = sysconf(_SC_PAGE_SIZE)` and replaces the callback, which may be NULL to suppress output.

State/persistence: Mutates global `page_size` and static `__libperf_pr`. These are process-wide.

Dependencies/integration: Uses public `<perf/core.h>`, internal `page_size` declaration, and libc `sysconf`/`vfprintf`.

Risks: No locking around global callback/page size; concurrent initialization/logging is not synchronized. `sysconf` failure is not checked. Passing NULL intentionally disables logging.

Test signals: Verify default logging, custom callback invocation, NULL callback suppression, initialized page size, and thread-safety assumptions in multithreaded users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/cpumap.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/cpumap.c

Purpose: Implements reference-counted CPU maps for libperf.

Important APIs/functions: Allocation/lifecycle `perf_cpu_map__alloc/get/put/new/new_online_cpus/new_any_cpu/new_int`; parsing `perf_cpu_map__new()`; queries `nr`, `cpu`, `idx`, `has`, `equal`, `min`, `max`, any/empty helpers; set operations `perf_cpu_map__merge()` and `perf_cpu_map__intersect()`.

Control flow: Online CPU maps prefer sysfs `devices/system/cpu/online`, falling back to `sysconf`. String parsing accepts comma-separated integers and ranges, rejects duplicates and invalid ranges, sorts/trims, and uses `-1` for any CPU. Merge/intersect use sorted-array algorithms with reference-count optimizations for subsets.

State/persistence: CPU maps are heap objects with refcounts and optional sanitizer indirection from `rc_check.h`. No durable persistence.

Dependencies/integration: Uses Linux refcount, warnings/asserts, tools sysfs API, internal cpumap definitions, and public libperf cpumap API.

Risks: Parser rejects duplicates as invalid rather than deduplicating in-place. `MAX_NR_CPUS` only warns. This checkout contains a duplicated `struct perf_cpu result = {` line in `perf_cpu_map__cpu()`, which is a compile blocker unless corrected elsewhere. Ownership rules around `merge()` replacing `*orig` require caller care.

Test signals: Unit tests for parsing ranges, duplicates, empty string, online fallback, get/put balance under sanitizers, subset/merge/intersect correctness, any CPU behavior, and a plain build compile check for the duplicated declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/evlist.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/evlist.c

Purpose: Implements libperf event-list management: evsel ownership, map propagation, open/close/enable/disable orchestration, ID hashing, polling, and mmap setup.

Important APIs/functions: `perf_evlist__new/init/delete/add/remove/set_maps/open/close/enable/disable`, ID helpers `perf_evlist__id_add[_fd]`, polling helpers, mmap entry points `perf_evlist__mmap[_ops]`, `perf_evlist__munmap()`, mmap iteration, leader/group helpers, and `perf_evlist__go_system_wide()`.

Control flow: Evlist owns a list of evsels. Map propagation derives each evsel CPU/thread map from user CPUs, PMU CPUs, system-wide flags, requires-CPU constraints, and CPU-index-0-only events, pruning empty events. Open iterates evsels and rolls back on failure. Mmap computes required mmap count, allocates pollfd capacity, then maps per-thread when any CPU is present or per-CPU otherwise, sharing outputs with `PERF_EVENT_IOC_SET_OUTPUT`.

State/persistence: Maintains evsel list, CPU/thread maps, all-CPU union, fdarray poll state, ID hash table, mmap arrays, and first mmap links. State is process memory plus perf FDs/mmaps.

Dependencies/integration: Uses internal evsel/cpumap/threadmap/mmap/xyarray/fdarray APIs, perf ioctls, poll, and public libperf iteration macros.

Risks: Map propagation ownership is subtle and can remove evsels. Mmap setup must keep refcounts balanced across shared outputs and pollfd filtering. ID fallback reads are incompatible with group format. `has_user_cpus` is meaningful but not set in this file’s `set_maps()`, so callers/other code must manage it.

Test signals: Existing libperf evlist tests should cover map propagation, open rollback, group leaders, ID hash lookup, poll filtering, mmap per-thread/per-CPU cases, overwrite buffers, system-wide events, and refcount sanitizer runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/evsel.c -->
## sources/distributed-fs/ceph-client/tools/lib/perf/evsel.c

Purpose: Implements libperf event selector lifecycle, perf_event_open calls, per-CPU/thread FD arrays, mmap helpers, reads, ioctls, sample IDs, period storage, and count scaling.

Important APIs/functions: `perf_evsel__new/init/delete/open/close/mmap/munmap/read/enable/disable/apply_filter`, FD/id alloc/free helpers, `perf_evsel__cpus/threads/attr`, `perf_sample_id__get_period_storage()`, and `perf_counts_values__scale()`.

Control flow: Open fills an `xyarray` of FDs for each CPU/thread combination, resolving group leader FDs first. Read computes expected read size from `read_format`, handles group vs non-group formats, optionally uses mmap self-read fast path, and normalizes values into `perf_counts_values`. Enable/disable/filter iterate ioctls across FD dimensions. Sample ID storage allocates arrays and optional per-thread hash buckets.

State/persistence: Evsel owns attr, maps, FD xyarray, mmap xyarray, sample ID arrays, IDs, leader relation, per-stream period list, and flags. Kernel perf FDs and mmap regions persist until close/munmap.

Dependencies/integration: Uses `perf_event_open` syscall, libperf maps, thread maps, mmap internals, xyarray, readn, ioctls, and Linux perf formats.

Risks: Static fallback maps are never freed by design. Group FD lookup requires leader opened first. Read format handling must stay aligned with kernel ABI. `perf_evsel__exit()` asserts resources were already closed/freed. Permission errors from perf_event_open propagate as negative errno.

Test signals: Tests should cover per-thread/per-CPU opens, group leader/member ordering, read formats including LOST and GROUP, mmap read-self path, ioctl failures, filter application, sample ID allocation/freeing, per-thread period storage, and scaling when running time is zero or less than enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/evsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/cpumap.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/cpumap.h

Purpose: Defines the internal layout and helpers for libperf CPU maps.

Important APIs/types: `DECLARE_RC_STRUCT(perf_cpu_map)` expands to a refcounted struct with `refcnt`, `nr`, and flexible `struct perf_cpu map[]`. Internal declarations expose allocation, index lookup, subset test, set-nr, and `perf_cpu_map__refcnt()`.

Control flow: Header has only inline refcount access. Runtime flow is in `cpumap.c`.

State/persistence: CPU map state is heap-owned and refcounted. Optional `rc_check.h` indirection can alter pointer layout in sanitizer builds.

Dependencies/integration: Includes public `<perf/cpumap.h>`, Linux refcount, and `rc_check.h`. Used by evlist/evsel and cpumap implementation.

Risks: Internal layout exposure means installed internal headers can create ABI coupling. Consumers must use `RC_CHK_ACCESS()`/helpers correctly under reference-count checking.

Test signals: Build with and without address/leak sanitizer refcount checking, verify flexible-array allocation sizes and refcount helper access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/cpumap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evlist.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evlist.h

Purpose: Defines the internal libperf event-list structure, mmap callback interface, iteration macros, and internal helper declarations.

Important APIs/types: `struct perf_evlist` contains evsel entries, CPU/thread maps, mmap state, fdarray poll state, and sample-ID hash heads. `struct perf_evlist_mmap_ops` abstracts mmap allocation and mapping callbacks. Macros iterate entries forward, reverse, and safely.

Control flow: Inline `perf_evlist__first/last()` and iteration macros drive many evlist operations. Mmap ops callbacks let tests or alternate implementations hook mapping behavior.

State/persistence: Defines in-memory ownership fields for evlist runtime; no storage by itself.

Dependencies/integration: Includes Linux list, fdarray, internal cpumap/evsel. Used by evlist implementation and internal tests.

Risks: `perf_evlist__first/last()` assume non-empty lists. Hash size constants tune sample-ID lookup. Internal fields are exposed to installed internal-header consumers.

Test signals: Compile internal users, exercise iteration macros on empty/non-empty lists, and validate mmap callback hooks in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evsel.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evsel.h

Purpose: Defines the internal libperf event-selector structure and related sample-ID/period storage.

Important APIs/types: `struct perf_sample_id_period`, `struct perf_sample_id`, and `struct perf_evsel`. Declarations cover lifecycle, FD/id allocation, read sizing, filters, per-thread period lookup, and attr flags.

Control flow: The safe period iterator macro supports freeing per-stream period nodes. `perf_sample_id` maps perf sample IDs back to evsels and carries stream metadata for mmap/AUX/sample processing.

State/persistence: Evsel state includes linked-list membership, perf attr, maps, FD/mmap/sample xyarrays, IDs, group leader, period list, member count, and PMU behavior flags.

Dependencies/integration: Uses Linux perf ABI, list/hlist, public/internal CPU map types, thread maps, and xyarray.

Risks: Struct comments expose subtle semantics around per-thread/global `PERF_SAMPLE_READ`. Any layout or flag change affects evlist/evsel/mmap integration. `nr_members` and `leader` must be maintained consistently for group reads.

Test signals: Group event tests, sample ID lookup tests, per-thread period storage tests, and build checks for public/internal header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/lib.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/lib.h

Purpose: Declares small libperf internal process-wide helpers.

Important APIs/types: Global `page_size`; robust I/O helpers `readn()`, `writen()`, and `preadn()`.

Control flow: No implementation here. Callers rely on `libperf_init()` to initialize `page_size`, and I/O helpers to transfer exact byte counts.

State/persistence: `page_size` is global process state. I/O helpers operate on caller FDs.

Dependencies/integration: Included by core, evsel, evlist, mmap, and other internals. Requires `<sys/types.h>`.

Risks: Header guard closing comment incorrectly names `CPUMAP`, a documentation issue. Users must not read `page_size` before initialization unless implementation provides a default elsewhere.

Test signals: Build all internal users, verify exact-read/write helpers on short reads/writes/EINTR, and check page-size initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/mmap.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/mmap.h

Purpose: Defines internal perf mmap ring-buffer state and operations.

Important APIs/types: `PERF_SAMPLE_MAX_SIZE`, `libperf_unmap_cb_t`, `struct perf_mmap`, `struct perf_mmap_param`, and declarations for init/mmap/munmap/get/put/read-head/read-self helpers.

Control flow: Runtime users initialize a `perf_mmap`, map a perf FD with parameters, read head/self counts, consume elsewhere, and release via refcounted get/put or munmap.

State/persistence: `struct perf_mmap` tracks base pointer, mask, fd, CPU, refcount, read positions, overwrite mode, flush state, event-copy buffer, and linked `next` pointer.

Dependencies/integration: Used by evlist/evsel mmap paths and public mmap APIs. Depends on refcount, Linux types, CPU map type, and perf count values.

Risks: Ring-buffer correctness depends on mask/page-size setup and refcount lifecycle. `event_copy` handles wrapped samples and must respect `PERF_SAMPLE_MAX_SIZE`.

Test signals: Mmap read/consume tests for forward and overwrite buffers, refcount get/put balance, wrapped events, self-read counts, and unmap callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/rc_check.h -->
## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/rc_check.h

Purpose: Provides optional sanitizer-assisted reference-count checking macros for libperf objects.

Important APIs/macros: `DECLARE_RC_STRUCT`, `RC_STRUCT`, `ADD_RC_CHK`, `RC_CHK_ACCESS`, `RC_CHK_FREE`, `RC_CHK_GET`, `RC_CHK_PUT`, and `RC_CHK_EQUAL`. `REFCNT_CHECKING` is enabled under address/leak sanitizer defines.

Control flow: Normal builds make macros mostly transparent. Checking builds wrap reference-counted objects in an extra allocated indirection on get/add, clear/free wrappers on put, and free the original object on final free, allowing leaks/double-frees/use-after-free to surface via sanitizers.

State/persistence: Adds heap wrapper allocations in sanitizer builds. No persistent state.

Dependencies/integration: Used by cpumap and potentially other refcounted internal structs. Includes `zalloc` for `zfree`.

Risks: Macro-generated type changes can surprise code that assumes pointer identity or direct layout. All access must go through `RC_CHK_ACCESS` in checking builds. `ADD_RC_CHK` allocation failure can turn a valid object into NULL result.

Test signals: Build and run libperf tests with ASAN/LSAN, intentionally exercise balanced get/put, missed put, double put, pointer equality, and final free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/rc_check.h -->
