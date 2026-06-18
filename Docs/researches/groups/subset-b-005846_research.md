# Research Report: subset-b-005846

This grouped report covers the source files assigned to `subset-b-005846`. Each file section is bounded by reconciliation markers so the guard can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/brcmphy.h -->
## sources/distributed-fs/ceph-client/include/linux/brcmphy.h

**Purpose:** This header is the Broadcom Ethernet PHY register and identifier catalog used by PHY drivers. It contains no executable control flow; it defines constants that let MDIO/PHY code identify Broadcom devices, access vendor-specific register windows, configure LEDs, Wake-on-LAN, BroadR-Reach/LRE, EEE, SerDes, RGMII/SGMII modes, power states, and cable diagnostics.

**Important APIs/types/functions:** There are no structs or functions. Important exports are `BRCM_PSEUDO_PHY_ADDR`, many `PHY_ID_BCM*` values, OUI masks, `PHY_BRCM_*` driver flags, `MII_BCM54XX_*` register addresses, interrupt masks, shadow-register selection helpers, LED encodings, expansion-register selectors, WOL register fields, LRE control/status/advertisement masks, and ECD fault/length result definitions.

**Control flow, state, persistence:** Runtime state lives in PHY driver-private data and hardware registers, not this header. The constants encode hardware-visible persistent state such as WOL configuration, PHY power modes, advertised link modes, and diagnostic results; callers must write/read them through MDIO helper paths.

**Dependencies/integration:** Includes `linux/phy.h` and depends on kernel bit macros such as `BIT()` and `GENMASK()`. It integrates with Broadcom PHY drivers under the PHY library and switch drivers that use pseudo-PHY address 30.

**Risks and test signals:** Risks are wrong bit masks, wrong shadow-bank selection, or mixing RDB/expansion addressing paths, all of which can silently misconfigure link, WOL, LEDs, or diagnostics. Test signals are PHY probe ID matching, ethtool link-mode reporting, interrupt delivery, WOL suspend/resume, EEE behavior, cable-test output, and register traces from known Broadcom PHY variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/brcmphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsearch.h -->
## sources/distributed-fs/ceph-client/include/linux/bsearch.h

**Purpose:** This header provides the kernel binary-search interface for sorted arrays. It offers an inline implementation for compile-time optimization and declares the out-of-line `bsearch()` helper.

**Important APIs/types/functions:** `__inline_bsearch(const void *key, const void *base, size_t num, size_t size, cmp_func_t cmp)` walks a sorted array by repeatedly comparing the key to the middle element. `bsearch()` has the same signature and is the exported generic helper. The comparator type `cmp_func_t` comes from `linux/types.h`.

**Control flow, state, persistence:** The algorithm is stateless and read-only. It computes `pivot = base + (num >> 1) * size`, returns the pivot on comparator equality, advances `base` past the pivot on positive comparison, and halves the remaining element count until exhausted.

**Dependencies/integration:** Used by code that keeps sorted kernel arrays, including BTF ID-set lookups in `btf.h`. The caller owns ordering, comparator correctness, element lifetime, and synchronization around concurrent mutation.

**Risks and test signals:** Risks include unsorted input, comparators that overflow or violate strict ordering, zero/incorrect element sizes, and racing writers. Test signals are boundary cases for empty, one-element, first/middle/last, missing-low, missing-high, and duplicate-key arrays, plus sanitizer coverage for pointer arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsearch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsg-lib.h -->
## sources/distributed-fs/ceph-client/include/linux/bsg-lib.h

**Purpose:** This header defines the block SCSI generic (BSG) helper-library interface used by transport drivers that expose request/reply command queues through the block layer.

**Important APIs/types/functions:** `struct bsg_buffer` describes DMA payload scatterlists. `struct bsg_job` carries device pointer, `kref`, timeout, transport-specific request/reply buffers and lengths, request/reply payloads, result, received payload length, bidi request/bio, and driver-private `dd_data`. Callback types are `bsg_job_fn` and `bsg_timeout_fn`. Functions include `bsg_job_done()`, `bsg_setup_queue()`, `bsg_remove_queue()`, `bsg_job_get()`, and `bsg_job_put()`.

**Control flow, state, persistence:** Drivers create a queue with `bsg_setup_queue()`, receive jobs through the supplied job callback, fill reply/result fields, and complete with `bsg_job_done()`. Job lifetime is reference-counted; queue lifetime is explicit. No persistent storage is defined here.

**Dependencies/integration:** Includes `linux/blkdev.h`, integrates with request queues, queue limits, scatterlists, block error handling timeouts, and transport-specific command protocols.

**Risks and test signals:** Risks are reference leaks, double completion, incorrect reply lengths, scatterlist direction mistakes, timeout races, and bidi request ownership errors. Test signals include SG_IO passthrough tests, timeout/error injection, queue teardown under in-flight jobs, refcount debugging, and DMA mapping checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsg-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsg.h -->
## sources/distributed-fs/ceph-client/include/linux/bsg.h

**Purpose:** This header exposes the higher-level BSG character-device queue registration API for request queues that accept SG_IO v4 and io_uring command paths.

**Important APIs/types/functions:** `bsg_sg_io_fn` handles `struct sg_io_v4` requests with write-open and timeout context. `bsg_uring_cmd_fn` handles `struct io_uring_cmd` with issue flags and write-open state. `bsg_register_queue()` binds a request queue to a parent device/name and callbacks, returning an opaque `struct bsg_device *`. `bsg_unregister_queue()` tears it down.

**Control flow, state, persistence:** The header defines an entry/exit contract only. Runtime state is owned by the BSG core and block queue. Registered callbacks are invoked when userspace submits passthrough commands; unregister must coordinate with in-flight users.

**Dependencies/integration:** Includes UAPI `linux/bsg.h` for `sg_io_v4`. It integrates with block request queues, device model parentage, and io_uring passthrough.

**Risks and test signals:** Risks are callback ABI mismatches, queue lifetime races during unregister, permission mistakes around `open_for_write`, and timeout semantics that differ between SG_IO and io_uring. Test signals include bsg device-node creation/removal, SG_IO passthrough, io_uring passthrough, permission tests, and teardown with open file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btf.h -->
## sources/distributed-fs/ceph-client/include/linux/btf.h

**Purpose:** This header is the kernel-internal BPF Type Format interface. It declares BTF object lifecycle, lookup, display, type inspection, kfunc registration/filtering, field parsing, BPF struct-ops integration, and config-gated stubs when BPF syscall support is absent.

**Important APIs/types/functions:** Key macros include `BTF_TYPE_EMIT`, `BTF_TYPE_EMIT_ENUM`, kfunc flags `KF_*`, `__bpf_kfunc`, kfunc diagnostic wrappers, and `stringify_struct()`. Types include `struct btf`, `btf_kfunc_id_set`, `btf_id_dtor_kfunc`, `btf_struct_meta`, `btf_field_desc`, and `btf_field_iter`. Functions cover `btf_get/put`, `btf_new_fd`, `btf_get_by_fd`, `btf_get_info_by_fd`, type resolution (`btf_type_id_size`, `btf_type_skip_modifiers`, `btf_resolve_size`), object formatting, ID lookup, kfunc allow checks, BTF relocation, and field iteration.

**Control flow, state, persistence:** Inline helpers decode `struct btf_type` metadata from UAPI layouts and traverse variable-length member/array/enum payloads. ID-set helpers use binary search over sorted arrays. Actual BTF object state, refcounts, module ownership, and verifier decisions live in BPF/BTF implementation files. Feature-disabled builds return safe stubs such as `NULL`, `-EOPNOTSUPP`, `-ENOENT`, or no-op success for registration.

**Dependencies/integration:** Depends on `linux/bsearch.h`, `linux/btf_ids.h`, BPF UAPI headers, module/file operations, seq files, verifier logs, and optional `CONFIG_BPF_SYSCALL`/`CONFIG_BPF_JIT`.

**Risks and test signals:** Risks are stale BTF kind assumptions, unsorted ID sets, unsafe raw object display, incorrect kfunc flags that weaken verifier guarantees, and build differences across config gates. Test signals include BPF verifier selftests, kfunc registration tests, BTF pretty-print output, module BTF load/unload, CO-RE relocation, and no-BPF config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btf_ids.h -->
## sources/distributed-fs/ceph-client/include/linux/btf_ids.h

**Purpose:** This header defines compile/link-time machinery for collecting symbolic BTF IDs into the `.BTF_ids` ELF section and later resolving them with `resolve_btfids`.

**Important APIs/types/functions:** `struct btf_id_set` stores a count and sorted `u32` IDs. `struct btf_id_set8` stores count, flags, and `{ id, flags }` pairs. Macros include `BTF_ID`, `BTF_ID_FLAGS`, `BTF_ID_LIST`, `BTF_ID_LIST_GLOBAL`, `BTF_ID_UNUSED`, `BTF_SET_START/END`, `BTF_SET8_START/END`, and `BTF_KFUNCS_START/END`. `BTF_SET8_KFUNCS` marks kfunc sets.

**Control flow, state, persistence:** With `CONFIG_DEBUG_INFO_BTF`, macros emit assembler objects into `.BTF_ids`; the IDs are initially zero and resolved at link/post-link time. Without BTF debug info, the macros become static dummy arrays/sets so code still compiles without runtime ID content.

**Dependencies/integration:** Depends on compiler attributes, stringification, inline asm, and the external `resolve_btfids` tool. It is consumed by BPF/kfunc code and queried through helpers in `btf.h`.

**Risks and test signals:** Risks are layout changes not mirrored in `resolve_btfids`, using unsorted sets where binary search is expected, missing debug BTF config, and duplicate or unused entries. Test signals are successful `resolve_btfids` runs, BPF selftests that locate expected IDs, module builds with and without `CONFIG_DEBUG_INFO_BTF`, and objdump checks for `.BTF_ids`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btf_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree-128.h -->
## sources/distributed-fs/ceph-client/include/linux/btree-128.h

**Purpose:** This header provides typed wrappers for the generic kernel B+Tree using 128-bit keys represented as two `u64` words.

**Important APIs/types/functions:** It declares `extern struct btree_geo btree_geo128` and `struct btree_head128`. Inline wrappers include `btree_init_mempool128`, `btree_init128`, `btree_destroy128`, `btree_lookup128`, `btree_get_prev128`, `btree_insert128`, `btree_update128`, `btree_remove128`, `btree_last128`, `btree_merge128`, `btree_visitor128`, `btree_grim_visitor128`, and `btree_for_each_safe128`. `visitor128_t` gives callbacks two `u64` key parts.

**Control flow, state, persistence:** The wrappers convert `(k1, k2)` into a two-element `u64 key[2]` and pass it to generic B+Tree functions with `btree_geo128`. Tree state is stored in the embedded `struct btree_head h`; memory allocation and node lifetime are handled by the generic implementation/mempool.

**Dependencies/integration:** Must be included after `btree.h` has declared the generic types/functions. It integrates with users that need compound keys and typed visitors without manually building `unsigned long *` keys.

**Risks and test signals:** Risks are key-word ordering mismatches, stack key lifetime assumptions outside synchronous calls, partial merge failures, and 32-bit architecture casting assumptions. Test signals include insert/lookup/remove/update of two-word keys, reverse iteration through `btree_for_each_safe128`, visitor traversal, and merge failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree-128.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree-type.h -->
## sources/distributed-fs/ceph-client/include/linux/btree-type.h

**Purpose:** This template header generates typed B+Tree wrappers for one-word key types. It is included multiple times by `btree.h` after defining `BTREE_TYPE_SUFFIX`, `BTREE_TYPE_BITS`, `BTREE_TYPE_GEO`, and `BTREE_KEYTYPE`.

**Important APIs/types/functions:** The template creates `struct btree_head<SUFFIX>` and wrappers for `init_mempool`, `init`, `destroy`, `merge`, `lookup`, `insert`, `update`, `remove`, `last`, `get_prev`, `visitor`, and `grim_visitor`. It also declares a typed visitor trampoline `visitor<SUFFIX>` and typedef `visitor<SUFFIX>_t`.

**Control flow, state, persistence:** Wrappers forward into generic `btree_*` operations while adapting key storage. If `BITS_PER_LONG > BTREE_TYPE_BITS`, the key is widened into a local `unsigned long`; otherwise it is passed by pointer cast. Tree state is the embedded generic head and mempool-managed nodes.

**Dependencies/integration:** Depends on macro definitions from `btree.h`, generic B+Tree functions, and the appropriate geometry object. It emits variants such as `btree_l`, `btree_32`, and `btree_64`.

**Risks and test signals:** Risks are macro leakage, including the template directly without definitions, visitor trampoline name assumptions, key truncation, and aliasing/alignment issues on cross-width builds. Test signals are compile coverage for all generated variants, lookup/update/remove behavior on 32- and 64-bit architectures, and visitor callback key correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree.h -->
## sources/distributed-fs/ceph-client/include/linux/btree.h

**Purpose:** This is the public generic B+Tree interface for mapping unsigned integer keys of several widths to non-NULL pointers.

**Important APIs/types/functions:** `struct btree_head` stores the root node, mempool, and tree height. Generic functions include `btree_alloc`, `btree_free`, `btree_init_mempool`, `btree_init`, `btree_destroy`, `btree_lookup`, `btree_insert`, `btree_update`, `btree_remove`, `btree_merge`, `btree_last`, `btree_get_prev`, `btree_visitor`, and `btree_grim_visitor`. The header then includes `btree-128.h` and `btree-type.h` to produce typed `l`, `32`, and `64` wrappers plus safe reverse-iteration macros.

**Control flow, state, persistence:** The generic implementation stores sorted key/value pairs in mempool-allocated nodes laid out as keys followed by values. Insert/update/remove/merge mutate the tree and may allocate/free nodes; lookup and reverse iteration read current tree state. Persistence is in memory only.

**Dependencies/integration:** Depends on `linux/kernel.h` and `linux/mempool.h`. Users must provide external synchronization if the tree is shared across threads.

**Risks and test signals:** Risks include inserting duplicate keys, inserting `NULL` values, ignoring partial `btree_merge()` failure semantics, using the wrong typed geometry, and unsafe iteration while mutating. Test signals include generic and typed CRUD tests, memory-pressure injection, reverse traversal ordering, visitor/grim visitor cleanup, and lockdep/KASAN runs around concurrent users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btrfs.h -->
## sources/distributed-fs/ceph-client/include/linux/btrfs.h

**Purpose:** This kernel header is a thin include wrapper that exposes Btrfs UAPI definitions to in-kernel users through `linux/btrfs.h`.

**Important APIs/types/functions:** It declares no new symbols. Its only functional content is `#include <uapi/linux/btrfs.h>`.

**Control flow, state, persistence:** There is no control flow or runtime state. Persistence semantics are entirely in the Btrfs filesystem and UAPI structures/constants included from the UAPI header.

**Dependencies/integration:** Integrates kernel code with Btrfs ioctl/format constants while preserving the conventional `linux/` include path.

**Risks and test signals:** Risks are mostly include-order or accidental divergence from UAPI. Test signals are successful builds of in-kernel Btrfs consumers and ABI tests that include the UAPI header through both paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/btrfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/buffer_head.h -->
## sources/distributed-fs/ceph-client/include/linux/buffer_head.h

**Purpose:** This header defines the legacy `buffer_head` abstraction used by filesystems and block helpers to track block mappings, state flags, and buffer-backed folio I/O.

**Important APIs/types/functions:** `enum bh_state_bits` defines state such as `BH_Uptodate`, `BH_Dirty`, `BH_Lock`, `BH_Mapped`, `BH_Delay`, `BH_Unwritten`, and `BH_Meta`. `struct buffer_head` stores state bits, circular folio/page linkage, block number, size, data pointer, block device, completion callback/private data, metadata association, refcount, and uptodate lock. Macro families generate `set_buffer_*`, `clear_buffer_*`, and `buffer_*` helpers. APIs cover allocation, lookup/read (`__find_get_block`, `bdev_getblk`, `__bread_gfp`, `sb_bread`), dirty/writeback, locking/waiting, submit, block write/read helpers, migration, metadata-buffer lists, and optional buffer-head LRU management.

**Control flow, state, persistence:** Buffer state is bit-based and refcounted. Reads lock buffers and submit block I/O when not uptodate; write helpers mark dirty and submit; `brelse()`/`bforget()` drop references or discard dirty state. Data persistence occurs only through block I/O initiated by implementation functions.

**Dependencies/integration:** Depends on block, fs, pagemap, waitqueue, atomic, migration, and folio APIs. It integrates with legacy filesystems, superblocks, block devices, and address-space operations.

**Risks and test signals:** Risks include stale uptodate barriers, leaked refs, buffer/folio aliasing bugs, dirty-state loss, migration races, and incorrect use in highmem or no-`CONFIG_BUFFER_HEAD` builds. Test signals include filesystem write/read/truncate tests, fsync metadata tests, writeback error injection, buffer migration tests, lockdep, KASAN, and `CONFIG_BUFFER_HEAD=n` compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/buffer_head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bug.h -->
## sources/distributed-fs/ceph-client/include/linux/bug.h

**Purpose:** This header centralizes kernel BUG/WARN reporting contracts and data-corruption checking helpers.

**Important APIs/types/functions:** `enum bug_trap_type` classifies trap handling as none, warning, or BUG. `MAYBE_BUILD_BUG_ON()` chooses compile-time or runtime checking depending on constant-ness. With `CONFIG_GENERIC_BUG`, declarations include `bug_get_file_line()`, `find_bug()`, `report_bug()`, `report_bug_entry()`, `is_valid_bugaddr()`, and `generic_bug_clear_once()`, plus `is_warning_bug()`. Without it, safe stubs are provided. `mem_dump_obj()` is printk-gated. `CHECK_DATA_CORRUPTION()` warns or BUGs depending on `CONFIG_BUG_ON_DATA_CORRUPTION`.

**Control flow, state, persistence:** Runtime state is architecture/generic BUG tables and once-warning metadata managed elsewhere. This header selects reporting behavior and exposes helpers that callers must act on, especially `CHECK_DATA_CORRUPTION()` returning a boolean.

**Dependencies/integration:** Includes `asm/bug.h`, compiler helpers, and `build_bug.h`. Integrates with trap handlers, printk, and corruption-hardening code.

**Risks and test signals:** Risks include using BUG where recoverable error handling is required, ignoring the return from corruption checks, and config-specific behavior changes. Test signals include WARN/BUG selftests, objtool/trap-table validation, printk/no-printk builds, and fault-injection paths that confirm corruption detection returns are handled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/build-salt.h -->
## sources/distributed-fs/ceph-client/include/linux/build-salt.h

**Purpose:** This header emits a Linux ELF note containing `CONFIG_BUILD_SALT`, allowing builds to carry a configured salt value in the image metadata.

**Important APIs/types/functions:** `LINUX_ELFNOTE_BUILD_SALT` is the note type. `BUILD_SALT` expands differently for assembler and C: assembler uses `ELFNOTE(Linux, ..., .asciz CONFIG_BUILD_SALT)`, while C uses `ELFNOTE32("Linux", ..., CONFIG_BUILD_SALT)`.

**Control flow, state, persistence:** There is no runtime control flow. The persistent output is a build-time ELF note embedded into the object/image.

**Dependencies/integration:** Depends on `linux/elfnote.h` and `CONFIG_BUILD_SALT`. It is consumed by build/link image metadata rather than runtime code.

**Risks and test signals:** Risks are missing or malformed `CONFIG_BUILD_SALT`, assembler/C macro divergence, and linker scripts dropping the note. Test signals are successful vmlinux/module builds and `readelf -n` verification of the Linux build-salt note.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/build-salt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/build_bug.h -->
## sources/distributed-fs/ceph-client/include/linux/build_bug.h

**Purpose:** This header provides compile-time assertion helpers used throughout the kernel to enforce layout and constant invariants.

**Important APIs/types/functions:** `BUILD_BUG_ON_ZERO()`, `BUILD_BUG_ON_NOT_POWER_OF_2()`, `BUILD_BUG_ON_INVALID()`, `BUILD_BUG_ON_MSG()`, `BUILD_BUG_ON()`, `BUILD_BUG()`, `static_assert()`, and `ASSERT_STRUCT_OFFSET()` are the main macros.

**Control flow, state, persistence:** These macros affect compilation only. Some forms produce expression value `0` to be usable inside initializers; others emit compile-time assertions or evaluate type checking without runtime code.

**Dependencies/integration:** Depends on compiler assertion infrastructure from `linux/compiler.h`. It is used by layout-sensitive subsystems, generated protocol headers, and template macros.

**Risks and test signals:** Risks include using non-constant expressions where C requires integer constant expressions, relying on side effects in `BUILD_BUG_ON_INVALID()`, or over-constraining ABI/layout across architectures. Test signals are compile-only tests, allmodconfig/tinyconfig coverage, and intentional negative tests in headers that require fixed struct offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/build_bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/buildid.h -->
## sources/distributed-fs/ceph-client/include/linux/buildid.h

**Purpose:** This header exposes helpers for parsing ELF build IDs from VMAs, files, memory buffers, and the kernel image.

**Important APIs/types/functions:** `BUILD_ID_SIZE_MAX` is 20. APIs include `build_id_parse()`, `build_id_parse_file()`, `build_id_parse_nofault()`, `build_id_parse_buf()`, optional `vmlinux_build_id`, `init_vmlinux_build_id()`, and the `struct freader` abstraction with `freader_init_from_file()`, `freader_init_from_mem()`, `freader_fetch()`, and `freader_cleanup()`.

**Control flow, state, persistence:** `freader` carries temporary read state for either a file-backed folio mapping or an in-memory buffer, including error state and fault policy. Parsed build IDs are copied into caller-provided buffers; the optional vmlinux build ID persists as global kernel state.

**Dependencies/integration:** Depends on VMA, file, folio, and ELF note parsing implementation. Used by stack traces, vmcore metadata, perf/BPF, and diagnostics that identify binaries.

**Risks and test signals:** Risks include faulting in no-fault paths, stale folio mappings, wrong buffer bounds, and assuming all build IDs are SHA1-sized despite the max constant. Test signals include parsing valid/malformed ELF notes, nofault VMA tests, file-backed and memory-backed readers, vmcore/stacktrace build-ID output, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/buildid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall.h -->
## sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall.h

**Purpose:** This header defines the controller-side STM32 firewall framework interface. It lets STM32 firewall providers register controllers and participate in boot-time device-tree population decisions.

**Important APIs/types/functions:** Firewall type bits are `STM32_PERIPHERAL_FIREWALL`, `STM32_MEMORY_FIREWALL`, and `STM32_NOTYPE_FIREWALL`. `struct stm32_firewall_controller` stores name, device, MMIO base, list entry, type, maximum entries, and callbacks `grant_access`, `release_access`, and `grant_memory_range_access`. Functions are `stm32_firewall_controller_register()`, `stm32_firewall_controller_unregister()`, and `stm32_firewall_populate_bus()`.

**Control flow, state, persistence:** Registered controllers become part of a framework-maintained list. Boot population calls into controllers to decide whether protected DT nodes are accessible. Access grants may change firewall hardware state and must be paired with release where applicable.

**Dependencies/integration:** Depends on device tree, platform devices, list infrastructure, and MMIO. Integrates with `stm32_firewall_device.h` consumers and STM32 access-controller bindings.

**Risks and test signals:** Risks include registering controllers before MMIO is ready, incorrect `max_entries`, missing release paths, and populating inaccessible devices that later fault. Test signals are DT boot with protected peripherals/memory, denied-access probes returning errors rather than crashing, controller unregister tests, and memory-range grant coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall_device.h -->
## sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall_device.h

**Purpose:** This header defines the consumer-side STM32 firewall interface for devices that need access grants from one or more firewall controllers.

**Important APIs/types/functions:** `STM32_FIREWALL_MAX_EXTRA_ARGS` limits per-entry arguments. `struct stm32_firewall` stores an opaque controller pointer, up to five extra arguments, entry name, argument count, and firewall ID. With `CONFIG_STM32_FIREWALL`, APIs include `stm32_firewall_get_firewall()`, `stm32_firewall_grant_access()`, `stm32_firewall_release_access()`, by-ID grant/release helpers, and `stm32_firewall_get_grant_all_access()`. Without the config, functions return `-ENODEV` or no-op.

**Control flow, state, persistence:** Consumers parse DT access-controller references, request grants before touching protected resources, then release. By-ID helpers allow subsystem resources but bypass DT ID validation and must be used carefully.

**Dependencies/integration:** Depends on device tree, platform device types, and controller registration from `stm32_firewall.h`. Integrates with STM32 peripheral/memory drivers.

**Risks and test signals:** Risks are leaked grants, using `U32_MAX`, trusting by-ID grants from unvalidated sources, and failing to handle `-ENODEV` on non-firewall builds. Test signals include config-on/off compile coverage, protected-device probe ordering, grant-all cleanup on partial failure, and negative DT entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bvec.h -->
## sources/distributed-fs/ceph-client/include/linux/bvec.h

**Purpose:** This header defines `bio_vec` memory segment descriptors and iterator helpers used by block I/O and page/folio-backed data movement.

**Important APIs/types/functions:** `struct bio_vec` stores page, length, and page offset. `bvec_set_page()`, `bvec_set_folio()`, and `bvec_set_virt()` initialize segments. `struct bvec_iter` tracks sector, remaining bytes, vector index, and per-vector offset. Access macros produce single-page and multipage views. Iterators include `bvec_iter_advance()`, `bvec_iter_advance_single()`, `for_each_bvec`, `for_each_mp_bvec`, `bvec_init_iter_all()`, and `bvec_advance()`. Mapping/copy helpers include `bvec_kmap_local()`, `memcpy_from_bvec()`, `memcpy_to_bvec()`, `memzero_bvec()`, `bvec_virt()`, and `bvec_phys()`.

**Control flow, state, persistence:** Iterators mutate only in-memory cursor state; `bi_size` shrinks as bytes are consumed. Segment descriptors are views over existing pages/folios, not owners of storage.

**Dependencies/integration:** Depends on highmem, pages/folios, warning helpers, min/max, and memory copy helpers. It integrates tightly with `bio`, block layer splitting, and filesystem I/O.

**Risks and test signals:** Risks include advancing past end, assuming multipage bvecs are single-page, using `bvec_virt()` on highmem, offset overflow, and losing sector updates because bare bvec helpers do not maintain `bi_sector`. Test signals are bio splitting/merging tests, highmem builds, KASAN bounds checks, WARN coverage for over-advance, and block I/O corruption tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/big_endian.h -->
## sources/distributed-fs/ceph-client/include/linux/byteorder/big_endian.h

**Purpose:** This header selects big-endian byteorder definitions for kernel code.

**Important APIs/types/functions:** It includes `<uapi/linux/byteorder/big_endian.h>`, emits a preprocessor warning if `CONFIG_CPU_BIG_ENDIAN` is not set, then includes `linux/byteorder/generic.h`.

**Control flow, state, persistence:** There is no runtime state. It establishes compile-time conversion macros such as `cpu_to_be*`, `be*_to_cpu`, and little-endian swap forms through the UAPI and generic layers.

**Dependencies/integration:** Depends on the architecture/Kconfig endian selection and generic byteorder aliases.

**Risks and test signals:** Risks are inconsistent Kconfig/include selection and drivers manually bypassing conversion macros. Test signals are big-endian compile builds, sparse endian annotations, and protocol/filesystem round-trip tests on big-endian targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/big_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/generic.h -->
## sources/distributed-fs/ceph-client/include/linux/byteorder/generic.h

**Purpose:** This header maps architecture-provided byteorder primitives onto standard kernel conversion names.

**Important APIs/types/functions:** It aliases `cpu_to_le64`, `le64_to_cpu`, `cpu_to_le32`, `le32_to_cpu`, `cpu_to_le16`, `le16_to_cpu`, corresponding big-endian forms, pointer forms `*p`, and in-place forms `*s` to underlying `__cpu_to_*`, `__*_to_cpu`, and related architecture/UAPI macros.

**Control flow, state, persistence:** There is no runtime state. The macros are compile-time conversion entry points that may become swaps or no-ops depending on architecture endian.

**Dependencies/integration:** Intended to be included by `big_endian.h` or `little_endian.h` after architecture/UAPI byteorder primitives are defined. Used by on-disk, network, firmware, and MMIO protocol code.

**Risks and test signals:** Risks include using pointer conversion macros on unaligned data, missing architecture definitions, and mixing CPU/native values with annotated endian types. Test signals include sparse endian warnings, unaligned-access tests, filesystem/network protocol interoperability, and cross-endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/little_endian.h -->
## sources/distributed-fs/ceph-client/include/linux/byteorder/little_endian.h

**Purpose:** This header selects little-endian byteorder definitions for kernel code.

**Important APIs/types/functions:** It includes `<uapi/linux/byteorder/little_endian.h>`, warns if `CONFIG_CPU_BIG_ENDIAN` is set, and includes `linux/byteorder/generic.h`.

**Control flow, state, persistence:** There is no runtime state. It defines the compile-time conversion surface used by native and protocol code.

**Dependencies/integration:** Depends on architecture/Kconfig endian selection and generic byteorder aliases.

**Risks and test signals:** Risks are Kconfig/include inconsistency and code that assumes little-endian layout without explicit conversion. Test signals include little-endian build coverage, sparse endian checking, and protocol/filesystem round trips against big-endian peers or images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/byteorder/little_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/c2port.h -->
## sources/distributed-fs/ceph-client/include/linux/c2port.h

**Purpose:** This header defines the Silicon Labs C2 debug/programming port framework interface.

**Important APIs/types/functions:** `C2PORT_NAME_LEN` limits device names. `struct c2port_device` stores access flags, ID, name, operations, mutex, device pointer, and private data. `struct c2port_ops` supplies flash geometry plus GPIO-like callbacks for access enable, C2D direction/read/write, and C2CK clock writes. Functions are `c2port_device_register()` and `c2port_device_unregister()`.

**Control flow, state, persistence:** Framework code serializes read/write through the per-device mutex and delegates signal toggling to provider callbacks. Flash persistence belongs to the target device accessed over C2; this header only models the host-side control surface.

**Dependencies/integration:** Requires `struct device` and mutex support from included users. Integrates platform-specific bit-banging drivers with the C2 core and sysfs/debug interfaces implemented elsewhere.

**Risks and test signals:** Risks are timing-sensitive line toggling, missing mutual exclusion, incorrect flash block geometry, and failing to disable access on unregister/error. Test signals include register/unregister tests, concurrent sysfs access, flash read/write/erase on known C2 devices, and GPIO trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/c2port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cache.h -->
## sources/distributed-fs/ceph-client/include/linux/cache.h

**Purpose:** This header defines cacheline alignment, placement, and structure-layout helpers used for performance and false-sharing control.

**Important APIs/types/functions:** It provides `L1_CACHE_ALIGN`, `SMP_CACHE_ALIGN`, `LARGEST_ALIGN`, `__read_mostly`, `__ro_after_init`, `__cacheline_aligned`, `__cacheline_aligned_in_smp`, internode alignment helpers, `cache_line_size()`, cacheline group markers, `CACHELINE_ASSERT_GROUP_MEMBER`, `CACHELINE_ASSERT_GROUP_SIZE`, `CACHELINE_PADDING`, and `ARCH_DMA_MINALIGN` fallback.

**Control flow, state, persistence:** No runtime control flow except optional `cache_line_size()` macro/function. The helpers affect linker sections, alignment, and struct padding, which changes object placement and memory layout.

**Dependencies/integration:** Includes UAPI alignment helpers, VDSO cache data, and architecture cache definitions. Used broadly by hot-path networking, scheduler, MM, block, and driver data structures.

**Risks and test signals:** Risks are ABI/layout changes, excessive padding, false sharing from missing alignment, and misuse of `__read_mostly` without performance justification. Test signals include pahole/layout checks, cacheline group build assertions, perf false-sharing traces, and DMA alignment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cache_coherency.h -->
## sources/distributed-fs/ceph-client/include/linux/cache_coherency.h

**Purpose:** This header defines a driver-facing framework for cache coherency maintenance operation providers.

**Important APIs/types/functions:** `struct cc_inval_params` carries physical address and size. `struct cache_coherency_ops` exposes `wbinv()` and `done()` callbacks. `struct cache_coherency_ops_inst` embeds a `kref`, list node, and ops pointer. APIs include register/unregister, `_cache_coherency_ops_instance_alloc()`, typed `cache_coherency_ops_instance_alloc()`, and `cache_coherency_ops_instance_put()`.

**Control flow, state, persistence:** Providers allocate/register instances, callers invoke operations through framework code implemented elsewhere, and refs control instance lifetime. Maintenance operations affect hardware cache state but create no persistent storage.

**Dependencies/integration:** Depends on list, kref, phys address types, and `static_assert`/`offsetof` constraints. The typed allocator requires the embedded instance member to be at offset zero.

**Risks and test signals:** Risks are freeing registered instances, embedding the instance at nonzero offset, incomplete `done()` sequencing, and invalid physical ranges. Test signals include provider register/unregister, refcount leak tests, invalidation/writeback-invalidate hardware validation, and compile failures for malformed embedding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cache_coherency.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cacheflush.h -->
## sources/distributed-fs/ceph-client/include/linux/cacheflush.h

**Purpose:** This header supplies generic cache flush wrappers around architecture implementations.

**Important APIs/types/functions:** It includes `asm/cacheflush.h`, declares or stubs `flush_dcache_folio()` depending on `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, provides a default no-op `flush_icache_pages()` if the architecture does not define it, and maps `flush_icache_page()` to a one-page call.

**Control flow, state, persistence:** Runtime behavior is architecture dependent. On non-implementing architectures the helpers are no-ops; on implementing architectures they synchronize data/instruction cache visibility for pages/folios.

**Dependencies/integration:** Integrates MM, filesystems, executable mappings, and architecture cache maintenance code. Uses `struct folio`, `struct vm_area_struct`, and `struct page` declarations from surrounding includes.

**Risks and test signals:** Risks are missing flushes on aliasing or non-coherent architectures, over-flushing hot paths, and assuming no-op behavior across all platforms. Test signals include executable mmap/write tests, D-cache aliasing tests, architecture cacheflush selftests, and cross-arch compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cacheinfo.h -->
## sources/distributed-fs/ceph-client/include/linux/cacheinfo.h

**Purpose:** This header describes CPU cache topology data and exposes cacheinfo discovery helpers.

**Important APIs/types/functions:** `enum cache_type` classifies instruction, data, separate, and unified caches. `struct cacheinfo` stores cache ID, type, level, line size, sets, ways, partitions, size, shared CPU mask, attributes, firmware token, sysfs disable flag, and private data. `struct cpu_cacheinfo` stores per-CPU cache leaf arrays and discovery flags. APIs include `get_cpu_cacheinfo()`, early/init/populate helpers, ACPI/PPTT and OF cache setup, last-level cache queries, `cache_get_priv_group()`, `get_cpu_cacheinfo_level()`, `get_cpu_cacheinfo_id()`, `use_arch_cache_info()`, and aliasing macros.

**Control flow, state, persistence:** Cacheinfo is populated during CPU topology initialization/hotplug and may be exposed through sysfs. Inline lookup helpers require the CPU hotplug lock and scan per-CPU leaf arrays.

**Dependencies/integration:** Depends on bitops, CPU masks, CPU hotplug locking, SMP, ACPI PPTT, OF, and architecture cachetype support.

**Risks and test signals:** Risks include missing hotplug locking, incorrect shared CPU masks, firmware token mismatches, wrong aliasing detection, and exposing invalid sysfs leaves. Test signals include cache sysfs topology tests, CPU hotplug, ACPI/DT boot variants, last-level sharing checks, and lockdep for `cpus_read_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cacheinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/call_once.h -->
## sources/distributed-fs/ceph-client/include/linux/call_once.h

**Purpose:** This header provides a small synchronization primitive to run an initialization callback exactly once after it succeeds.

**Important APIs/types/functions:** State constants are `ONCE_NOT_STARTED`, `ONCE_RUNNING`, and `ONCE_COMPLETED`. `struct once` stores an atomic state and mutex. `once_init()` initializes the object with a lock class key. `call_once(struct once *once, int (*cb)(struct once *))` runs the callback if not completed.

**Control flow, state, persistence:** Fast path uses `atomic_read_acquire()` to skip locking once completed. Slow path takes the mutex, rejects unexpected state, marks running, invokes `cb`, resets to not-started on negative return, or stores completed with release ordering on success. State persists in the `struct once` object for the lifetime of the owning subsystem.

**Dependencies/integration:** Depends on atomics, mutexes, lockdep lock classes, and guard-based mutex cleanup.

**Risks and test signals:** Risks include failing to call `once_init()`, callback recursion on the same object, callbacks that return success before publishing all state, and unexpected `ONCE_RUNNING` states causing `-EINVAL`. Test signals include concurrent caller stress tests, failure-then-retry behavior, lockdep checks, and memory-order tests for initialized data visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/call_once.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/bittiming.h -->
## sources/distributed-fs/ceph-client/include/linux/can/bittiming.h

**Purpose:** This header defines CAN bit-timing, CAN FD/XL transmission-delay compensation, PWM timing, and calculation/validation interfaces for CAN network drivers.

**Important APIs/types/functions:** Constants include `CAN_SYNC_SEG`, unset/unknown bitrate sentinels, and TDC ctrlmode masks. Types include `struct can_tdc`, `can_tdc_const`, `can_pwm`, `can_pwm_const`, and `data_bittiming_params`. APIs include config-gated `can_calc_bittiming()`, `can_calc_tdco()`, `can_calc_pwm()`, plus `can_sjw_set_default()`, `can_sjw_check()`, `can_get_bittiming()`, `can_validate_pwm_bittiming()`, and inline helpers `can_get_relative_tdco()`, `can_bit_time()`, `can_bit_time_tqmin()`, and `can_tqmin_to_ns()`.

**Control flow, state, persistence:** Calculation helpers fill driver-owned timing structures from requested bitrate/sample-point constraints. If `CONFIG_CAN_CALC_BITTIMING` is absent, calculation stubs report `-EINVAL` through netlink extack. Timing state persists in `struct can_priv` fields.

**Dependencies/integration:** Depends on netdevice and CAN netlink UAPI. Integrated by CAN drivers during netlink configuration and device open/reconfigure paths.

**Risks and test signals:** Risks include invalid segment limits, mixing absolute and relative TDCO semantics, failing to respect ctrlmode support, and config-disabled behavior not surfaced to users. Test signals include iproute2 bitrate configuration, extack messages, CAN FD/XL TDC cases, PWM validation, and hardware loopback at configured rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/bittiming.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/can-ml.h -->
## sources/distributed-fs/ceph-client/include/linux/can/can-ml.h

**Purpose:** This header defines CAN network-layer private state and receive-list containers used by the PF_CAN core.

**Important APIs/types/functions:** Capability bits are `CAN_CAP_CC`, `CAN_CAP_FD`, `CAN_CAP_XL`, and `CAN_CAP_RO`. Receive-list constants size SFF direct arrays and EFF hash arrays. `struct can_dev_rcv_lists` contains generic, SFF, and EFF receive hlist heads plus entry count. `struct can_ml_priv` stores device receive lists, optional J1939 private state, and capability mask. Inline helpers are `can_get_ml_priv()`, `can_set_ml_priv()`, `can_cap_enabled()`, and `can_set_cap()`.

**Control flow, state, persistence:** The header stores per-netdevice receive filter state and capabilities. Inline helpers attach/retrieve this state through netdevice ML private slots.

**Dependencies/integration:** Depends on CAN IDs, hlist/list infrastructure, netdevice ML private data, and optional J1939 integration.

**Risks and test signals:** Risks include uninitialized ML private state, stale receive-list entries on device unregister, capability masks inconsistent with device MTU/ctrlmode, and optional J1939 build coverage. Test signals include PF_CAN receive filter registration/unregistration, SFF/EFF dispatch tests, capability reporting, and netdevice teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/can-ml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/core.h -->
## sources/distributed-fs/ceph-client/include/linux/can/core.h

**Purpose:** This header exposes the PF_CAN core interfaces used by CAN protocol modules and drivers.

**Important APIs/types/functions:** `DNAME()` formats device names for optional devices. `struct can_proto` binds socket type/protocol to proto ops and `struct proto`. `CAN_REQUIRED_SIZE()` computes the minimum structure size containing a member. APIs include `can_proto_register()`, `can_proto_unregister()`, `can_rx_register()`, `can_rx_unregister()`, `can_send()`, `can_set_skb_uid()`, and `can_sock_destruct()`.

**Control flow, state, persistence:** Protocol modules register socket protocols; receive callbacks are attached to net namespaces/devices with CAN ID and mask filters; `can_send()` injects frames with optional loopback. Runtime filter tables and protocol lists live in AF_CAN implementation state.

**Dependencies/integration:** Depends on CAN UAPI, skbuffs, netdevices, network namespaces, and sockets. It is the shared integration point for raw, BCM, ISO-TP, J1939, and driver-facing CAN code.

**Risks and test signals:** Risks are filter lifetime races, mismatched register/unregister callback/data pairs, namespace leaks, and sending malformed SKBs. Test signals include PF_CAN protocol load/unload, receive filter matching, loopback behavior, namespace teardown, and socket destructor/refcount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/dev.h -->
## sources/distributed-fs/ceph-client/include/linux/can/dev.h

**Purpose:** This header defines the common CAN network-device driver interface and `struct can_priv` base private data.

**Important APIs/types/functions:** `enum can_mode` models stop/start/sleep; `enum can_termination_gpio` models termination GPIO states. `struct can_priv` stores netdev pointer, CAN stats, nominal/data/XL bittiming, bitrate constraints, clock, termination data/GPIO, echo SKBs, state, ctrlmode, restart work, and driver callbacks. APIs include CAN netdev allocation/free/open/close, registration, restart/bus-off handling, static ctrlmode setup, timestamping ethtool helpers, state-string helpers, state transitions, and OF transceiver setup.

**Control flow, state, persistence:** Drivers allocate a candev, fill constraints/callbacks, open/close through common helpers, update ctrlmode/state, queue restart work on bus-off, and use `can_dev_dropped_skb()` to reject sends that violate mode/frame constraints. State is runtime netdevice state.

**Dependencies/integration:** Depends on CAN bittiming/error/length/netlink/SKB helpers, ethtool, netdevice, GPIO, delayed work, and optional OF.

**Risks and test signals:** Risks include ctrlmode/MTU mismatch, leaking echo SKBs, wrong bus-off restart timing, accepting FD/XL frames when disabled, and unpaired open/close. Test signals include netlink ctrlmode changes, CAN FD/XL send rejection, bus-off recovery, timestamping queries, echo SKB accounting, and register/unregister tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/dev/peak_canfd.h -->
## sources/distributed-fs/ceph-client/include/linux/can/dev/peak_canfd.h

**Purpose:** This header defines the PEAK System uCAN protocol command and message layouts used by PEAK CAN FD capable adapters.

**Important APIs/types/functions:** It enumerates command opcodes (`PUCAN_CMD_*`), received/transmitted message types (`PUCAN_MSG_*`), command structs for reset/mode/timing/filter/abort/error-count/options, message structs for RX/TX/error/status/busload, and many field masks. Inline helpers extract command opcode, build opcode/channel fields, and read channel/DLC/status bits from little-endian packed protocol messages.

**Control flow, state, persistence:** The header models firmware wire-format state. Drivers build packed commands, send them to hardware/firmware, parse incoming message collections, and translate status/error bits into CAN stack state. Persistent device configuration such as filters and timing lives in adapter firmware after commands are accepted.

**Dependencies/integration:** Depends on endian helpers and packed layout rules. Integrated by PEAK USB/PCI drivers with CAN core, bittiming, and SKB translation.

**Risks and test signals:** Risks include packed-struct alignment, endian mistakes, opcode/channel bit overlap, DLC conversion errors, and firmware version drift. Test signals include bus analyzer traces, hardware loopback, FD/bitrate-switch frames, status/error injection, filter programming validation, and sparse endian checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/dev/peak_canfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/length.h -->
## sources/distributed-fs/ceph-client/include/linux/can/length.h

**Purpose:** This header calculates Classical CAN and CAN FD frame wire lengths and provides DLC/length conversion helpers.

**Important APIs/types/functions:** It defines bit counts for standard/extended CAN and CAN FD headers, CRC fields, footers, and intermission. Macros include `can_bitstuffing_len()`, `can_frame_bits()`, `can_frame_bytes()`, `CAN_FRAME_LEN_MAX`, `CANFD_FRAME_LEN_MAX`, and `can_cc_dlc2len()`. Inline helpers handle Classical CAN raw DLC (`can_get_cc_dlc()`, `can_frame_set_cc_len()`) and FD sanitization. External APIs are `can_fd_dlc2len()`, `can_fd_len2dlc()`, and `can_skb_get_frame_len()`.

**Control flow, state, persistence:** Macro calculations are pure arithmetic. Classical CAN raw DLC handling conditionally preserves `len8_dlc` only when ctrlmode allows it. No persistent state is stored here.

**Dependencies/integration:** Depends on CAN UAPI frame layouts, CAN netlink ctrlmode, math helpers, and SKBs. Used by drivers and statistics paths that estimate bus load or validate frame sizes.

**Risks and test signals:** Risks include passing unsanitized `data_len`, confusing RTR actual data length with DLC, FD CRC17/CRC21 threshold errors, and bitstuffing worst-case assumptions. Test signals include known frame-length vectors, DLC round trips, SKB length tests for CAN/CAN FD/CAN XL, and busload calculations compared with analyzer measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/length.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/cc770.h -->
## sources/distributed-fs/ceph-client/include/linux/can/platform/cc770.h

**Purpose:** This header defines platform data and register bit masks for Intel/Bosch CC770-style CAN controller drivers.

**Important APIs/types/functions:** It exports CPU interface register bits (`CPUIF_*`), clock-out masks/shifts, bus configuration bits (`BUSCFG_*`), and `struct cc770_platform_data` with oscillator frequency and register defaults `cir`, `cor`, and `bcr`.

**Control flow, state, persistence:** No code runs here. Platform data is consumed during driver probe to program hardware interface, clock, and bus behavior. Hardware register values persist in the controller until reset/reconfiguration.

**Dependencies/integration:** Used by board/platform descriptions and CC770 driver probe paths.

**Risks and test signals:** Risks include wrong oscillator frequency, clock-divider settings, RX/TX pin polarity mistakes, and platform data that leaves the controller in sleep/reset. Test signals are probe initialization traces, CAN bit-timing accuracy, loopback traffic, and board-specific RX/TX pin validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/cc770.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/flexcan.h -->
## sources/distributed-fs/ceph-client/include/linux/can/platform/flexcan.h

**Purpose:** This header defines minimal platform data for FlexCAN devices that are not fully described by firmware.

**Important APIs/types/functions:** `struct flexcan_platform_data` carries `clock_frequency` and `clk_src`.

**Control flow, state, persistence:** There is no code. The driver consumes this data during probe to select clock source/frequency for bit timing. Hardware state persists in FlexCAN registers managed by the driver.

**Dependencies/integration:** Used by platform-board code and the FlexCAN driver, alongside device tree/ACPI paths.

**Risks and test signals:** Risks are stale board data, wrong clock source, and timing drift. Test signals include probe with platform data, configured bitrate verification, CAN loopback/traffic tests, and comparison with firmware-described boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/flexcan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/sja1000.h -->
## sources/distributed-fs/ceph-client/include/linux/can/platform/sja1000.h

**Purpose:** This header defines platform data and register-bit settings for SJA1000-compatible CAN controllers.

**Important APIs/types/functions:** It exports clock-divider register bits (`CDR_*`), output-control register mode/drive bits (`OCR_*`), and `struct sja1000_platform_data` with oscillator frequency, OCR, and CDR values.

**Control flow, state, persistence:** No runtime logic exists here. Probe code uses platform data to program controller output, clock, RX comparator, and PeliCAN mode. Hardware state persists until reset or driver reinitialization.

**Dependencies/integration:** Used by SJA1000 platform/ISA/PCI style drivers and board files.

**Risks and test signals:** Risks include mismatched oscillator frequency, disabling clock output unexpectedly, incorrect TX output drive mode, or missing PeliCAN mode. Test signals include bit-timing checks, loopback, RX/TX pin electrical validation, and probe register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/platform/sja1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/rx-offload.h -->
## sources/distributed-fs/ceph-client/include/linux/can/rx-offload.h

**Purpose:** This header defines helper state and APIs for CAN drivers that offload receive handling into NAPI-backed queues.

**Important APIs/types/functions:** `struct can_rx_offload` stores netdev, mailbox-read callback, normal and IRQ SKB queues, max queue length, mailbox range, NAPI object, and direction flag. APIs add timestamp/FIFO/manual offload modes, queue timestamped or tail SKBs, retrieve echo SKBs into queues, finish IRQ/threaded IRQ receive processing, delete, enable, and disable offload.

**Control flow, state, persistence:** Drivers initialize offload, enqueue received SKBs from interrupt context, and finish IRQ handling to schedule NAPI. NAPI drains queues into the network stack. State is transient queue/NAPI state tied to the netdevice.

**Dependencies/integration:** Depends on netdevice, NAPI, CAN SKB helpers, and driver mailbox/timestamp hardware.

**Risks and test signals:** Risks include queue overflow, timestamp ordering mistakes, incorrect mailbox direction, NAPI lifecycle races, and using non-IRQ-safe paths in interrupt context. Test signals include high-rate RX stress, timestamp ordering tests, bus-off/error traffic, NAPI enable/disable during open/close, and echo SKB accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/rx-offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/skb.h -->
## sources/distributed-fs/ceph-client/include/linux/can/skb.h

**Purpose:** This header defines CAN SKB allocation, echo, validation, ownership, and frame-length helper interfaces.

**Important APIs/types/functions:** APIs include echo buffer management (`can_flush_echo_skb`, `can_put_echo_skb`, `__can_get_echo_skb`, `can_get_echo_skb`, `can_free_echo_skb`), allocation helpers for Classical CAN, CAN FD, CAN XL, and error SKBs, and `can_dropped_invalid_skb()`. Inline helpers add/find CAN SKB extensions, safely assign socket ownership, clone echo SKBs, identify CAN/CAN FD/CAN XL SKB payloads, and extract payload length/data length with RTR awareness.

**Control flow, state, persistence:** Echo helpers store SKB references in `struct can_priv` echo slots until transmit completion. Validation helpers inspect `skb->len` and frame payload fields. Ownership helpers conditionally take a socket reference only if it is still alive.

**Dependencies/integration:** Depends on skbuff extensions, CAN frame UAPI, net/can, sockets, and netdevice stats.

**Risks and test signals:** Risks include echo slot leaks, double-free on clone failure, accepting malformed CAN XL lengths, socket refcount races, and RTR length confusion. Test signals include CAN_RAW loopback/echo tests, invalid SKB drop counters, CAN FD/XL allocation tests, socket close during TX, and KASAN/refcount debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/can/skb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/capability.h -->
## sources/distributed-fs/ceph-client/include/linux/capability.h

**Purpose:** This header defines the in-kernel capability representation and authorization helpers around user namespaces, files, and inode ownership.

**Important APIs/types/functions:** `kernel_cap_t` wraps a `u64`. `struct cpu_vfs_cap_data` stores xattr capability data in CPU endian form. Macros define kernel capability version, FS/NFSD masks, empty/full sets, and operations such as `cap_clear`, `cap_raise`, `cap_lower`, `cap_raised`, `cap_combine`, `cap_intersect`, `cap_drop`, `cap_isclear`, `cap_isidentical`, and `cap_issubset`. Capability check APIs include `capable()`, `ns_capable()`, no-audit variants, inode-aware helpers, `file_ns_capable()`, `ptracer_capable()`, and specialized `perfmon_capable()`, `bpf_capable()`, and checkpoint/restore helpers. File-capability APIs parse/convert disk xattrs.

**Control flow, state, persistence:** Capability sets are bitmasks in credentials and file xattrs. With `CONFIG_MULTIUSER=n`, checks stub to true. File capability xattrs persist on disk and are converted through VFS/idmap helpers.

**Dependencies/integration:** Depends on UAPI capabilities, UID/GID types, user namespaces, mount idmaps, VFS dentries/inodes/files, and LSM/audit implementation.

**Risks and test signals:** Risks include fallback to `CAP_SYS_ADMIN`, namespace confusion, idmapped mount conversion mistakes, and config-off assumptions. Test signals include LTP capability tests, filecap xattr round trips, user namespace tests, BPF/perf permission tests, and `CONFIG_MULTIUSER=n` compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cb710.h -->
## sources/distributed-fs/ceph-client/include/linux/cb710.h

**Purpose:** This header defines shared structures and helpers for the CB710 PCI card-reader driver and its virtual slots.

**Important APIs/types/functions:** `struct cb710_slot` embeds a platform device, MMIO base, and IRQ handler. `struct cb710_chip` stores PCI device, MMIO base, platform ID, optional debug refcount, slot mask/count, IRQ spinlock, and flexible slot array. Slot masks identify MMC/MS/SM slots. Macro-generated port accessors create 8/16/32-bit read/write/modify helpers. APIs include `cb710_pci_update_config_reg()`, `cb710_set_irq_handler()`, container conversion helpers, device accessors, optional `cb710_dump_regs()`, and scatter-gather PIO helpers `cb710_sg_dwiter_*`.

**Control flow, state, persistence:** Runtime state tracks slots, platform devices, IRQ handler dispatch, and MMIO register values. SG iterator helpers transfer 32-bit words between IO ports and mapped scatterlist buffers, advancing iterator state.

**Dependencies/integration:** Depends on PCI, platform devices, MMIO, IRQ/spinlock, MMC host, scatterlist mapping, and highmem.

**Risks and test signals:** Risks include MMIO width mistakes, IRQ handler races, slot lifetime/refcount bugs, and SG iterator over/under-run behavior. Test signals include card insertion/removal, MMC transfer tests, IRQ stress, debug register dumps, SG PIO boundary tests, and PCI config update validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cb710.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cc_platform.h -->
## sources/distributed-fs/ceph-client/include/linux/cc_platform.h

**Purpose:** This header declares a generic confidential-computing platform capability query interface.

**Important APIs/types/functions:** `enum cc_attr` lists active platform attributes such as host/guest memory encryption, guest state encryption, string I/O unrolling, SEV-SNP, TDX, memory acceptance requirements, and host SNP. The primary API is `cc_platform_has(enum cc_attr attr)` declared later in the header implementation surface.

**Control flow, state, persistence:** Callers query whether a security/platform attribute is active before choosing memory, I/O, and virtualization behavior. State is derived from architecture/platform initialization, not stored by this header.

**Dependencies/integration:** Depends on generic types and architecture confidential-computing backends. Used by x86/arm64 memory encryption, DMA, I/O, and virtualization-sensitive code.

**Risks and test signals:** Risks include treating attributes as compile-time constants, assuming one vendor feature implies another, and missing fallbacks for encrypted guests. Test signals include architecture CC boot tests, SEV/TDX/SNP guest runs, memory acceptance tests, and compile coverage on non-CC architectures where queries return false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cc_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cciss_ioctl.h -->
## sources/distributed-fs/ceph-client/include/linux/cciss_ioctl.h

**Purpose:** This header bridges CCISS block-driver ioctl UAPI into kernel code and defines 32-bit compat passthrough ioctl structures when needed.

**Important APIs/types/functions:** It includes `<uapi/linux/cciss_ioctl.h>`. Under `CONFIG_COMPAT`, it defines `IOCTL32_Command_struct`, `BIG_IOCTL32_Command_struct`, and compat ioctl numbers `CCISS_PASSTHRU32` and `CCISS_BIG_PASSTHRU32`, with 32-bit user pointers represented as `__u32`.

**Control flow, state, persistence:** No runtime logic is in the header. The compat structs guide ioctl translation in driver code; request execution and controller state live elsewhere.

**Dependencies/integration:** Depends on UAPI CCISS types and compat configuration. Integrated by legacy HP Smart Array/CCISS ioctl handling.

**Risks and test signals:** Risks include pointer truncation/extension mistakes, struct packing drift versus userspace ABI, and missing compat handlers on 64-bit kernels. Test signals include 32-bit userspace ioctl passthrough tests on 64-bit kernels, ABI size checks, and request error-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cciss_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ccp.h -->
## sources/distributed-fs/ceph-client/include/linux/ccp.h

**Purpose:** This header defines the client-facing command interface for AMD Cryptographic Coprocessor (CCP) operations.

**Important APIs/types/functions:** Config-gated APIs are `ccp_present()`, `ccp_version()`, and `ccp_enqueue_cmd()`, stubbing to `-ENODEV`/0 when CCP support is unavailable. It defines operation enums and parameter structs for AES, XTS-AES, SHA/HMAC, 3DES, RSA, passthrough, no-DMA passthrough, and ECC. `enum ccp_engine` selects the engine. `struct ccp_cmd` contains driver-owned list/work/device/return fields, flags (`CCP_CMD_MAY_BACKLOG`, `CCP_CMD_PASSTHRU_NO_DMA_MAP`), selected engine, engine error, a union of engine parameters, completion callback, and callback data.

**Control flow, state, persistence:** Clients fill a `ccp_cmd`, submit it, and receive completion through callback. Backlog-capable commands may complete first with `-EINPROGRESS` when promoted from backlog. Scatterlists and IV/hash contexts may be both input and output for certain engines. No data persists except hardware/driver queue state and caller buffers.

**Dependencies/integration:** Depends on scatterlists, workqueues, lists, DMA addresses, and crypto constants. Integrated by crypto API drivers and hardware acceleration users.

**Risks and test signals:** Risks include missing required fields per engine, invalid scatterlist lifetimes, callback races, unhandled backlog returns, IV/context mutation surprises, and config-off behavior. Test signals include crypto selftests for each engine/mode, async completion/backlog tests, DMA mapping debug, hardware error injection, and module unload with queued commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ccp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdev.h -->
## sources/distributed-fs/ceph-client/include/linux/cdev.h

**Purpose:** This header defines the kernel character-device core object and registration helpers.

**Important APIs/types/functions:** `struct cdev` embeds a `kobject`, module owner, file operations pointer, list node, and device number/count. APIs include `cdev_init()`, `cdev_alloc()`, `cdev_put()`, `cdev_add()`, `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`, `cdev_del()`, and `cd_forget()`.

**Control flow, state, persistence:** Drivers initialize or allocate a `cdev`, bind file operations and device numbers, add it to the char-device map, optionally bind it to a device object, then delete/put during teardown. State persists in the VFS/device model while registered.

**Dependencies/integration:** Depends on kobjects, modules, file operations, inodes, and device numbers. Integrates with `device_create()`, sysfs, devtmpfs/udev, and VFS open path.

**Risks and test signals:** Risks include registering before file ops are ready, device-number collisions, parent lifetime bugs, deleting while open without correct refcounts, and mixing `cdev_add` with `cdev_device_add` incorrectly. Test signals include open/read/write/ioctl smoke tests, hot-unplug while open, sysfs/devnode checks, module unload, and refcount debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdrom.h -->
## sources/distributed-fs/ceph-client/include/linux/cdrom.h

**Purpose:** This header defines the uniform in-kernel CD-ROM driver interface and shared packet-command/media structures.

**Important APIs/types/functions:** `struct packet_command` carries a SCSI/MMC packet, data buffer, length, status, sense header, data direction, quiet flag, and timeout. `struct cdrom_device_info` stores operations, disk handle, capabilities/options, cached events, use count, name, changer/media flags, CDDA method, sense/media state, MMC profile, and open-for-data flag. `struct cdrom_device_ops` contains driver callbacks for open/release/status/events/tray/door/speed/session/MCN/reset/audio/generic packet/CDDA. APIs include `cdrom_open()`, `cdrom_release()`, `cdrom_ioctl()`, event checks, registration, TOC/session helpers, mode sense/select, command initialization, and dummy packet fallback. Additional packed structures model changer/mechanism and MMC mode pages.

**Control flow, state, persistence:** The uniform layer routes block-device operations and ioctls to device ops, caches media events, manages open counts, and sends packet commands to hardware. Persistent state is media/device state and cached flags in `cdrom_device_info`.

**Dependencies/integration:** Depends on block devices, gendisk, SCSI sense, UAPI CD-ROM ioctls, and endianness bitfields.

**Risks and test signals:** Risks include ABI packing/bitfield endian bugs, stale media-change events, door-lock leaks, sense-data handling mistakes, and ioctl permission issues. Test signals include cdrom ioctl suites, media insert/eject, multisession/TOC reads, packet-command error paths, changer slot tests, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdrom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/bitfield.h -->
## sources/distributed-fs/ceph-client/include/linux/cdx/bitfield.h

**Purpose:** This header provides CDX firmware/protocol bitfield helpers for little-endian 32-bit dwords.

**Important APIs/types/functions:** It defines field-attribute helpers `CDX_VAL`, `CDX_LOW_BIT`, `CDX_WIDTH`, and `CDX_HIGH_BIT`, `struct cdx_dword` wrapping `__le32`, `CDX_DWORD_VAL()`, `CDX_DWORD_FIELD()`, `CDX_INSERT_FIELD()`, `CDX_INSERT_FIELDS()`, `CDX_POPULATE_DWORD()`, arity adapters `CDX_POPULATE_DWORD_1..7`, and `CDX_SET_DWORD()`.

**Control flow, state, persistence:** Helpers are pure macro transformations. They extract or populate protocol fields using `FIELD_GET/PREP`, masks built from `_LBN/_WIDTH` constants, and CPU/little-endian conversions.

**Dependencies/integration:** Depends on `linux/bitfield.h` and byteorder helpers. Used by CDX MCDI protocol code and generated command headers.

**Risks and test signals:** Risks include undefined field metadata, values too wide for the field, endian omissions, and macro argument ordering mistakes. Test signals include compile-time field metadata checks, protocol encode/decode round trips, sparse endian warnings, and firmware command traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/cdx_bus.h -->
## sources/distributed-fs/ceph-client/include/linux/cdx/cdx_bus.h

**Purpose:** This header exposes the public CDX bus interface for AMD/Xilinx CDX controllers, devices, and drivers.

**Important APIs/types/functions:** Constants include resource limits and bus/controller ID helpers. `struct cdx_device_config` models MSI, bus-master, reset, and MSI-enable configuration. `struct cdx_ops` supplies controller callbacks for bus enable/disable, scan, and device configure. `struct cdx_controller` stores backing device, private data, MSI domain, ID, registration state, and ops. `struct cdx_device` embeds a device object, IDs, resources, DMA mask, flags, bus/dev numbers, MSI fields, driver override, and IRQ-chip state. `struct cdx_driver` wraps driver model callbacks. APIs include `__cdx_driver_register()`, `cdx_driver_unregister()`, `cdx_dev_reset()`, `cdx_set_master()`, `cdx_clear_master()`, resource macros, conversion macros, and external `cdx_bus_type`.

**Control flow, state, persistence:** Controllers register, scan buses, create devices, and route configuration requests to controller ops. Drivers bind by ID table, probe/remove/shutdown, and receive reset notifications. Device enable/MSI/master state is runtime hardware/bus state.

**Dependencies/integration:** Depends on Linux device model, MSI/IRQ domains, module device tables, resources, debugfs, and DMA/IOMMU policy.

**Risks and test signals:** Risks include resource-count overflow, driver-override lifetime mistakes, MSI locking races, reset callback ordering, and bus-mastering/IOMMU policy errors. Test signals include CDX enumeration, driver bind/unbind, reset and MSI tests, DMA/IOMMU validation, and hot-remove/resource sysfs checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/cdx_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/edac_cdx_pcol.h -->
## sources/distributed-fs/ceph-client/include/linux/cdx/edac_cdx_pcol.h

**Purpose:** This header defines CDX MCDI protocol constants for EDAC DDR configuration queries.

**Important APIs/types/functions:** It includes CDX MCDI helpers and defines `MC_CMD_EDAC_GET_DDR_CONFIG`, input offset/length for `CONTROLLER_INDEX`, output word length, and DDR config register offset/length constants.

**Control flow, state, persistence:** There is no code. EDAC/CDX clients use these constants to encode MCDI requests and decode responses for DDR controller configuration. Returned configuration reflects hardware/firmware state.

**Dependencies/integration:** Depends on `linux/cdx/mcdi.h` and the CDX firmware command protocol. Integrated by EDAC drivers that query CDX-managed DDR controllers.

**Risks and test signals:** Risks are protocol-version drift, incorrect offset/length interpretation, and insufficient output buffer sizing. Test signals include successful `cdx_mcdi_rpc()` for DDR config, decoded EDAC topology, firmware negative responses, and buffer length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/edac_cdx_pcol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/mcdi.h -->
## sources/distributed-fs/ceph-client/include/linux/cdx/mcdi.h

**Purpose:** This header defines the CDX Management Controller Diagnostic Interface (MCDI) protocol state, command tracking, and request/response helpers.

**Important APIs/types/functions:** `enum cdx_mcdi_mode` selects event wait or fail-fast mode. `enum cdx_mcdi_cmd_state` tracks queued, retry, running, cancelled, and finished commands. `struct cdx_mcdi` stores protocol data, ops, remoteproc/RPMsg endpoints, and post-probe work. `struct cdx_mcdi_cmd` tracks refcount, lists, work, state, buffers, sequence, timing, completion cookie/callback, handle, command number, return code, and output. `struct cdx_mcdi_iface` stores locks, command lists, workqueue, waitqueue, doorbell/sequence owners, previous handle/seq, mode, and epoch. APIs include `cdx_mcdi_init()`, `cdx_mcdi_finish()`, `cdx_mcdi_process_cmd()`, and `cdx_mcdi_rpc()`. Macros declare buffers and access dword fields.

**Control flow, state, persistence:** RPCs allocate/queue commands, serialize through `iface_lock`, submit through `mcdi_request`, wait for RPMsg/event completion, retry on MC resource rejection, and complete callbacks/waiters. State is transient protocol/queue state.

**Dependencies/integration:** Depends on mutexes, krefs, RPMsg, remoteproc, workqueues, waitqueues, CDX bitfield helpers, and generated `MC_CMD_*` field constants.

**Risks and test signals:** Risks include sequence/doorbell ownership races, timeout handling, reboot epoch recovery, cancelled-command cleanup, and buffer alignment assumptions. Test signals include firmware RPC success/failure, timeout/retry injection, RPMsg disconnect, command cancellation, and lockdep/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cdx/mcdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/auth.h -->
## sources/distributed-fs/ceph-client/include/linux/ceph/auth.h

**Purpose:** This header defines the Ceph client authentication abstraction used to negotiate with monitors and create service authorizers for MDS/OSD/other peers.

**Important APIs/types/functions:** `struct ceph_authorizer` has a destroy hook. `struct ceph_auth_handshake` stores an authorizer, request/reply buffers, and optional message signing/checking callbacks. `struct ceph_auth_client_ops` is the protocol vtable for authentication status, request/reply exchange, authorizer creation/update/challenge/verification/invalidation, reset, destroy, and message signing. `struct ceph_auth_client` stores selected protocol, private implementation state, ops, negotiation flag, entity name, global ID, key, wanted keys, preferred/fallback connection modes, and mutex. Public APIs initialize/destroy/reset, build hello/auth messages, handle monitor replies, manage authorizers, process service replies, handle bad methods/authorizers, and sign/check messages.

**Control flow, state, persistence:** Authentication proceeds through monitor hello/request/reply loops; `handle_reply()` may request another round with `-EAGAIN`. Service connection setup obtains/upgrades authorizers and verifies server replies. Auth state persists in `ceph_auth_client` and protocol-private tickets/keys until reset/destroy.

**Dependencies/integration:** Depends on Ceph types, buffers, crypto keys, messages, and connection modes. Integrated by Ceph monitor/client connection code.

**Risks and test signals:** Risks include mutex violations, stale tickets, global ID changes, authorizer buffer lifetime errors, missing signature checks, and bad fallback mode handling. Test signals include Ceph auth integration tests, monitor reconnect/reauth, service challenge/reply flows, message signing verification, bad-method negotiation, and key rotation/expiry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/buffer.h -->
## sources/distributed-fs/ceph-client/include/linux/ceph/buffer.h

**Purpose:** This header defines a simple reference-counted Ceph buffer wrapper used for encoded protocol data.

**Important APIs/types/functions:** `struct ceph_buffer` stores a `kref`, `struct kvec` containing pointer/length, and allocation length. APIs include `ceph_buffer_new()`, `ceph_buffer_release()`, `ceph_buffer_get()`, `ceph_buffer_put()`, and `ceph_decode_buffer()`.

**Control flow, state, persistence:** Buffers are allocated with kmalloc for smaller sizes and vmalloc for larger sizes by implementation code. `ceph_buffer_get()` increments refs; `ceph_buffer_put()` releases when the last ref drops. `ceph_decode_buffer()` consumes encoded input pointers and returns a referenced buffer.

**Dependencies/integration:** Depends on krefs, MM/vmalloc, UIO kvecs, and Ceph encoding code. Used by Ceph auth, mon/osd/mds messages, and protocol decode paths.

**Risks and test signals:** Risks include ref leaks, use-after-free, allocating untrusted lengths, decode pointer overruns, and mixing kmalloc/vmalloc free paths. Test signals include Ceph protocol decode tests, fault injection for large allocations, KASAN/refcount debugging, and malformed buffer decode cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_debug.h -->
## sources/distributed-fs/ceph-client/include/linux/ceph/ceph_debug.h

**Purpose:** This header defines Ceph-specific debug and client-context logging macros.

**Important APIs/types/functions:** It sets `pr_fmt` to prefix messages with `KBUILD_MODNAME`. `dout()` and `doutc()` expand differently depending on `CONFIG_CEPH_LIB_PRETTYDEBUG`, `DEBUG`, and dynamic debug: pretty mode adds filename/line and optional client FSID/global ID, otherwise it wraps `pr_debug`. Client-context macros include notice/info/warn/warn_once/err and ratelimited warn/err variants with `[fsid global_id]` prefixes.

**Control flow, state, persistence:** Logging calls evaluate through printk/dynamic-debug paths. In non-debug builds, some forms become `no_printk` to preserve format checking without emitting output. No persistent state is stored here.

**Dependencies/integration:** Depends on string basename helpers and Ceph client objects exposing `fsid` and `monc.auth->global_id`. Integrated across Ceph lib and filesystem/client code.

**Risks and test signals:** Risks include using `doutc()` before auth/client pointers are initialized, logging sensitive values, format-string mismatches hidden by config combinations, and excessive debug overhead in pretty mode. Test signals include dynamic-debug toggles, compile coverage with/without pretty debug, null/early-client path review, and ratelimited log behavior under repeated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_debug.h -->
