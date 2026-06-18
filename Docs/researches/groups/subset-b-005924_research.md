# subset-b-005924 research

Grouped research for Linux headers under `sources/distributed-fs/ceph-client/include/linux`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm.h -->
# sources/distributed-fs/ceph-client/include/linux/tpm.h

## Purpose
Defines the kernel TPM core interface: TPM 1.2/2.0 constants, command and response metadata, chip state, low-level bus operation callbacks, TPM command-buffer helpers, PCR/random APIs, and optional TPM2 HMAC session support. It is a central integration header for TPM device drivers, trusted keys, RNG, ACPI PPI, event logs, and callers that transmit TPM2 commands.

## Important APIs, Types, And Functions
Key types are `struct tpm_chip`, `struct tpm_class_ops`, `struct tpm_buf`, `struct tpm_digest`, `struct tpm_bank_info`, `struct tpm_space`, and `struct tpm_header`. `struct tpm_class_ops` is the bus-driver vtable for `send`, `recv`, `status`, `cancel`, locality, clock, timeout, and idle/ready transitions. `struct tpm_chip` owns device/cdev state, ops lifetime locking, event log seqops, RNG registration, timeout/duration tables, PCR banks, ACPI PPI data, TPM space buffers, command attributes, active locality, and optional HMAC auth session state.

Public APIs include `tpm_try_get_ops()`, `tpm_put_ops()`, `tpm_transmit_cmd()`, `tpm_pcr_read()`, `tpm_pcr_extend()`, `tpm_get_random()`, `tpm_default_chip()`, `tpm2_flush_context()`, `tpm2_find_hash_alg()`, and TPM buffer helpers such as `tpm_buf_init()`, `tpm_buf_append_u32()`, `tpm_buf_read_u16()`, `tpm_buf_append_handle()`, `tpm_buf_append_auth()`, and HMAC response validation helpers.

## Control Flow
Callers construct a `tpm_buf` with a tag and ordinal, append handles/auth/payload, then pass it to `tpm_transmit_cmd()`. The core uses `tpm_chip.ops` under `ops_sem` and `tpm_mutex` to serialize and dispatch to the transport. Return codes are normalized by helpers such as `tpm2_rc_value()` and `tpm_ret_to_err()`. Auth-session builds are conditional: when TPM2 HMAC is configured, session start/fill/check/end functions participate in request/response flow; otherwise inline stubs preserve source compatibility.

## State, Persistence, And Dependencies
Persistent kernel state is per `tpm_chip`: cdev lifetime, locality, timeout tuning, PCR bank information, event log pointers, allocated command attributes, work-space context buffers, and optional TPM2 HMAC seed/context data. Dependencies include `hw_random`, `acpi`, `cdev`, `fs`, `highmem`, `crypto/hash_info`, and AES definitions. Compile-time dependency gates provide no-op or `-ENODEV` fallbacks when TPM support is not built.

## Integration Points
Integrates with `/dev/tpm*`, sysfs groups, ACPI PPI, BIOS/EFI event logs, hwrng, TPM2 trusted-key/auth paths, and bus drivers implementing `tpm_class_ops`. `tpm_is_firmware_upgrade()` and chip flags expose state to drivers that must restrict normal command paths during firmware update mode.

## Risks And Test Signals
Risks include command-buffer overflow/boundary flags being ignored, mismatched TPM2 handle/name/auth encoding, stale ops after driver unregister, locality leaks, timeout calibration errors, and conditional stubs hiding missing TPM support. Test signals are TPM command self-tests, PCR read/extend coverage across hash banks, random read behavior, firmware-upgrade mode checks, HMAC-session positive/negative tests, suspend/resume locality handling, and compile coverage with TPM, ACPI, and HMAC configs both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_command.h -->
# sources/distributed-fs/ceph-client/include/linux/tpm_command.h

## Purpose
Provides small TPM 1.2 command constants used by legacy trusted-key and command-building paths: request/response tags, selected ordinals, the storage-root-key handle, and nonce size.

## Important APIs, Types, And Functions
There are no functions or structs. Exports are preprocessor constants: `TPM_TAG_RQU_COMMAND`, `TPM_TAG_RQU_AUTH1_COMMAND`, `TPM_TAG_RQU_AUTH2_COMMAND`, response tag equivalents, ordinals such as `TPM_ORD_GETRANDOM`, `TPM_ORD_OSAP`, `TPM_ORD_OIAP`, `TPM_ORD_SEAL`, `TPM_ORD_UNSEAL`, `SRKHANDLE`, and `TPM_NONCE_SIZE`.

## Control Flow
The header has no runtime control flow. Consumers use these constants while serializing TPM 1.2 command packets and interpreting command classes.

## State, Persistence, And Dependencies
No state is held. It has no include dependencies beyond its guard and is strictly compile-time metadata.

## Integration Points
Integrates with TPM 1.2 command construction, especially sealed/unsealed data flows and OSAP/OIAP authorization sessions. It complements the broader `tpm.h` TPM2 definitions.

## Risks And Test Signals
Risks are wrong wire values causing TPM command rejection or authentication mismatch. Test signals are legacy TPM command vectors, build coverage for trusted-key paths that still include this header, and checking serialized packets against TCG constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_eventlog.h -->
# sources/distributed-fs/ceph-client/include/linux/tpm_eventlog.h

## Purpose
Defines TPM BIOS/EFI event log record layouts and helper logic for calculating TPM2 event sizes. It gives parsers the packed structures and validation needed to walk variable-length TCG event logs containing multiple digest algorithms.

## Important APIs, Types, And Functions
Important definitions include `struct tcpa_event`, `struct tcpa_pc_event`, `struct tcg_efi_specid_event_head`, `struct tcg_pcr_event`, `struct tcg_event_field`, `struct tcg_pcr_event2_head`, `struct tcg_algorithm_size`, and `struct tcg_algorithm_info`. Enums define BIOS platform classes, TPM 1.2 event types, and PC event IDs. The key function is `__calc_tpm2_event_size()`, which validates a TPM2 event against the initial Spec ID event and returns the computed byte length or zero on malformed input.

## Control Flow
`__calc_tpm2_event_size()` starts at a TPM2 event header, optionally maps only the bytes it needs through `TPM_MEMREMAP`, validates that `event_header` is PCR 0, `NO_ACTION`, and has a zero SHA1 digest, then checks the Spec ID signature and algorithm count. It walks each digest by reading its algorithm ID, matching it to the digest-size table from the Spec ID event, skips the digest bytes, then reads the event data length and computes total size. Unknown algorithms, mapping failure, mismatched counts, or empty event type/data return zero.

## State, Persistence, And Dependencies
The header stores no persistent state. It depends on `linux/tpm.h`, endian conversion on PPC64, and arch/platform-provided `TPM_MEMREMAP`/`TPM_MEMUNMAP` hooks when parsing physical log memory. Structures are packed where wire layout requires it.

## Integration Points
Used by TPM event-log readers under firmware/ACPI/EFI paths and seq_file exports for binary or ASCII event logs. It must agree with PCR bank metadata from TPM2 capabilities and TCG EFI Spec ID event layout.

## Risks And Test Signals
Risks include parsing attacker-controlled or firmware-corrupt logs, incorrect pointer arithmetic across pages, endianness mismatches, trusting unbounded algorithm counts, and accepting unknown digest algorithms. Test signals include malformed-log fuzzing, cross-page mapping tests, PPC64 endian coverage, Spec ID signature/count validation, and regression logs from TPM 1.2 and TPM2 firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_eventlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_svsm.h -->
# sources/distributed-fs/ceph-client/include/linux/tpm_svsm.h

## Purpose
Defines request and response helpers for AMD SVSM vTPM commands in SEV-SNP guests. It maps the SVSM vTPM command structure to the TCG TPM simulator protocol used for `TPM_SEND_COMMAND`.

## Important APIs, Types, And Functions
Exports `SVSM_VTPM_MAX_BUFFER`, `struct svsm_vtpm_request`, `struct svsm_vtpm_response`, `struct svsm_vtpm_cmd_request`, and `struct svsm_vtpm_cmd_response`. Inline helpers are `svsm_vtpm_cmd_request_fill()` and `svsm_vtpm_cmd_response_parse()`.

## Control Flow
`svsm_vtpm_cmd_request_fill()` verifies the TPM command payload fits within the fixed 4096-byte maximum minus request header, writes platform command `8`, locality, payload size, and copies the TPM command bytes. `svsm_vtpm_cmd_response_parse()` validates the caller output buffer is large enough, rejects oversized platform response lengths, copies the response bytes, and returns the response size.

## State, Persistence, And Dependencies
No persistent state is stored. The packed request layout is wire/ABI state shared with SVSM firmware. Dependencies are `errno`, `string`, and base integer types.

## Integration Points
Used by an SVSM-backed TPM transport driver as the adapter between Linux TPM core `send`/`recv` semantics and the SVSM call interface. It integrates with confidential-computing guest firmware rather than physical TPM buses.

## Risks And Test Signals
Risks include buffer-size mismatch with simulator protocol, untrusted platform response sizes, nonzero locality support assumptions, and layout padding mistakes. Test signals are request-size boundary tests at 4096 bytes, malformed response-size tests, packed layout assertions, and end-to-end TPM2 commands through an SVSM vTPM instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tpm_svsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace.h -->
# sources/distributed-fs/ceph-client/include/linux/trace.h

## Purpose
Declares high-level tracing interfaces for exporting ftrace output, writing to trace arrays, creating/destroying trace instances, and controlling osnoise hooks.

## Important APIs, Types, And Functions
`struct trace_export` links export targets and provides a `write()` callback for trace data. Public APIs under `CONFIG_TRACING` include `register_ftrace_export()`, `unregister_ftrace_export()`, `trace_array_puts()`, `trace_array_printk()`, `trace_array_init_printk()`, `trace_array_get_by_name()`, `trace_array_destroy()`, and osnoise registration/IRQ entry/exit hooks.

## Control Flow
When tracing is enabled, producers write constant strings or formatted data into a `trace_array`; export targets can be registered so committed trace records are delivered beyond the ring buffer. When tracing is disabled, inline stubs return neutral failures or no-ops, allowing callers to compile without runtime tracing.

## State, Persistence, And Dependencies
The header defines only interfaces. Runtime state lives in `trace_array`, registered export lists, and trace buffers managed by tracing core. It depends on `BIT()` being available to consumers and forward-declares `struct trace_array`.

## Integration Points
Integrates ftrace, trace instances, trace_printk initialization, and osnoise tracer architecture hooks. Export flags distinguish functions, events, and markers.

## Risks And Test Signals
Risks include export callbacks running in sensitive contexts, stale export registration, trace-array lifetime mistakes, and config-disabled stubs masking missing tracing behavior. Test signals include registration/unregistration races, writing into named trace arrays, disabled-config builds, and osnoise tracer entry/exit accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_clock.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_clock.h

## Purpose
Declares trace clock functions used by tracing infrastructure to timestamp events with different precision/scalability tradeoffs.

## Important APIs, Types, And Functions
Exports `trace_clock_local()`, `trace_clock()`, `trace_clock_jiffies()`, `trace_clock_global()`, and `trace_clock_counter()`, all returning `u64` and marked `notrace`.

## Control Flow
The header has no implementation. Runtime callers choose local, medium/default, jiffies, global monotonic, or counter clocks depending on ordering and overhead needs.

## State, Persistence, And Dependencies
No state is defined here. It includes compiler/types and architecture-specific `asm/trace_clock.h`, which may provide arch-optimized definitions or backing state.

## Integration Points
Used by ftrace, trace events, ring-buffer timestamping, and tracing UI clock selection. The functions must be safe from tracing recursion because they are `notrace`.

## Risks And Test Signals
Risks are non-monotonic timestamps when the wrong clock is selected, recursion if traced, and architecture implementation drift. Test signals include per-CPU and global ordering checks, tracing recursion tests, and build coverage across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_events.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_events.h

## Purpose
Defines the core trace event metadata, record formatting APIs, ring-buffer reservation/commit interface, per-event file state, dynamic event command builders, trigger/filter flags, and optional perf/BPF integration hooks.

## Important APIs, Types, And Functions
Core types include `struct trace_entry`, `struct trace_iterator`, `struct trace_event_functions`, `struct trace_event`, `struct trace_event_class`, `struct trace_event_call`, `struct trace_event_file`, `struct trace_event_buffer`, `struct dynevent_cmd`, `struct synth_field_desc`, and `struct synth_event_trace_state`. APIs cover printing helpers (`trace_print_flags_seq()`, `trace_print_hex_seq()`), event registration (`register_trace_event()`, `trace_add_event_call()`), buffer reservation (`trace_event_buffer_reserve()`), commit (`trace_event_buffer_commit()`), filtering (`trace_define_field()`, `filter_match_preds()`), dynamic synth/kprobe event creation, event enable/disable, trigger execution, and perf/BPF probe attachment.

## Control Flow
An event call has a class, fields, print format, flags, and optional perf/BPF state. Runtime tracing reserves a buffer record, fills a `trace_entry`, applies filters/triggers/PID checks, commits to the ring buffer, and optionally submits to perf/BPF. Dynamic event builders accumulate a command in `seq_buf`, add fields, and call `dynevent_create()`. Disabled config paths provide `-EOPNOTSUPP` or neutral stubs for BPF/perf features.

## State, Persistence, And Dependencies
Persistent state lives in event-call lists, class field lists, per-event files, filters protected by RCU, eventfs inode links, trigger lists, atomic/refcount fields, perf arrays, and BPF program arrays. Dependencies include ring buffers, trace_seq, percpu data, hardirq state, perf events, and tracepoints.

## Integration Points
Integrates ftrace event definitions, tracefs event files, perf tracepoints, BPF raw tracepoints, dynamic synthetic/kprobe/uprobe events, hist triggers, and scheduler task-info recording.

## Risks And Test Signals
Risks include flag races, stale dynamic-event references, filter field mismatches, trigger recursion, BPF array lifetime under RCU, oversized perf trace records, and event format ABI drift. Test signals include event enable/disable races, dynamic event create/delete tests, filter parser and field offset tests, perf/BPF attach-detach coverage, tracefs format validation, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_printk.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_printk.h

## Purpose
Provides developer-facing ftrace printk helpers and tracing on/off controls. It lets kernel code write debug messages to trace buffers with optimized handling for constant format strings.

## Important APIs, Types, And Functions
Defines `enum ftrace_dump_mode`, control functions such as `tracing_on()`, `tracing_off()`, `tracing_is_on()`, `tracing_snapshot()`, `tracing_start()`, `tracing_stop()`, macros `trace_printk()`, `do_trace_printk()`, `trace_puts()`, `ftrace_vprintk()`, and backends `__trace_bprintk()`, `__trace_printk()`, `__trace_bputs()`, `__trace_puts()`, `__ftrace_vbprintk()`, `__ftrace_vprintk()`, `trace_dump_stack()`, and `ftrace_dump()`.

## Control Flow
`trace_printk()` stringifies variadic arguments to route no-argument constant strings to `trace_puts()` and formatted calls to `do_trace_printk()`. Constant format strings are placed in `__trace_printk_fmt` for binary printk decoding and use binary backends; dynamic formats use normal text formatting. Disabled tracing compiles to no-op stubs.

## State, Persistence, And Dependencies
State is primarily persistent format-string section entries, trace buffers initialized when trace_printk is used, and global tracing enable/snapshot state. Dependencies include compiler attributes, instruction pointer access, `stddef`, and stringify helpers.

## Integration Points
Integrates with ftrace buffers, printk format export, tracing control files, panic/oops dump modes, and ad hoc debugging in fast paths.

## Risks And Test Signals
Risks include leaving debug trace_printk calls in production paths, extra memory allocation for format buffers, dynamic format overhead, and unexpected no-op behavior when tracing is disabled. Test signals include format-section presence, binary format decoding, tracing_on/off behavior, snapshot allocation, and disabled-config compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_recursion.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_recursion.h

## Purpose
Implements per-task recursion guards for ftrace and internal trace event paths. It prevents tracing callbacks from recursively tracing themselves in normal, IRQ, softirq, NMI, and transition contexts.

## Important APIs, Types, And Functions
Defines recursion bit indexes, context constants, `trace_recursion_set()`, `trace_recursion_clear()`, `trace_recursion_test()`, `trace_get_context_bit()`, `trace_test_and_set_recursion()`, `trace_clear_recursion()`, `ftrace_test_recursion_trylock()`, and `ftrace_test_recursion_unlock()`. Optional helpers record recursion and validate RCU watching.

## Control Flow
`trace_test_and_set_recursion()` reads `current->trace_recursion`, optionally warns if RCU is not watching, computes the bit for the current interrupt context plus caller class, and returns `-1` if the same context is already tracing. It allows one transition case to avoid dropping events during interrupt-context accounting windows. On success it sets the bit, issues a barrier, disables preemption, and returns the bit to clear later.

## State, Persistence, And Dependencies
State is in `current->trace_recursion`, with only the current task modifying it. Dependencies include interrupt context level, scheduler current task, preemption controls, optional RCU validation, and optional recursion recording.

## Integration Points
Used by ftrace callbacks, internal tracing lists, branch tracing, function graph IRQ state, and event recursion protection.

## Risks And Test Signals
Risks include forgetting to unlock returned bits, tracing with RCU inactive, false recursion drops during context transitions, and invalid use when tracing config is disabled. Test signals include recursive ftrace callback tests, IRQ/NMI context tracing, preemption state assertions, and forced RCU-not-watching validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_recursion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_remote.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_remote.h

## Purpose
Defines the callback interface for registering a remote trace source with tracefs. A remote provider exposes trace buffers and event controls that tracefs can present like local tracing data.

## Important APIs, Types, And Functions
`struct trace_remote_callbacks` provides `init`, `load_trace_buffer`, `unload_trace_buffer`, `enable_tracing`, `swap_reader_page`, `reset`, and `enable_event`. Public APIs are `trace_remote_register()`, `trace_remote_alloc_buffer()`, and `trace_remote_free_buffer()`.

## Control Flow
A remote registers a name, callbacks, private data, and event table. Tracefs calls `init()` to extend its directory, lazily calls `load_trace_buffer()` before first buffer access, toggles writing through `enable_tracing()`, calls `swap_reader_page()` while consuming per-CPU pages, calls `reset()` on trace clear, and calls `enable_event()` for per-event toggles.

## State, Persistence, And Dependencies
Provider state is opaque through `priv`; buffer state is represented by `trace_buffer_desc`. The header depends on dcache, ring buffer, and remote-event definitions.

## Integration Points
Integrates tracefs with off-core or external tracing producers that can provide ring-buffer-compatible pages and event metadata.

## Risks And Test Signals
Risks include callback ordering mistakes, buffer lifetime errors between load/unload, stale event enable state, and per-CPU reader-page swap races. Test signals include remote registration/removal, tracefs open/close buffer lifecycle, event enable toggles, reset behavior, and multi-CPU buffer consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_remote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_remote_event.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_remote_event.h

## Purpose
Defines the metadata and format macros for remote trace events consumed through `trace_remote`.

## Important APIs, Types, And Functions
Exports `struct remote_event_hdr`, `struct remote_event`, `REMOTE_EVENT_NAME_MAX`, `RE_STRUCT`, `re_field`, and `REMOTE_EVENT_FORMAT()`. A remote event holds name, id, enabled state, parent remote pointer, field descriptors, print format, and a `print()` callback.

## Control Flow
The header has no runtime control flow. Providers define packed-ish event payload structs with `REMOTE_EVENT_FORMAT()`, attach field metadata and print functions, and tracefs uses those to expose and render remote records.

## State, Persistence, And Dependencies
Event state includes the enabled bit, metadata pointers, and format callback owned by the remote provider. Dependencies are forward declarations of tracing structures.

## Integration Points
Pairs with `trace_remote_register()` and tracefs event presentation. `struct remote_event_hdr.id` maps raw records back to metadata entries.

## Risks And Test Signals
Risks include id/name mismatches, format structs not matching remote ring-buffer payloads, dangling field or print-format pointers, and name truncation at 30 bytes. Test signals are event format dumps, raw-record print tests, enable/disable propagation, and payload-size/layout assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_remote_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_seq.h -->
# sources/distributed-fs/ceph-client/include/linux/trace_seq.h

## Purpose
Defines `struct trace_seq`, the fixed-size formatting buffer used by tracing print paths to build lines and binary-derived text safely.

## Important APIs, Types, And Functions
Exports `TRACE_SEQ_SIZE`, `TRACE_SEQ_BUFFER_SIZE`, `trace_seq_init()`, `trace_seq_used()`, `trace_seq_buffer_ptr()`, `trace_seq_has_overflowed()`, `trace_seq_pop()`, and tracing-enabled formatting/copy helpers such as `trace_seq_printf()`, `trace_seq_bprintf()`, `trace_print_seq()`, `trace_seq_to_user()`, `trace_seq_puts()`, `trace_seq_putmem_hex()`, `trace_seq_path()`, `trace_seq_bitmask()`, `trace_seq_hex_dump()`, and `trace_seq_acquire()`.

## Control Flow
Callers initialize a `trace_seq`, append formatted fragments, inspect overflow, and flush to `seq_file` or userspace. The inline `trace_seq_used()` deliberately uses `seq_buf_used()` rather than raw length so overflowed buffers do not expose undefined memory lengths.

## State, Persistence, And Dependencies
State is per `trace_seq`: embedded `seq_buf`, read position, full flag, and roughly 8 KiB backing buffer. It depends on `seq_buf` and page-size constants.

## Integration Points
Used by trace event output, flag/symbol printers, bitmask/hex dump renderers, tracefs reads, and dynamic event formatting.

## Risks And Test Signals
Risks include treating overflowed `seq.len` as valid, failing to check `full`, and returning pointers after further appends move the write position. Test signals include long-format overflow tests, user-copy length tests, hex dump output, and disabled-config no-op builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/trace_seq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracefs.h -->
# sources/distributed-fs/ceph-client/include/linux/tracefs.h

## Purpose
Declares tracefs and eventfs creation/removal APIs used by tracing infrastructure to expose control files, trace instances, and dynamic event directories.

## Important APIs, Types, And Functions
Defines `eventfs_callback`, `eventfs_release`, `struct eventfs_entry`, and forward `struct eventfs_inode`. APIs under `CONFIG_TRACING` include `eventfs_create_events_dir()`, `eventfs_create_dir()`, `eventfs_remove_events_dir()`, `eventfs_remove_dir()`, `tracefs_create_file()`, `tracefs_create_dir()`, `tracefs_remove()`, `tracefs_create_instance_dir()`, and `tracefs_initialized()`.

## Control Flow
Eventfs creates files lazily through callbacks: lookup/access iterates entry arrays, callback supplies mode, data, and file operations, and release handles callback data cleanup. Tracefs helper functions create normal files/directories and instance directories with mkdir/rmdir hooks.

## State, Persistence, And Dependencies
Runtime state is dentry/inode hierarchy and eventfs inode metadata owned by tracing. Callback data may be replaced per file. Dependencies include VFS `fs.h`, `seq_file`, and base types.

## Integration Points
Used by ftrace event directories, tracing instances, dynamic event files, and remote tracefs extensions.

## Risks And Test Signals
Risks include callback deadlocks because eventfs callbacks run under internal locks, data lifetime bugs, stale dentries after removal, and disabled-config missing prototypes. Test signals include lazy lookup tests, directory removal while files are open, instance mkdir/rmdir tests, and lockdep coverage for callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracepoint-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/tracepoint-defs.h

## Purpose
Provides lightweight tracepoint structure definitions for code that needs tracepoint keys or print flag tables without including the full tracepoint macro system.

## Important APIs, Types, And Functions
Defines `struct trace_print_flags`, `struct trace_print_flags_u64`, `struct tracepoint_func`, `struct tracepoint_ext`, `struct tracepoint`, `tracepoint_ptr_t`, `struct bpf_raw_event_map`, `DECLARE_TRACEPOINT()`, and `tracepoint_enabled()`.

## Control Flow
The only inline-like behavior is `tracepoint_enabled()`, which checks the tracepoint static key when tracepoints are configured and returns false otherwise. Full probe iteration and registration are in `tracepoint.h` and tracing core.

## State, Persistence, And Dependencies
`struct tracepoint` stores name, static key, static call metadata, iterator/probestub pointers, RCU-protected function array, and optional extension flags such as `faultable`. Dependencies are atomic and static-key infrastructure.

## Integration Points
Used by headers that need safe `tracepoint_enabled()` guards before calling out-of-line trace wrappers, and by BPF raw tracepoint registration through `bpf_raw_event_map`.

## Risks And Test Signals
Risks include calling tracepoints directly from headers causing bloat or side effects, failing to guard out-of-line calls, and bad alignment of BPF maps. Test signals include disabled tracepoint branch behavior, header-only users compiling without full tracepoint macros, and BPF raw tracepoint metadata validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracepoint-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracepoint.h -->
# sources/distributed-fs/ceph-client/include/linux/tracepoint.h

## Purpose
Implements the public kernel tracepoint declaration/definition macro layer, probe registration APIs, module iteration, static-key/static-call dispatch, RCU/SRCU unregister synchronization, and trace event macro fallbacks.

## Important APIs, Types, And Functions
Exports registration APIs `tracepoint_probe_register*()`, `tracepoint_probe_unregister()`, iteration helpers, module notifier helpers, `tracepoint_synchronize_unregister()`, grace-period wrappers, syscall tracepoint hooks, `tracepoint_string()`, `DECLARE_TRACE*`, `DEFINE_TRACE*`, `EXPORT_TRACEPOINT_SYMBOL*`, and default `TRACE_EVENT`/`DEFINE_EVENT` macro expansions.

## Control Flow
With tracepoints enabled, each declared tracepoint gets inline `trace_name()` and `trace_name_enabled()` helpers guarded by a static branch. Enabled calls enter `__do_trace_name()`, acquire the appropriate SRCU or tasks-trace guard, then dispatch either through static call to the first probe or an iterator over an RCU-protected `tracepoint_func` array. Syscall tracepoints are marked faultable and use tasks-trace RCU plus `might_fault()`. Disabled builds generate stubs returning `-ENOSYS` or false.

## State, Persistence, And Dependencies
Tracepoint definitions create section entries in `__tracepoints`, `__tracepoints_ptrs`, and string sections. Runtime state includes static keys, static calls, function arrays, priorities, module ownership, and optional extension registration/unregistration callbacks. Dependencies include SMP, SRCU, RCU tasks trace, static calls, modules, errno, and tracepoint definitions.

## Integration Points
Used by all `TRACE_EVENT` providers, ftrace, perf, BPF, modules exporting tracepoints, Rust tracepoint call wrappers, and userspace tracepoint string decoding.

## Risks And Test Signals
Risks include unregistering probes without waiting for both SRCU and tasks-trace grace periods, wrong faultable classification, RCU-not-watching calls, module unload races, static-call/probe-array mismatches, and macro redefinition issues across multiple trace headers. Test signals include probe register/unregister races, module unload tests, syscall tracepoint faulting-context tests, static key disabled overhead tests, and `__tracepoint_check` build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/transport_class.h -->
# sources/distributed-fs/ceph-client/include/linux/transport_class.h

## Purpose
Defines the generic transport class abstraction used by bus/storage transports to add class devices and attribute containers around lower-level devices.

## Important APIs, Types, And Functions
Key types are `struct transport_class`, `struct anon_transport_class`, and `struct transport_container`. Macros `DECLARE_TRANSPORT_CLASS()` and `DECLARE_ANON_TRANSPORT_CLASS()` initialize common class/container definitions. APIs include `transport_setup_device()`, `transport_add_device()`, `transport_configure_device()`, `transport_remove_device()`, `transport_destroy_device()`, register/unregister helpers, and class register/unregister functions.

## Control Flow
`transport_register_device()` calls setup, add, and destroys on add failure. `transport_unregister_device()` removes then destroys. Container registration is delegated to `attribute_container_register()` and unregister bugs out if the container cannot be unregistered.

## State, Persistence, And Dependencies
Runtime state is in embedded `struct class` and `attribute_container` objects, plus optional statistics/encryption attribute groups. Dependencies are device model, bug handling, and attribute containers.

## Integration Points
Used by SCSI and other transport-layer class implementations to attach transport-specific sysfs attributes and lifecycle hooks to generic devices.

## Risks And Test Signals
Risks include setup/add failure cleanup gaps, unregistering active attribute containers, incorrect match callbacks for anonymous classes, and sysfs attribute lifetime bugs. Test signals include device add/remove error injection, sysfs attribute presence, class unregister lockdep, and transport-specific hotplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/transport_class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ts-nbus.h -->
# sources/distributed-fs/ceph-client/include/linux/ts-nbus.h

## Purpose
Declares a tiny interface for Technologic Systems NBUS register access.

## Important APIs, Types, And Functions
Forward-declares `struct ts_nbus` and exports `ts_nbus_read()` and `ts_nbus_write()`, using 8-bit register addresses and 16-bit values.

## Control Flow
No implementation is present. Callers pass an NBUS handle, address, and either receive or write a 16-bit value; error handling is via integer return codes.

## State, Persistence, And Dependencies
State is opaque in `struct ts_nbus`. The header itself assumes fixed-width integer types are visible from including context.

## Integration Points
Used by platform or MFD child drivers sharing a TS NBUS controller.

## Risks And Test Signals
Risks include endianness/addressing assumptions and lack of visible locking contract. Test signals are controller read/write tests, invalid address handling, and concurrent child-driver access coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ts-nbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsacct_kern.h -->
# sources/distributed-fs/ceph-client/include/linux/tsacct_kern.h

## Purpose
Declares kernel helpers for taskstats accounting: basic accounting and extended task accounting updates.

## Important APIs, Types, And Functions
Exports `bacct_add_tsk()` when `CONFIG_TASKSTATS` is enabled, and `xacct_add_tsk()`, `acct_update_integrals()`, `acct_account_cputime()`, and `acct_clear_integrals()` when `CONFIG_TASK_XACCT` is enabled. Disabled configs provide inline no-ops.

## Control Flow
Callers populate a `struct taskstats` from a task and namespace context or update/clear per-task integral accounting. With disabled configs, calls compile away.

## State, Persistence, And Dependencies
The header owns no state. Runtime state lives in `task_struct` accounting fields and taskstats netlink output. It depends on `linux/taskstats.h`.

## Integration Points
Used by task exit, process accounting, and taskstats interfaces that report CPU, IO, and delay accounting.

## Risks And Test Signals
Risks include silent no-op behavior under disabled configs, namespace attribution mistakes, and stale integral updates. Test signals include taskstats netlink samples, task exit accounting, namespace-aware stats, and builds with taskstats/xacct toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsacct_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsm-mr.h -->
# sources/distributed-fs/ceph-client/include/linux/tsm-mr.h

## Purpose
Defines Trusted Security Module measurement-register descriptors and sysfs attribute-group creation helpers for confidential-computing guests.

## Important APIs, Types, And Functions
Key types are `struct tsm_measurement_register` and `struct tsm_measurements`. Flags include `TSM_MR_F_NOHASH`, `TSM_MR_F_WRITABLE`, `TSM_MR_F_READABLE`, `TSM_MR_F_LIVE`, and `TSM_MR_F_RTMR`. `TSM_MR_()` initializes readable hashed registers. APIs are `tsm_mr_create_attribute_group()` and `tsm_mr_free_attribute_group()`.

## Control Flow
Drivers provide an array of register descriptors plus optional `refresh()` and `write()` callbacks. Sysfs reads of live registers cause cache refresh; writes call the architecture-specific write/extend callback with exactly the register-sized data.

## State, Persistence, And Dependencies
Register names and value buffers must stay valid while the measurement set is in use. Runtime cache state is in driver-owned `mr_value` buffers. Dependency is hash algorithm metadata from `crypto/hash_info.h`.

## Integration Points
Used by TDX/SEV-SNP or other CC guest drivers that expose RTMR/MR state in sysfs and allow controlled extension of writable registers.

## Risks And Test Signals
Risks include dangling MR buffers, incorrect hash metadata, writable register semantics differing by architecture, and stale cache after live hardware changes. Test signals include sysfs read/write permissions, live refresh invocation, write-size enforcement, hash-name presentation, and attribute-group cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsm-mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsm.h -->
# sources/distributed-fs/ceph-client/include/linux/tsm.h

## Purpose
Defines the core TSM report-generation and device-registration interface for confidential-computing attestation providers.

## Important APIs, Types, And Functions
Key types are `struct tsm_report_desc`, `struct tsm_report`, `enum tsm_attr_index`, `enum tsm_bin_attr_index`, `struct tsm_report_ops`, and `struct tsm_dev`. APIs include `tsm_report_register()`, `tsm_report_unregister()`, `tsm_register()`, `tsm_unregister()`, and `find_tsm_dev()`. `DEFINE_FREE(put_tsm_dev, ...)` provides cleanup-attribute support for device references.

## Control Flow
A provider registers `tsm_report_ops` with a name, privilege floor, visibility callbacks, and `report_new()` implementation. Consumers configure report descriptors with input blob, privilege level, and optional service-provider fields; `report_new()` fills output, auxiliary, and manifest blobs.

## State, Persistence, And Dependencies
TSM report state includes copied input descriptor and dynamically allocated output blobs up to `TSM_REPORT_OUTBLOB_MAX`. Device state embeds `struct device`, id, and optional PCI TSM ops. Dependencies include sizes, UUID/GUID, devices, and base types.

## Integration Points
Integrates configfs/sysfs TSM report instances, CC guest attestation drivers, PCI TSM providers, and service-provider-specific attestation metadata.

## Risks And Test Signals
Risks include oversized output blobs, privilege-level validation gaps, provider singleton conflicts, blob lifetime leaks, and visibility callbacks hiding required ABI files. Test signals include report generation with boundary input sizes, provider register/unregister, privilege floor enforcement, service GUID parsing, and cleanup of output/aux/manifest buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty.h -->
# sources/distributed-fs/ceph-client/include/linux/tty.h

## Purpose
Defines the core open TTY object, termios flag accessors, tty lifecycle APIs, hangup/control helpers, and optional config stubs.

## Important APIs, Types, And Functions
Important pieces include termios character macros (`INTR_CHAR`, `EOF_CHAR`, etc.), flag macros (`I_IGNBRK`, `C_BAUD`, `L_ICANON`, etc.), `struct tty_struct`, `struct tty_file_private`, `enum tty_struct_flags`, `tty_io_nonblock()`, `tty_io_error()`, `tty_throttled()`, `tty_kref_get()`, and APIs for open/close, hangup, termios, throttling, resize, SAK, locking, audit, and VT ioctl support.

## Control Flow
TTY file operations operate through `tty_struct`: opens create or find a tty, attach driver/ldisc/port, and initialize termios. Reads and writes flow through the current line discipline and driver ops. Hangup and close set flags, cancel work, notify ldisc/driver, and drop references. Flow control uses locked `flow` fields and driver stop/start callbacks.

## State, Persistence, And Dependencies
`tty_struct` is transient while open and refcounted by `kref`; persistent device state belongs in `tty_port`. It stores termios, locks, counts, wait queues, process-group/session state, link to peer PTY, ldisc and driver private data, file list, and pending work. Dependencies include fs, termios, tty driver/ldisc/port, mutexes, rwsems, llist, and uapi tty definitions.

## Integration Points
Integrates character devices, line disciplines, low-level serial/PTY drivers, process sessions, proc/audit, virtual terminals, and termios ioctls.

## Risks And Test Signals
Risks include wrong tty-vs-port lifetime assumptions, lock-order bugs around ldisc/termios/legacy mutexes, use after hangup, missed nonblocking behavior during ldisc changes, and process-group races. Test signals include open/close/hangup stress, PTY peer closure tests, termios ioctl regression, concurrent readers/writers, audit/vt coverage, and disabled `CONFIG_TTY` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/tty_buffer.h

## Purpose
Defines the internal flip-buffer data structures used to stage received TTY characters and per-character status flags before delivery to a line discipline.

## Important APIs, Types, And Functions
Key types are `struct tty_buffer` and `struct tty_bufhead`. Inline helpers `char_buf_ptr()` and `flag_buf_ptr()` compute data and flag addresses. Flag constants are `TTY_NORMAL`, `TTY_BREAK`, `TTY_FRAME`, `TTY_PARITY`, and `TTY_OVERRUN`.

## Control Flow
Drivers append characters into the tail buffer through helpers declared in `tty_flip.h`. A work item on the buffer head later pushes committed data toward the line discipline. Separate `used`, `commit`, `lookahead`, and `read` offsets let producers and consumers track appended, committed, scanned, and delivered bytes.

## State, Persistence, And Dependencies
Per-port buffer state is in `tty_bufhead`: queue head/tail, flip workqueue, work item, mutex, priority, sentinel, free-list, memory accounting, and memory limit. `tty_buffer` stores optional next/free link, size/use offsets, a flag-buffer indicator, and aligned data area.

## Integration Points
Embedded in `struct tty_port` and used by serial drivers, PTYs, and ldisc receive paths.

## Risks And Test Signals
Risks include overrun when flags buffer is absent but error flags arrive, memory-limit accounting bugs, producer/consumer offset races, and stale lookahead positions. Test signals include parity/break injection, high-rate receive stress, flip workqueue ordering, memory-limit enforcement, and ldisc receive-room throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_driver.h -->
# sources/distributed-fs/ceph-client/include/linux/tty_driver.h

## Purpose
Defines the low-level TTY driver API, driver flags/types, driver object layout, allocation/registration helpers, and device node registration functions.

## Important APIs, Types, And Functions
Exports `enum tty_driver_flag`, `enum tty_driver_type`, `enum tty_driver_subtype`, `struct tty_operations`, and `struct tty_driver`. Important APIs include `tty_alloc_driver()`, `__tty_alloc_driver()`, `tty_driver_kref_get/put()`, `tty_set_operations()`, `tty_register_driver()`, `tty_unregister_driver()`, `tty_register_device*()`, `tty_unregister_device()`, and proc registration helpers.

## Control Flow
A driver allocates `struct tty_driver`, fills required metadata and `tty_operations`, registers the driver, and registers devices either statically or dynamically. Runtime calls enter driver ops for lookup/install/open/close/write/ioctl/termios/throttle/stop/start/hangup/break/modem/serial/poll/proc behavior. Driver teardown unregisters devices/driver and drops the kref.

## State, Persistence, And Dependencies
`tty_driver` persists across device opens and owns cdev arrays, active tty pointers, port pointers, per-line termios storage, workqueue, proc entry, linked PTY peer driver, driver private state, and module owner. Dependencies include VFS, cdev, kref, list, uaccess, termios, and seq_file.

## Integration Points
Used by serial, console, PTY, system tty, kgdboc polling, procfs driver reporting, and device-model sysfs nodes.

## Risks And Test Signals
Risks include mandatory `open`/`close` omissions, write callbacks sleeping in invalid contexts, incorrect dynamic-device flags, termios storage leaks, PTY peer mismatches, and module unload while ttys are open. Test signals include driver register/unregister, dynamic device hotplug, write_room/write behavior, kgdb polling if configured, proc output, and termios reset semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_flip.h -->
# sources/distributed-fs/ceph-client/include/linux/tty_flip.h

## Purpose
Declares and inlines the receive-side flip-buffer insertion API used by low-level TTY drivers to queue input for line discipline processing.

## Important APIs, Types, And Functions
APIs include `tty_buffer_set_limit()`, `tty_buffer_space_avail()`, `tty_buffer_request_room()`, `__tty_insert_flip_string_flags()`, `tty_prepare_flip_string()`, `tty_flip_buffer_push()`, `tty_insert_flip_string_fixed_flag()`, `tty_insert_flip_string_flags()`, `tty_insert_flip_char()`, `tty_insert_flip_string()`, `tty_ldisc_receive_buf()`, and exclusive buffer lock helpers.

## Control Flow
Drivers insert input bytes with either fixed flags or per-byte flags, then call `tty_flip_buffer_push()` to schedule delivery. `tty_insert_flip_char()` fast-paths a single normal or compatible flagged character into the current tail buffer when there is room; otherwise it falls back to the general string insertion routine, which can allocate/commit buffers as needed.

## State, Persistence, And Dependencies
State is in the port's `tty_bufhead` and current `tty_buffer`. This header depends on `tty_buffer.h` and `tty_port.h`, and receives into `struct tty_ldisc`.

## Integration Points
Used by serial interrupt handlers, USB serial, PTYs, and any driver feeding received bytes to a line discipline.

## Risks And Test Signals
Risks include failing to push after insertion, passing mutable flags incorrectly, fast-pathing an error flag into a no-flags buffer, and inserting while ldisc/port teardown is active. Test signals include receive bursts, fixed/per-byte flag validation, single-character fast path, exclusive lock behavior, and flow-control receive-room tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_flip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_ldisc.h -->
# sources/distributed-fs/ceph-client/include/linux/tty_ldisc.h

## Purpose
Defines line discipline locking and operation hooks, which sit between userspace TTY reads/writes and low-level TTY drivers.

## Important APIs, Types, And Functions
Defines `struct ld_semaphore`, `init_ldsem()`, read/write lock APIs, `struct tty_ldisc_ops`, `struct tty_ldisc`, `MODULE_ALIAS_LDISC()`, `tty_ldisc_ref()`, `tty_ldisc_deref()`, `tty_ldisc_ref_wait()`, `tty_ldisc_flush()`, `tty_register_ldisc()`, `tty_unregister_ldisc()`, and `tty_set_ldisc()`.

## Control Flow
TTY core invokes top-side ldisc hooks for open, close, flush, read, write, ioctl, termios, poll, and hangup. Low-level drivers invoke bottom-side hooks for `receive_buf`, `receive_buf2`, `lookahead_buf`, DCD change, and write wakeup. `ld_semaphore` protects ldisc changes so no new ldisc calls enter during replacement or shutdown.

## State, Persistence, And Dependencies
`struct tty_ldisc` stores ops and tty pointer. `struct tty_ldisc_ops` includes module owner for refcounting. Semaphore state includes atomic count, wait queues, spinlock, and optional lockdep map. Dependencies include fs, wait queues, atomics, lists, lockdep, and seq_file.

## Integration Points
Used by `n_tty`, PPP, HDLC, PPS, and custom line disciplines, and by TTY core ioctl/read/write dispatch.

## Risks And Test Signals
Risks include ldisc callbacks sleeping or doing I/O in wrong contexts, write_wakeup deadlocks if it writes directly, receive_buf2 partial-consume handling, lookahead duplicate processing, and module unload while referenced. Test signals include ldisc registration/switching, concurrent read/write during switch, receive_buf2 flow-control tests, write_wakeup work scheduling, and lockdep on ldsem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_ldisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_port.h -->
# sources/distributed-fs/ceph-client/include/linux/tty_port.h

## Purpose
Defines persistent per-device TTY port state and helper APIs for open/close/hangup, carrier control, flip-buffer linkage, and device registration.

## Important APIs, Types, And Functions
Key types are `struct tty_port_operations`, `struct tty_port_client_operations`, and `struct tty_port`. APIs include `tty_port_init()`, `tty_port_link_wq()`, `tty_port_link_device()`, register/unregister helpers, transmit-buffer allocation, `tty_port_destroy()`, `tty_port_get/put()`, flag accessors, `tty_port_tty_get/set()`, carrier/DTR/RTS helpers, hangup helpers, open/close helpers, and `tty_port_install()`.

## Control Flow
TTY drivers can delegate open/close to `tty_port_open()` and `tty_port_close()`, which serialize through the port mutex, invoke `activate()` on first open, block until carrier if needed, and call `shutdown()` when the final close or hangup completes. Port-to-tty references are acquired with `tty_port_tty_get()` and released with `tty_kref_put()`.

## State, Persistence, And Dependencies
`struct tty_port` persists beyond individual opens. It owns flip buffers, tty back-pointers, ops/client ops, spinlock, open counters, wait queues, async flags, console bit, mutexes, optional transmit buffer/fifo, close/drain delays, kref, and client data. Dependencies include kfifo, kref, mutexes, tty buffers, and wait queues.

## Integration Points
Used by serial-core-like drivers, USB serial, console ports, and any TTY driver wanting common open/close/hangup handling.

## Risks And Test Signals
Risks include using raw `port->tty` after hangup, missing `activate()`/`shutdown()` serialization, carrier wait races, kref/destruct lifetime bugs, and workqueue linkage surprises with `TTY_DRIVER_NO_WORKQUEUE`. Test signals include carrier wait/hangup tests, final-close shutdown, blocked open accounting, DTR/RTS toggles, suspend/active flag behavior, and kref destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tty_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/turris-omnia-mcu-interface.h -->
# sources/distributed-fs/ceph-client/include/linux/turris-omnia-mcu-interface.h

## Purpose
Defines the CZ.NIC Turris Omnia MCU I2C command set, status/control/feature bit fields, interrupt bits, and typed inline helpers for command read/write transactions.

## Important APIs, Types, And Functions
Enums cover MCU commands (`OMNIA_CMD_*`), flashing subcommands, status word bits, control byte bits, feature bits, extended status/control, interrupt bits, LED mode/state fields, poweroff magic, and USB over-current protection fields. APIs include `omnia_cmd_write_read()`, `omnia_cmd_write()`, typed write helpers for u8/u16/u32, `omnia_cmd_read()`, `omnia_compute_reply_length()`, `omnia_cmd_read_bits()`, `omnia_cmd_read_bit()`, and typed read helpers for u8/u16/u32.

## Control Flow
Callers serialize a command byte and optional little-endian payload, send it over I2C through `omnia_cmd_write_read()`, and optionally parse replies. `omnia_cmd_read_bits()` computes the shortest reply length needed for a bit mask, reads that many bytes, converts little-endian data to CPU order, and masks the requested bits. Feature flags gate use of newer MCU commands.

## State, Persistence, And Dependencies
No state is held. Wire protocol state is represented by fixed command IDs and bit masks. Dependencies include bitfield helpers, bitops, unaligned little-endian stores, byteorder, types, and `struct i2c_client`.

## Integration Points
Used by Turris Omnia platform drivers for LEDs, watchdog, MCU firmware/flashing, wakeup/poweroff, USB power/over-current, TRNG, crypto signing, board info, and interrupt handling.

## Risks And Test Signals
Risks include using commands without checking feature bits, invalid legacy 32-bit feature reads when bit 20 is set, endian mistakes, too-short reply lengths, and magic poweroff misuse. Test signals include mocked I2C command buffers, feature-gated command probing, bit-mask length tests, endian round-trips, interrupt mask read/write, and board hardware integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/turris-omnia-mcu-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/turris-signing-key.h -->
# sources/distributed-fs/ceph-client/include/linux/turris-signing-key.h

## Purpose
Declares a Turris-specific signing key subtype interface backed by the kernel key subsystem, typically for MCU/board signing support.

## Important APIs, Types, And Functions
Under `CONFIG_KEYS`, defines `struct turris_signing_key_subtype` with key/data/signature/public-key sizes, hash algorithm name, `get_public_key()` callback, and `sign()` callback. Provides `turris_signing_key_get_dev()` and `devm_turris_signing_key_create()`.

## Control Flow
A device-managed creator registers a signing key with subtype operations and description. Consumers retrieve the associated `struct device` from key payload slot 1 and call subtype callbacks to expose the public key or sign messages.

## State, Persistence, And Dependencies
Key state lives in `struct key` payload fields and device-managed lifetime. Dependencies are key management, base types, and `struct device`.

## Integration Points
Pairs with Turris Omnia MCU crypto commands and kernel keyring infrastructure. Device-managed creation ties key lifetime to driver lifetime.

## Risks And Test Signals
Risks include assumptions about key payload layout, callback size mismatches, missing `CONFIG_KEYS` stubs for callers, and signing hardware failures. Test signals include key creation/destruction, public-key extraction, signature-size validation, key payload device association, and build coverage with `CONFIG_KEYS` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/turris-signing-key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/typecheck.h -->
# sources/distributed-fs/ceph-client/include/linux/typecheck.h

## Purpose
Provides compile-time type-checking macros that still evaluate as ordinary expressions in C code.

## Important APIs, Types, And Functions
Exports `typecheck(type, x)`, `typecheck_fn(type, function)`, and `typecheck_pointer(x)`.

## Control Flow
The macros rely on `typeof`, dummy variables, pointer comparison, assignment to a function-typed object, or dereferencing in `sizeof` to force compile-time diagnostics. `typecheck()` and `typecheck_pointer()` evaluate to `1`.

## State, Persistence, And Dependencies
No runtime state or external dependencies. All behavior is compile-time.

## Integration Points
Used by kernel macros that need to assert argument types while preserving expression usability, such as time/comparison/helper macros.

## Risks And Test Signals
Risks include GNU C dependency, side effects if arguments are not carefully handled by caller macros, and confusing diagnostics. Test signals are compile-fail tests for wrong scalar/function/pointer types and compile-pass use in conditional expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/typecheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/types.h -->
# sources/distributed-fs/ceph-client/include/linux/types.h

## Purpose
Defines common in-kernel type aliases, scalar typedefs, list/RCU callback structures, atomic placeholders, address-size types, and utility function pointer types.

## Important APIs, Types, And Functions
Key exports include bitmap declaration macro, 128-bit aliases when supported, device/inode/mode/pid/time typedefs, `bool`, uid/gid types, `size_t`, `ssize_t`, BSD/SysV aliases, fixed-width integer aliases, aligned 64-bit aliases, `ktime_t`, `sector_t`, `blkcnt_t`, `dma_addr_t`, `gfp_t`, `phys_addr_t`, `resource_size_t`, `irq_hw_number_t`, `atomic_t`, `atomic64_t`, `rcuref_t`, `list_head`, `hlist_head`, `hlist_node`, `ustat`, `callback_head`/`rcu_head`, callback typedefs, swap/cmp function typedefs, and `struct rcuwait`.

## Control Flow
No runtime control flow is implemented. The header conditions type widths on architecture/config symbols such as DMA and physical address width.

## State, Persistence, And Dependencies
This is foundational compile-time type state. It includes UAPI Linux types and excludes most definitions under assembly. Alignment of `callback_head` is a correctness requirement for RCU/page tail bit encoding.

## Integration Points
Included throughout the kernel; every subsystem depends on its aliases and list/RCU base structures. It bridges UAPI type definitions to internal kernel names.

## Risks And Test Signals
Risks include ABI/type-width mismatches across architectures, redefinition conflicts with compiler/libc names, and alignment regressions in RCU callback structures. Test signals are allmodconfig builds, sparse bitwise type checks, 32/64-bit architecture builds, and compile checks for DMA/phys address width configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/u64_stats_sync.h -->
# sources/distributed-fs/ceph-client/include/linux/u64_stats_sync.h

## Purpose
Provides helpers for tear-free 64-bit statistics updates on 32-bit systems while compiling to cheap/no-op paths on 64-bit systems.

## Important APIs, Types, And Functions
Defines `struct u64_stats_sync`, `u64_stats_t`, and helpers `u64_stats_read()`, `u64_stats_copy()`, `u64_stats_set()`, `u64_stats_add()`, `u64_stats_sub()`, `u64_stats_inc()`, `u64_stats_init()`, `u64_stats_update_begin/end()`, IRQ-save update variants, `u64_stats_fetch_begin()`, and `u64_stats_fetch_retry()`.

## Control Flow
Writers take their own mutual exclusion, then call update begin/end around non-atomic counter changes. On 32-bit, begin disables preemption and starts a seqcount write; end completes the seqcount and re-enables preemption. Readers loop with fetch begin/retry until they read a stable sequence. On 64-bit, seqcount operations are no-ops and counters use `local64_t`.

## State, Persistence, And Dependencies
`struct u64_stats_sync` contains a seqcount only on 32-bit. Counters are stored in `u64_stats_t`. Dependencies include seqlock and either `asm/local64.h` or string/memcpy.

## Integration Points
Used by networking and driver statistics that are updated frequently and read from procfs/sysfs/ethtool without heavy locking.

## Risks And Test Signals
Risks include missing writer mutual exclusion, failing to disable preemption on 32-bit writers, using non-IRQ variants when IRQ readers/writers exist, and assuming multiple counters are mutually consistent on 64-bit. Test signals include 32-bit stress readers, KCSAN/concurrency tests, IRQ-context stats updates, wraparound tests, and netdev stats regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/u64_stats_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/u64_stats_sync_api.h -->
# sources/distributed-fs/ceph-client/include/linux/u64_stats_sync_api.h

## Purpose
Compatibility include wrapper for the u64 stats synchronization API.

## Important APIs, Types, And Functions
It only includes `linux/u64_stats_sync.h`; all exported types and functions come from that header.

## Control Flow
No control flow.

## State, Persistence, And Dependencies
No state beyond the included API. Dependency is exactly `u64_stats_sync.h`.

## Integration Points
Allows users that include the `_api` header name to receive the canonical u64 stats API.

## Risks And Test Signals
Risks are limited to include-path churn or accidental divergence. Test signals are compile coverage for files including `u64_stats_sync_api.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/u64_stats_sync_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uacce.h -->
# sources/distributed-fs/ceph-client/include/linux/uacce.h

## Purpose
Defines the kernel interface for UACCE, exposing accelerator queues to userspace through character devices, mmap regions, ioctls, PASID/SVA binding, and sysfs attributes.

## Important APIs, Types, And Functions
Key types are `struct uacce_qfile_region`, `struct uacce_ops`, `struct uacce_interface`, `enum uacce_dev_state`, `enum uacce_q_state`, `struct uacce_queue`, and `struct uacce_device`. APIs under `CONFIG_UACCE` are `uacce_alloc()`, `uacce_register()`, and `uacce_remove()`; disabled configs return `-ENODEV`/`-EINVAL` or no-op.

## Control Flow
A driver fills a `uacce_interface` and ops, allocates/registers a `uacce_device`, then userspace opens queues. Queue lifecycle flows through `get_queue`, `start_queue`, poll/update checks, mmap/ioctl operations, `stop_queue`, and `put_queue`. Device isolation state and error threshold callbacks expose reliability controls.

## State, Persistence, And Dependencies
`uacce_device` stores algorithm/API strings, queue region page counts, parent device, VF flag, flags, device id, cdev/device, mutex, private data, and queue list. `uacce_queue` stores private queue state, waitqueue, list node, qfile regions, mutex, state, PASID, SVA handle, and mapping. Dependencies include cdev and UAPI UACCE definitions.

## Integration Points
Used by accelerator drivers needing shared virtual addressing and userspace queue access, often with IOMMU SVA/PASID support.

## Risks And Test Signals
Risks include queue state-machine races, mmap region bounds, PASID/SVA lifetime leaks, isolation threshold validation, and disabled-config caller handling. Test signals include queue open/start/stop/close, mmap fault tests, ioctl compatibility, hot-unplug with active queues, waitqueue notification, and isolation sysfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uacce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uaccess.h -->
# sources/distributed-fs/ceph-client/include/linux/uaccess.h

## Purpose
Defines generic user-access wrappers around architecture raw copy/get/put primitives, including object-size hardening, fault injection, instrumentation, speculative-access barriers, pagefault disable guards, nofault copies, ABI-compatible struct copy helpers, and scoped unsafe user access macros.

## Important APIs, Types, And Functions
Core APIs include `copy_from_user()`, `copy_to_user()`, `__copy_from_user()`, `__copy_to_user()`, inatomic variants, `_inline_copy_from_user()`, `_inline_copy_to_user()`, `copy_mc_to_kernel()`, `pagefault_disable/enable()`, `pagefault_disabled()`, `faulthandler_disabled()`, `probe_subpage_writeable()`, `copy_from_user_inatomic_nontemporal()`, `check_zeroed_user()`, `copy_struct_from_user()`, `copy_struct_to_user()`, kernel/user nofault copy/string helpers, `get_kernel_nofault()`, unsafe get/put/copy macros, scoped user access macros, `get_user_inline()`, `put_user_inline()`, and hardened usercopy abort hook.

## Control Flow
Normal copies first validate compile/runtime copy size, check or mask user addresses, apply speculation barriers after `access_ok()`, instrument the copy, call arch raw copy, and return bytes not copied. Only `copy_from_user()` zero-pads the destination tail on short copy. Struct-copy helpers compare user and kernel struct sizes: old userspace gets zero-filled trailing kernel fields, newer userspace must provide zeroed unknown fields, and smaller user output receives only the known prefix with optional trailing-data notification.

## State, Persistence, And Dependencies
Persistent state touched here is `current->pagefault_disabled`. Other behavior is controlled by arch `asm/uaccess.h`, hardened usercopy static keys, fault injection, instrumentation, nospec, scheduler context, and copy-size checking.

## Integration Points
Every syscall, ioctl, procfs/sysfs binary path, and driver userspace ABI uses these helpers. Architecture ports provide raw primitives and optional masked/scoped access implementations.

## Risks And Test Signals
Risks include unchecked return values from non-zeroing `__copy_from_user()`, missing `access_ok()` around inatomic copies, incorrect struct ABI size rules, speculative access after failed checks, nesting scoped access illegally, and pagefault-disable misuse. Test signals include hardened usercopy tests, fault-injection short copies, KASAN/KMSAN instrumentation, struct versioning ABI tests, nofault copy tests, MTE/subpage probing, and 32/64-bit compat ioctl coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ubsan.h -->
# sources/distributed-fs/ceph-client/include/linux/ubsan.h

## Purpose
Declares a helper for reporting UBSAN failure descriptions when trap or KVM EL2 UBSAN handling is enabled.

## Important APIs, Types, And Functions
Exports `report_ubsan_failure(u32 check_type)` under `CONFIG_UBSAN_TRAP` or `CONFIG_UBSAN_KVM_EL2`; otherwise an inline stub returns `NULL`.

## Control Flow
Callers pass a UBSAN check type and receive a string description when supported. Disabled configs return no description.

## State, Persistence, And Dependencies
No state is stored. It depends on base `u32` visibility from including context.

## Integration Points
Used by UBSAN trap/reporting paths, including hypervisor/EL2 contexts that need compact failure reporting.

## Risks And Test Signals
Risks include missing declarations when callers assume a string is always available, and unsupported check types returning unexpected values in implementations. Test signals include UBSAN trap tests, KVM EL2 build coverage, and disabled-config compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ubsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ucopysize.h -->
# sources/distributed-fs/ceph-client/include/linux/ucopysize.h

## Purpose
Performs object-size sanity checking for usercopy and uio operations, including compile-time overflow diagnostics and optional hardened runtime range validation.

## Important APIs, Types, And Functions
Key APIs are `check_object_size()`, `copy_overflow()`, and `check_copy_size()`. Hardened builds declare `__check_object_size()` and static key `validate_usercopy_range`. Compile-time error hooks are `__bad_copy_from()` and `__bad_copy_to()`, and runtime overflow reporting is `__copy_overflow()`.

## Control Flow
`check_copy_size()` gets the compiler-known object size, rejects copies larger than that object, emits compile-time errors for constant overflows, calls runtime overflow reporting for dynamic overflows, rejects sizes larger than `INT_MAX`, then invokes hardened object-size validation. It returns whether the copy should proceed.

## State, Persistence, And Dependencies
Runtime state is the hardened usercopy static key. Dependencies include bug/WARN infrastructure and jump labels when hardened usercopy is enabled.

## Integration Points
Called by `uaccess.h` and uio copy paths before copying between kernel and user memory.

## Risks And Test Signals
Risks include false negatives when compiler object size is unknown, false positives in flexible-array patterns, disabled hardened validation reducing runtime coverage, and overflows larger than `INT_MAX`. Test signals include compile-time overflow tests, hardened usercopy LKDTM tests, dynamic-size rejection, and builds with hardened usercopy toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ucopysize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ucs2_string.h -->
# sources/distributed-fs/ceph-client/include/linux/ucs2_string.h

## Purpose
Declares helpers for handling UCS-2 strings and converting them to UTF-8.

## Important APIs, Types, And Functions
Defines `typedef u16 ucs2_char_t` and exports `ucs2_strnlen()`, `ucs2_strlen()`, `ucs2_strsize()`, `ucs2_strscpy()`, `ucs2_strncmp()`, `ucs2_utf8size()`, and `ucs2_as_utf8()`.

## Control Flow
Implementations measure bounded or unbounded UCS-2 strings, copy/compare UCS-2 character arrays, calculate required UTF-8 size, and emit UTF-8 bytes up to a maximum.

## State, Persistence, And Dependencies
No state is held. Dependencies are base types and NULL definition.

## Integration Points
Used by firmware/EFI/device-name paths that receive UCS-2 strings but expose UTF-8 text to kernel/userspace.

## Risks And Test Signals
Risks include truncation, malformed surrogate handling depending on implementation, off-by-one termination, and byte-vs-character size confusion. Test signals include bounded string tests, UTF-8 conversion vectors, truncation behavior, and comparisons with embedded NULs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ucs2_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/udp.h -->
# sources/distributed-fs/ceph-client/include/linux/udp.h

## Purpose
Defines in-kernel UDP socket state, hashing helpers, socket flags, encapsulation/GRO hooks, and convenience accessors for UDP networking.

## Important APIs, Types, And Functions
Key exports include `udp_hdr()`, UDP hash-table size constants, `udp_hashfn()`, UDP flag bits, `struct udp_prod_queue`, `struct udp_sock`, flag macros (`udp_test_bit`, `udp_set_bit`, etc.), `UDP_MAX_SEGMENTS`, `udp_sk()`, `udp_set_peek_off()`, no-check6 accessors, `udp_cmsg_recv()`, static keys `udp_encap_needed_key` and `udpv6_encap_needed_key`, `udp_encap_needed()`, `udp_unexpected_gso()`, `udp_allow_gso()`, hash iteration macros, and `udp_tunnel_sk()`.

## Control Flow
UDP paths derive headers from skb transport offsets, hash ports with per-netns mix, set socket flags atomically, and handle GRO/GSO acceptance. `udp_cmsg_recv()` reports UDP GRO segment size via control message when the skb is UDP L4 GSO. `udp_unexpected_gso()` rejects GSO packets not accepted by the socket or suspicious for tunnel encapsulation when encapsulation static keys and callbacks are active.

## State, Persistence, And Dependencies
`struct udp_sock` extends `inet_sock` and stores hash nodes, flags, corking length/GSO size, encapsulation callbacks, GRO callbacks, producer queue, reader queue, forward accounting, peek offset cache, tunnel list, and NUMA drop counters. Dependencies include inet sockets, skbuff, netns hashing, UAPI UDP, static keys, and optional IPv6/UDP tunnel configs.

## Integration Points
Used by IPv4/IPv6 UDP receive/transmit, UDP tunnels, GRO/GSO offload, socket control messages, per-net namespace hash tables, and encapsulation protocols.

## Risks And Test Signals
Risks include accepting unexpected GSO into tunnels, stale `peeking_with_offset`, incorrect per-net hash masks, callback lifetime races, zero-checksum policy mistakes, and cacheline-sensitive field churn. Test signals include UDP GRO/GSO tests, tunnel receive with malformed GSO types, IPv6 zero-checksum options, hash distribution tests, peek-offset recvmsg behavior, and encapsulation static-key enable/disable coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/udp.h -->
