# Group Research: group_549_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_i_309d80083c07

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/instance.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/instance.c

## Role

`instance.c` implements illumos device instance-number assignment. It maintains the in-kernel representation of persistent `/etc/path_to_inst` mappings from device tree paths and driver binding names to stable instance numbers.

## Main Behavior

The core state is `e_ddi_inst_state`, containing an instance tree rooted at `ins_root`, a list of driver entries without known majors, a dirty flag, and a reentrant global serialization lock.

`e_ddi_instance_init()` initializes the tree, optionally calls platform I/O alias setup, reads `INSTANCE_FILE` or its backup, and falls back to rebuild/preassignment when the file is missing, empty, or marked with the bootstrap magic string. Rebuilds force reconfiguration boot behavior so `/dev` and `path_to_inst` are regenerated together.

Instance tree nodes are `in_node_t` path components with unit addresses. Driver bindings are `in_drv_t` entries attached to nodes. Driver entries move through provisional, permanent, and borrowed states around `e_ddi_assign_instance()`, `e_ddi_keep_instance()`, and `e_ddi_free_instance()`.

## Instance Assignment

`e_ddi_assign_instance()` first allows platform override, then bypasses the persistent tree for pseudo devices. For normal devices it walks or creates the path node, handles aliases through `e_ddi_borrow_instance()`, allocates a driver entry when needed, assigns an instance using either preassigned `devi_instance` or `in_next_instance()`, and hashes the result onto the corresponding `devnames` major list.

`in_assign_instance_block()` supports driver.conf-controlled contiguous instance blocks for multi-port NICs and similar devices. It reads `ddi-instance-blocks`, matches the current device path against configured suffixes, allocates a contiguous block with `in_next_instance_block()`, and inserts persistent mappings for all paths in the block, including devices not currently present.

`in_next_instance_block()` depends on sorted `dn_inlist` entries. It can allocate quickly from `dn_instance`, or search for holes while respecting the preassigned boundary `dn_pinstance`.

## Persistence And Walking

`in_pathin()` parses entries from `path_to_inst`, normalizes binding names, rejects duplicate path/driver mappings and duplicate instance numbers, and creates permanent tree entries.

`e_ddi_walk_instances()` walks permanent mappings and reconstructs full paths with `in_walk_instances()`. `e_ddi_instance_majorinstance_to_path()` performs the reverse lookup from major and instance to a path.

Dirty state is tracked with `ins_dirty`; changes post a devfs sysevent through `i_log_devfs_instance_mod()` so userland can synchronize instance data.

## Locking And Invariants

All instance-tree mutation is serialized by `e_ddi_enter_instance()` / `e_ddi_exit_instance()`, which support recursive entry by the owning thread. Many helpers assert `ins_busy`.

Important invariants:
- Parents are instantiated before children and destroyed after them.
- Driver entries are removed before their owning nodes.
- `dev_info_t` and `in_node_t` back-pointers must agree while linked.
- `dn_inlist` is sorted by instance number.
- Newly introduced holes force `dn_instance = IN_SEARCHME`.

## Dependencies

This file depends on DDI device tree state, `devnamesp`, driver major lookup, binding-name aliasing, platform instance overrides, sysevents, boot flags, and cluster upgrade compatibility.

## Research Notes

This is a persistence and boot-enumeration file rather than a filesystem file, but it directly affects stable `/dev` naming. Audit-sensitive areas are alias borrow/return behavior, contiguous block assignment, preassigned instance boundary handling, duplicate suppression during `path_to_inst` parsing, and dirty/sysevent synchronization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/instance.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ip_cksum.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ip_cksum.c

## Role

`ip_cksum.c` provides high-use network checksum helpers for illumos IP-family code: one’s-complement IP checksums over STREAMS mblk chains, SCTP CRC32 checksums, IPv4 header checksums, and IPv6 extension-header length parsing.

## IP Checksum

`ip_cksum()` computes a partial one’s-complement checksum over an `mblk_t` chain. It accepts an initial sum and intentionally does not complement the result, allowing callers to combine partial checksum state.

The function has a fast path for a single aligned mblk and a slow path for chained, odd-length, or odd-address data. The slow path preserves byte ordering across mblk boundaries and handles words split between adjacent buffers.

It also understands `STRUIO_IP` mblks where some data may already have been checksummed. It validates that the requested offset and data pointers still match the precalculated checksum range; otherwise it clears `STRUIO_IP` and falls back to normal checksum calculation.

## Other Helpers

`sctp_cksum()` computes SCTP CRC32 over an mblk chain using `sctp_crc32()`, starting with `0xffffffff` and complementing the final result.

`ip_csum_hdr()` computes and returns the IPv4 header checksum for an `ipha_t`, including optional IPv4 header words. A computed `0xffff` checksum is normalized to zero.

`ip_hdr_length_nexthdr_v6()` walks an IPv6 header and known extension headers contained in the same mblk. It returns the total network header length and optionally a pointer to the next-header field that names the transport header.

## Invariants And Assumptions

- Non-`STRUIO_IP` fast-path data is expected to be 16-bit aligned.
- IPv6 extension-header parsing assumes all IPv6 headers/extensions are in the same mblk.
- Odd-length and odd-address handling depends on endian-specific byte placement.
- `STRUIO_IP` cached checksum state is trusted only when the current mblk spans the expected checksum interval.

## Research Notes

The risk in this file is almost entirely boundary and alignment correctness. Hotspots are split-word handling across `b_cont`, STRUIO partial-checksum invalidation, IPv6 malformed-extension detection, and endian-specific odd-byte accumulation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ip_cksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ipc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ipc.c

## Role

`ipc.c` is the shared System V IPC namespace implementation used by message queues, semaphore arrays, and shared memory segments. It provides common object IDs, key lookup, permission handling, resource-control checks, reference management, removal, enumeration, and zone cleanup.

## Data Model

Each IPC object embeds `kipc_perm_t` as its first member. Objects have owner/creator uid/gid, mode bits, key, project, zone, refcount, list membership, AVL key membership, and an allocated ID.

`ipc_service_t` represents one facility namespace. It owns:
- A power-of-two ID table of `ipc_slot_t`.
- Per-slot sequence numbers and locks.
- An `id_space` allocator.
- An AVL tree for keyed lookup.
- A list of all visible objects.
- Project and zone resource-control handles.
- Facility destructor and RMID callbacks.

IDs combine table index and sequence number, reducing stale-ID reuse hazards.

## Locking Model

The file documents and implements this lock order:

`namespace lock -> slot locks in table order -> p_lock`

ID lookup avoids taking the namespace lock by reading the current table size, taking the computed slot lock, then verifying the table size did not change. Table growth allocates a new table, locks old and corresponding new slots, copies entries, chains the old table from the new one, publishes the new pointer and size, and intentionally keeps old tables reachable because threads may still touch old embedded locks.

## Interfaces

`ipcperm_access()` performs mode, owner/group, supplementary group, zone, and privilege checks. `ipcperm_set/stat` and `ipcperm_set64/stat64` implement common IPC_SET/STAT behavior and auditing.

`ipcs_create()` initializes a namespace; `ipcs_destroy()` tears it down when empty.

`ipc_lookup()` returns a held ID lock for a valid, zone-visible object. `ipc_hold()`, `ipc_rele()`, and `ipc_rele_locked()` manage object references and call the facility destructor when the last removed object reference drops.

`ipc_get()` implements the first phase of GET: keyed lookup or allocation of an invisible object. `ipc_commit_begin()` revalidates key/resource races and prepares project/zone references. `ipc_commit_end()` publishes the object into the table, AVL tree, and used list. `ipc_cleanup()` unwinds failed allocations.

`ipc_rmid()` removes an object after permission checks, calls facility RMID cleanup, and releases the namespace reference. `ipc_ids()` enumerates visible IDs with zone filtering. `ipc_remove_zone()` removes all objects belonging to a zone without holding the service lock across destructors.

## Resource And Zone Handling

Allocation checks both project and zone resource controls before growing or consuming an ID. Object publication increments project and zone usage counters; removal decrements them. Key lookup is keyed by both IPC key and zone ID, so identical keys can exist independently in different zones.

## Research Notes

This file is concurrency-heavy infrastructure. Audit-sensitive areas are lock ordering during table growth, stale-table lock validation, `ipc_get()`/`ipc_commit_begin()` races, resource-control accounting rollback, zone visibility rules, and deferred destruction after RMID.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/iscsiboot_prop.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/iscsiboot_prop.c

## Role

`iscsiboot_prop.c` contains common helpers for iSCSI boot properties: optional diagnostic printing, freeing boot-property subfields, IP address formatting, and construction of iSCSI boot paths.

## Boot Property Printing

`iscsi_print_boot_property()` prints the global `iscsiboot_prop` when `iscsi_print_bootprop` is enabled. It delegates to initiator, NIC, and target printers.

The printed data includes initiator name, initiator CHAP name, local IP/gateway/DHCP/MAC, target name/IP/port/LUN, and target CHAP name. CHAP secrets are freed by the cleanup routines but not printed here.

`kinet_ntoa()` formats IPv4 as dotted decimal and IPv6 as colon-separated 16-bit hex groups without compression.

## Memory Cleanup

`iscsi_boot_free_ini()` frees initiator name, CHAP name, and CHAP secret buffers and clears pointers/lengths.

`iscsi_boot_free_tgt()` frees target name, CHAP name, CHAP secret, and boot parameter buffers and clears pointers/lengths.

`iscsi_boot_prop_free()` nulls the global pointer and frees nested initiator and target allocations from the saved structure.

## Boot Path Construction

`get_iscsi_bootpath_vhci()` builds a `/iscsi/ssd@...` boot path from target name, TPGT, LUN, and boot parameters. It lazily calls `ld_ib_prop()` when global boot properties are absent.

`get_iscsi_bootpath_phy()` builds a `/iscsi/disk@...` boot path, first passing the target name through `replace_sp_c()`.

`replace_sp_c()` percent-encodes special characters in target names: `:`, space, `@`, and `/`.

## Research Notes

This file is small but sits on the early-boot storage path. Hotspots are fixed-size path buffers, unchecked assumptions about target-name length during escaping, endian interpretation of the boot LUN bytes, and ensuring boot-property ownership is consistent with the partial free behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/iscsiboot_prop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kcpc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kcpc.c

## Role

`kcpc.c` implements the kernel CPU performance counter framework. It binds performance counter request sets to LWPs or CPUs, configures platform counter backends, handles context switching, overflow interrupts, DTrace CPC integration, CPU capacity/utilization interposition, and request multiplexing.

## Backend And Initialization

`kcpc_init()` initializes global locks once and loads the platform PCBE module through `kcpc_hw_load_pcbe()`. `kcpc_register_pcbe()` installs the backend operations and counter count. PCBE callbacks perform event coverage, configuration, programming, sampling, stopping, freeing, and event/attribute listing.

`kcpc_pcbe_tryload()` loads qualified PCBE modules by platform-specific ID components.

## Binding And Configuration

`kcpc_bind_thread()` creates a frozen context for an LWP, assigns requests to hardware counters, configures PCBE request state, installs context ops, and programs the hardware if binding the current thread. It supports `CPC_BIND_LWP_INHERIT`.

`kcpc_bind_cpu()` creates a CPU-bound context, requires the current thread to be bound to the requested CPU, rejects conflicting non-CU CPC use, and programs the target CPU while holding CPU and CPC context locks.

`kcpc_assign_reqs()` and `kcpc_tryassign()` place requests onto counters, preserving explicit assignments and trying different starting requests to avoid simple ordering failures.

`kcpc_configure_reqs()` calls `pcbe_configure()` for each request, sets overflow-notification state, links request data storage, and maps PCBE errors to kernel errno values.

## Sampling, Enablement, And Teardown

`kcpc_sample()` validates the set, samples current hardware when appropriate, updates hrtime and virtual tick accounting, and copies counter data, time, and tick values to user buffers.

`kcpc_enable()` supports enable/disable and user/system counting flag changes. For user/system mode toggles it stops, snapshots presets, duplicates the set, unbinds, edits flags, and rebinds.

`kcpc_unbind()`, `kcpc_passivate()`, and `kcpc_free()` invalidate contexts, stop hardware when needed, remove context ops, clear thread state, free PCBE configs, release set data, and coordinate with concurrent `kcpc_restore()` using `KCPC_CTX_RESTORE`.

## Context Switching And Overflow

`kcpc_save()` stops counters on switch-out, samples active thread-bound contexts, and may restore CU counter use. `kcpc_restore()` avoids invalid/frozen contexts, marks restore-in-progress, and programs the hardware at high PIL with preemption disabled.

`kcpc_hw_overflow_intr()` handles hardware overflow interrupts. If DTrace CPC is active, it coordinates per-CPU interrupt state, fires DTrace, resets overflowed counters, and reprograms. Otherwise it calls `kcpc_overflow_intr()` to either post an AST for LWP-bound overflow handling or synchronously sample/restart a CPU-bound context.

`kcpc_overflow_ast()` samples after an overflow, detects PICs marked for `CPC_OVF_NOTIFY_EMT`, preserves freeze state for signal delivery, or restarts counters.

## CPU And CU Integration

`kcpc_program()` and `kcpc_unprogram()` are high-PIL routines used locally or via cross-call. They interpose with capacity/utilization CPC use through `cu_cpc_unprogram()` and `cu_cpc_program()`.

`kcpc_cpu_ctx_create()` creates one or more CPU contexts from a request list, splitting or degrading to one request per set when counters cannot cover all events simultaneously.

`kcpc_cpu_stop()` and `kcpc_cpu_program()` use `cpu_call()` wrappers to stop or program counters on remote CPUs.

## Research Notes

This file has substantial concurrency and interrupt-context risk. Important invariants include preemption disabled while programming/sampling hardware, high-PIL synchronization with cross-calls, `cpu_lock` while dereferencing CPU structures, set binding completion signaled by `KCPC_SET_BOUND`, and atomic flag updates. Audit hotspots are overflow skid handling, invalidation races, PCBE config lifetime, CPU DR/offline paths, inherited LWP contexts, and CU interposition.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kcpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kdi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kdi.c

## Role

`kdi.c` is a small kernel debugger interface glue file. It forwards kernel lifecycle notifications to the active debugger vector and arbitrates DTrace versus KMDB breakpoint ownership.

## Debug Vector Forwarding

The global `kdi_dvec` contains debugger callbacks. This file forwards:
- VM-ready and memory-available notifications.
- Module-available and thread-available notifications.
- Module loaded/unloading notifications.
- x86 fault handling.
- SPARC CPU initialization and CPR restart hooks.

Some calls first invoke `dv_kctl_*` control callbacks, then the debugger-facing callback.

## DTrace/KMDB State

`kdi_dtrace_state` tracks one of idle, DTrace active, or KMDB breakpoint active.

`kdi_dtrace_set()` performs atomic compare-and-swap transitions for:
- DTrace activate/deactivate.
- KMDB breakpoint activate/deactivate.

It rejects conflicting ownership with `EBUSY`, treats idempotent transitions as success, and rejects invalid transition values with `EINVAL`.

## Research Notes

The file is simple but gates debugger/tracing coexistence. The main invariant is that DTrace and KMDB breakpoint activity cannot be active at the same time. The CAS loop avoids locking and makes the transition state safe under concurrent callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kiconv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kiconv.c

## Role

`kiconv.c` implements committed kernel iconv interfaces: `kiconv_open(9F)`, `kiconv(9F)`, `kiconv_close(9F)`, and `kiconvstr(9F)`. It provides embedded UTF-8 conversions for common single-byte encodings and dynamically loads regional conversion modules for broader codepage support.

## Embedded Conversions

Embedded conversions cover UTF-8 to and from:
- CP1252
- ISO-8859-1
- ISO-8859-15
- CP850

UTF-8 to single-byte conversions use state objects with a mapping-table ID and BOM-processing flag. They validate UTF-8 using `u8_number_of_bytes`, `u8_valid_min_2nd_byte`, and `u8_valid_max_2nd_byte`, binary-search mapping tables, copy ASCII directly, and use `?` for non-identical conversions.

Single-byte to UTF-8 conversions use table lookup for bytes above `0x7f`, copy ASCII directly, and reject unmapped code points unless string-mode replacement is requested.

## String Conversion

`kiconvstr_to_sb()` and `kiconvstr_fr_sb()` provide one-shot conversions with flags:
- `KICONV_IGNORE_NULL` controls whether NUL terminates processing.
- `KICONV_REPLACE_INVALID` converts invalid input to replacement characters instead of failing.

UTF-8 replacement uses `U+FFFD`; single-byte replacement uses the ASCII replacement character.

## Code Names And Modules

`normalize_codename()` removes skippable characters, folds ASCII uppercase to lowercase, and maps aliases through `code_list`.

`conv_list` contains embedded conversions plus module-backed conversions for Japanese, Simplified Chinese, Korean, Traditional Chinese, and EMEA encodings. Module rows start with function pointers set to `NULL`.

`check_and_load_conversions()` normalizes names, locates the conversion row, loads the corresponding `kiconv` module with `modload()` if needed, increments the module function-use refcount, and returns a descriptor.

`kiconv_register_module()` fills conversion function pointers during module install. `kiconv_unregister_module()` clears them only when the module refcount is zero.

## Public Interface

`kiconv_open()` opens a conversion and rolls back the module refcount if the module’s open routine fails.

`kiconv()` dispatches through the selected conversion function.

`kiconv_close()` calls the conversion close routine, frees the descriptor, and decrements the module refcount.

`kiconvstr()` loads/refs a conversion, calls the string converter, frees the temporary descriptor, and decrements the module refcount.

## Research Notes

The main correctness surface is buffer accounting and UTF-8 validation. Audit hotspots are binary-search assumptions about sorted mapping tables, descriptor ID bounds, module refcount lifetime, `modload()` races, invalid-input replacement paths, and ensuring every output path updates remaining input/output lengths consistently.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kiconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/klpd.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/klpd.c

## Role

`klpd.c` implements kernel support for privilege-policy daemon upcalls. It lets userland door servers answer privilege policy questions for credentials, projects, zones, and `pfexec`.

## Registration Model

A `klpd_reg_t` stores a door handle, target pid, allowed privilege set, optional credential, disabled flag, reference count, and linked-list pointers.

Registrations can be:
- Credential-specific through `credklpd_t`.
- Project-specific through `kpj_klpd`.
- Global through `klpd_list`.
- Zone `pfexecd` specific through `zone_pfexecd`.

List nodes are refcounted and unlinked lazily so walkers can safely continue.

## KLPD Calls

`klpd_marshall()` builds a door-call payload containing the requested privilege set and optional argument data. Supported argument types include none, vnode path, integer, and protocol/port variants.

For vnode arguments it resolves a path relative to the registering credential’s zone root and optionally appends a caller-supplied component.

`klpd_call()` refuses to upcall while sensitive locks such as `pidlock`, `p_lock`, or `p_crlock` are held. It also enforces that the requested privilege set is within the caller’s limit set. It tries credential-specific registration first, then project registration, then global registrations visible to the caller’s zone.

`klpd_do_call()` prevents self-calls to the door server, retries `EAGAIN`, unregisters bad global doors on `EINVAL`/`EBADF`, validates the reply buffer, and treats malformed replies as denial.

## Register And Unregister

`klpd_reg()` validates the caller’s requested privilege set against its effective/outer effective privileges, validates the door, prevents same-process pid registrations from calling themselves, and registers by pid, project, or global scope.

For current-process pid registration it creates a new credential copy with a `credklpd_t` pointer. For another pid it requires an existing credential KLPD object and updates it in place.

`klpd_unreg()` removes project, pid, current-process, or global registrations depending on the supplied id type and id.

`crklpd_hold()`, `crklpd_rele()`, `crklpd_alloc()`, and `crklpd_setreg()` manage credential-attached registration state.

## Pfexec Support

`pfexec_reg()` and `pfexec_unreg()` manage a per-zone `pfexecd` door registration after privilege checks.

`pfexec_call()` asks `pfexecd` for execution attributes for a resolved path. A successful reply can allow execution unchanged or return a modified credential with uid/gid changes, inherited privileges, limit privileges, and scrub-environment requirements. Returned privilege sets must remain within the current limit set.

`get_forced_privs()` asks `pfexecd` for forced privileges for a path, intersects them with the zone kernel credential’s limit set, and rejects privileges outside the caller’s limit set.

`check_user_privs()` asks `pfexecd` whether a user is authorized for a requested privilege set.

## Research Notes

This file is a high-value security boundary. Important audit areas are door upcall error handling, avoiding userland callbacks with kernel locks held, refcount/list unlink rules, zone visibility, path construction and bounds, reply size/alignment validation, credential mutation from `pfexecd` replies, and strict enforcement that granted privileges never exceed limit privileges.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/klpd.c -->