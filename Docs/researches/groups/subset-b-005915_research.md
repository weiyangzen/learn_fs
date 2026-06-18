<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scmi_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/scmi_protocol.h

Purpose: `scmi_protocol.h` is the public in-kernel client interface for the Arm System Control and Management Interface stack. It defines common limits, revision metadata, SCMI device/driver registration, protocol acquisition through `struct scmi_handle`, per-protocol operation vtables, and notification report payloads used by clock, performance, power, sensor, reset, voltage, powercap, pinctrl, and system clients.

Important APIs/types/functions: Core exported types are `struct scmi_revision_info`, `struct scmi_handle`, `struct scmi_protocol_handle`, `struct scmi_device`, `struct scmi_driver`, `struct scmi_device_id`, and protocol ops tables such as `scmi_clk_proto_ops`, `scmi_perf_proto_ops`, `scmi_power_proto_ops`, `scmi_sensor_proto_ops`, `scmi_reset_proto_ops`, `scmi_voltage_proto_ops`, `scmi_powercap_proto_ops`, and `scmi_pinctrl_proto_ops`. Registration is through `scmi_driver_register()`, `scmi_driver_unregister()`, `scmi_protocol_register()`, `scmi_protocol_unregister()`, `scmi_register()`, `scmi_unregister()`, `module_scmi_driver()`, and `module_scmi_protocol()`. Notification integration is represented by `struct scmi_notify_ops` and event report structs such as `scmi_clock_rate_notif_report`, `scmi_perf_limits_report`, `scmi_sensor_update_report`, and `scmi_powercap_meas_changed_report`.

Control flow: A client driver binds to an `scmi_device`, uses `sdev->handle` to acquire a protocol, receives an ops table plus protocol handle, and then calls protocol-specific methods. Calls are dispatched through the SCMI core transport implementation, which owns message formatting, completion, and delayed responses. Notifications flow in reverse: protocol event sources are identified by protocol ID, event ID, and optional source ID, then the core invokes registered notifier blocks with one of the typed report payloads.

State and persistence behavior: This header does not store state itself. It describes cached protocol metadata (`scmi_clock_info`, `scmi_sensor_info`, `scmi_voltage_info`, `scmi_powercap_info`) whose ownership is in the SCMI core, and it exposes operations that mutate platform firmware state such as clock rates, power domain state, voltage configuration, pin muxing, power caps, and sensor configuration. Devres-managed acquisition and notifier registration tie lifetime to the SCMI device.

Dependencies and integration points: It depends on the device model, notifier chains, module registration, bitfield helpers, OPP/clock/regulator/pinctrl/powercap-style consumers, and the Arm SCMI transport selected by `CONFIG_ARM_SCMI_PROTOCOL`. Integration risk is highest at firmware boundaries: domains, IDs, units, asynchronous delayed responses, and notification source IDs must match the platform's advertised protocol version and capabilities.

Risks: Incorrect assumptions about atomic transports can sleep in atomic contexts. Misusing `__must_check` protocol info pointers, ignoring capability flags such as forbidden control fields, or passing invalid domain IDs can produce firmware errors. Sensor interval and config bitfields encode signed exponents and segmented ranges; wrong decoding can silently produce bad units. Powercap zero semantics are nuanced because cap disabling is separate from setting a cap value.

Test signals: Exercise protocol acquire/put, disabled `CONFIG_ARM_SCMI_PROTOCOL` stubs returning `-EINVAL`, clock parent/rate/state changes, performance OPP and fast-switch paths, sensor timestamped multi-axis reads, reset assert/deassert, voltage segmented ranges, powercap enable/threshold notifications, pinctrl group/function settings, and notifier register/unregister with wildcard and source-specific IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scmi_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scpi_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/scpi_protocol.h

Purpose: `scpi_protocol.h` exposes the older Arm System Control Processor Interface client API. It is a compact firmware-facing vtable for clocks, DVFS, sensors, and power-domain state before SCMI superseded much of this functionality.

Important APIs/types/functions: `struct scpi_opp` and `struct scpi_dvfs_info` describe frequency/voltage operating points and DVFS latency. `enum scpi_sensor_class` and `struct scpi_sensor_info` describe basic firmware sensors. `struct scpi_ops` carries function pointers for version lookup, clock range/value set/get, DVFS index and OPP-table handling, device-to-domain mapping, transition latency, OPP registration, sensor capability/info/value reads, and device power state get/set. `get_scpi_ops()` returns the active operations when `CONFIG_ARM_SCPI_PROTOCOL` is reachable and returns `NULL` otherwise.

Control flow: Consumers first call `get_scpi_ops()`, check for a non-NULL table, then call the relevant firmware operation. The header itself has no protocol state machine; the implementing SCPI driver owns transport messages and caching.

State and persistence behavior: SCPI operations can change firmware-controlled clock, DVFS, and power-domain state. The `scpi_dvfs_info` pointer returned by the implementation likely references implementation-owned OPP data, so consumers should treat it as read-only and scoped to the SCPI provider lifetime.

Dependencies and integration points: This integrates with `struct device`, OPP registration, clock users, sensor users, and platform firmware. It depends only on `<linux/types.h>` here but expects callers to include device declarations before using device-based callbacks.

Risks: The API predates SCMI and has a global `get_scpi_ops()` style, so absent-provider handling is essential. Packed firmware structs require exact layout. DVFS indexes must be validated against `count`, and callers must not assume every platform supports disabling a clock by writing zero.

Test signals: Boot with and without `CONFIG_ARM_SCPI_PROTOCOL`, validate `NULL` ops fallback, enumerate DVFS OPPs for device domains, test sensor count/info/value reads, and check that clock and power-state calls propagate firmware errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scpi_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/screen_info.h -->
# sources/distributed-fs/ceph-client/include/linux/screen_info.h

Purpose: `screen_info.h` provides kernel helpers for interpreting boot-time `struct screen_info` framebuffer and text-console metadata. It bridges architecture/UAPI boot parameters into resource reservation, pixel format detection, VGA/VBE/EFI framebuffer handling, and optional PCI fixups.

Important APIs/types/functions: Inline helpers include `__screen_info_has_lfb()`, `__screen_info_lfb_base()`, `__screen_info_set_lfb_base()`, `__screen_info_lfb_size()`, `__screen_info_vbe_mode_nonvga()`, `__screen_info_video_type()`, `screen_info_video_type()`, and `__screen_info_vesapm_info_base()`. Exported declarations include `screen_info_resources()`, `__screen_info_lfb_bits_per_pixel()`, `screen_info_pixel_format()`, `screen_info_apply_fixups()`, and `screen_info_pci_dev()`.

Control flow: Consumers inspect `screen_info_video_type()` first to classify initialized display output. Linear framebuffer helpers then compute base and size, including the special VESA size shift and optional 64-bit base extension. Resource builders and framebuffer drivers call the non-inline helpers to reserve memory, decode pixel formats, and discover matching PCI devices when PCI is enabled.

State and persistence behavior: The helpers operate on caller-provided `struct screen_info`. `__screen_info_set_lfb_base()` mutates the base fields and toggles `VIDEO_CAPABILITY_64BIT_BASE`; other inline helpers are read-only. Boot-time screen info persists as early console/framebuffer discovery state, but this header owns no storage.

Dependencies and integration points: It depends on UAPI `linux/screen_info.h`, bit macros, resource management, PCI, and framebuffer/pixel-format code. Integration points include simplefb/simpledrm, VGA arbitration, EFI framebuffer setup, and early architecture boot parameter parsing.

Risks: Misclassifying `orig_video_isVGA` can reserve or touch VGA resources incorrectly. 64-bit framebuffer bases require both low and extended fields to be coherent. VESA VLFB size is encoded differently from EFI, and `vesapm_seg` below `0xc000` is intentionally rejected.

Test signals: Cover EFI and VESA linear framebuffers, legacy text modes, non-VGA VBE bit 5, 64-bit framebuffer bases, zero or unknown video type, PCI-disabled stubs, and resource counts up to `SCREEN_INFO_MAX_RESOURCES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/screen_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scs.h -->
# sources/distributed-fs/ceph-client/include/linux/scs.h

Purpose: `scs.h` declares Shadow Call Stack support used to protect return addresses by keeping a separate per-task shadow stack. It provides allocation, task preparation/release, runtime enablement queries, and corruption checks around a sentinel value.

Important APIs/types/functions: With `CONFIG_SHADOW_CALL_STACK`, the header defines `SCS_ORDER`, `SCS_SIZE`, `GFP_SCS`, `SCS_END_MAGIC`, `task_scs()`, `task_scs_sp()`, and functions `scs_alloc()`, `scs_free()`, `scs_init()`, `scs_prepare()`, and `scs_release()`. Inline helpers include `scs_task_reset()`, `__scs_magic()`, `task_scs_end_corrupted()`, `scs_is_dynamic()`, and `scs_is_enabled()`. Disabled builds stub these to no-ops or false.

Control flow: Task setup allocates and initializes an SCS area, stores base/SP in thread info, and resets SP when tasks are reused. On release, the area is freed. Runtime checks compare the magic word at the end of the allocation and verify the shadow stack pointer remains inside bounds.

State and persistence behavior: State is per-task in `thread_info` fields and per-allocation in the sentinel word. `dynamic_scs_enabled` provides a static key for runtime dynamic SCS mode. No persistent disk state exists.

Dependencies and integration points: It depends on task/thread-info layout, page allocation, poison pointer constants, static keys, scheduler lifecycle, and architecture compiler support for shadow call stacks. It is tightly integrated with fork/exit and low-level call/return instrumentation.

Risks: Bad stack bounds or missed reset can corrupt future task state. Dynamic SCS checks must match architecture enablement. The sentinel check uses `READ_ONCE_NOCHECK()` to avoid sanitizer false positives; changing this can create noisy or unsafe instrumentation.

Test signals: Test `CONFIG_SHADOW_CALL_STACK` and disabled builds, fork/exit stress, task reuse, deliberate sentinel corruption, dynamic SCS toggling, and architecture context-switch paths that save/restore the SCS pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sctp.h -->
# sources/distributed-fs/ceph-client/include/linux/sctp.h

Purpose: `sctp.h` defines in-kernel SCTP wire-format structures, chunk and parameter identifiers, error causes, and helper macros shared by the SCTP protocol implementation. It mirrors RFC-defined packet layouts for common headers, chunks, TLV parameters, PR-SCTP, ADD-IP, AUTH, stream reset, ndata, and UDP encapsulation support.

Important APIs/types/functions: Core types include `struct sctphdr`, `sctp_hdr()`, `struct sctp_chunkhdr`, `enum sctp_cid`, `struct sctp_paramhdr`, `enum sctp_param`, data chunk structs (`sctp_data_chunk`, `sctp_idata_chunk`), INIT/SACK/heartbeat/shutdown/error chunks, PR-SCTP forward-TSN structs, ADD-IP structs, AUTH structs, stream reset request/response structs, `struct sctp_infox`, and `struct sctp_new_encap_port_hdr`. Macros include chunk/parameter action masks, `sctp_test_T_bit()`, SCTP DATA flags, DSCP/flowlabel masks, `SCTP_PAD4()`, and `SCTP_TRUNC4()`.

Control flow: Receive paths cast skb transport headers and chunk bodies to these structures after length validation. Chunk type high bits determine how unknown chunks are handled: discard, discard with error, skip, or skip with error. Parameter high bits do the equivalent for unknown TLVs. Association setup consumes INIT/INIT-ACK parameters; SACK and FWD-TSN update reliability state; AUTH validates protected chunks; ASCONF and RECONF update addresses or streams.

State and persistence behavior: The header owns no runtime state. Its structures encode transient packet state that drives SCTP association state machines elsewhere. Some structures use flexible arrays for variable TLVs, so state ownership belongs to skb buffers and association objects.

Dependencies and integration points: It depends on IPv4/IPv6 address structs, skbuff transport header access, UAPI SCTP definitions, endian types, and SCTP association internals. It integrates with netfilter, socket options, LSM SCTP hooks, checksum handling, and transport address management.

Risks: Wire structs use mixed endianness and packed protocol lengths; missing `ntohs`/`hton` style conversion or insufficient length checks can cause protocol bugs or out-of-bounds reads. Flexible arrays require 4-byte padding via `SCTP_PAD4()`. Unknown action bits must be honored exactly for interoperability.

Test signals: Fuzz chunk and parameter lengths, unknown chunk/parameter actions, INIT/COOKIE/SACK association setup, PR-SCTP FWD-TSN, ndata I-DATA/I-FWD-TSN, AUTH unsupported HMAC error, ADD-IP ASCONF serial handling, stream reset responses, UDP encapsulation restart cause, and skb header offset assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scx200.h -->
# sources/distributed-fs/ceph-client/include/linux/scx200.h

Purpose: `scx200.h` declares register offsets and presence detection for National Semiconductor SCx200/Geode-style configuration blocks. It is a low-level platform header for legacy embedded x86 hardware.

Important APIs/types/functions: The only external state is `scx200_cb_base`, with `scx200_cb_present()` checking whether the configuration base is nonzero. Macros define PCI bridge/configuration registers (`SCx200_DOCCS_BASE`, `SCx200_DOCCS_CTRL`), GPIO block size, clock generator size, miscellaneous block offsets, and individual register offsets such as `SCx200_PMR`, `SCx200_MCR`, `SCx200_INTSEL`, `SCx200_IID`, `SCx200_REV`, `SCx200_CBA`, and `SCx200_CBA_SCRATCH`.

Control flow: Platform probe code discovers and stores the configuration base, then users check `scx200_cb_present()` before doing I/O to the defined offsets. This header has no executable flow beyond that macro.

State and persistence behavior: State is a global base address exported by the SCx200 platform driver. Register writes affect chipset hardware state and persist until reset or reprogramming, not through this header.

Dependencies and integration points: It integrates with PCI discovery, GPIO, watchdog, clock, and platform drivers for SCx200-class devices. The header itself has no include guard in this snapshot, so repeated inclusion relies on build context not to redefine incompatible symbols.

Risks: Legacy fixed I/O offsets and global base state are easy to misuse if hardware is absent. Drivers must avoid touching registers when `scx200_cb_present()` is false and must serialize shared configuration block access in implementation code.

Test signals: Probe on hardware/emulation with and without the SCx200 config block, validate base discovery, check no I/O occurs when absent, and test register offsets against vendor documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scx200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scx200_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/scx200_gpio.h

Purpose: `scx200_gpio.h` provides inline GPIO accessors and shared state declarations for the SCx200 GPIO block. It is performance-oriented legacy I/O code that updates shadow output registers and writes them to the hardware port.

Important APIs/types/functions: Exports include `scx200_gpio_configure()`, `scx200_gpio_base`, `scx200_gpio_shadow[2]`, `scx200_gpio_ops`, and `scx200_gpio_present()`. Inline operations are `scx200_gpio_get()`, `scx200_gpio_current()`, `scx200_gpio_set_high()`, `scx200_gpio_set_low()`, `scx200_gpio_set()`, and `scx200_gpio_change()`. Internal macros compute bank, I/O address, shadow pointer, masked index, and the `outsl` write.

Control flow: Callers compute a GPIO bank from `index >> 5`, reduce the index to a bank-local bit, update or read `scx200_gpio_shadow`, and perform port I/O. Input reads add `0x04` to the bank I/O address and test the selected bit.

State and persistence behavior: Output state is mirrored in the global `scx200_gpio_shadow` array and pushed to hardware via `outsl`. The current electrical input state is read from hardware, while `scx200_gpio_current()` reports the shadowed drive value. Configuration changes are delegated to `scx200_gpio_configure()`.

Dependencies and integration points: It depends on x86 I/O helpers, bit operations, and `struct nsc_gpio_ops` from the NSC GPIO subsystem. It integrates with legacy GPIO clients and board support using direct I/O port access.

Risks: Shadow updates are not visibly locked here; concurrent writers can race unless implementation-level locking wraps calls. The inline assembly constraint and direct `outsl` assume the platform I/O model. Invalid indexes can select unexpected banks because no bounds check exists.

Test signals: Exercise absent hardware fallback, GPIO input reads, output high/low/toggle, concurrent updates to different pins in the same bank, configuration changes, and shadow/hardware consistency after repeated writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scx200_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seccomp.h -->
# sources/distributed-fs/ceph-client/include/linux/seccomp.h

Purpose: `seccomp.h` exposes kernel-side seccomp entry points, filter lifecycle hooks, user-facing prctl helpers, checkpoint/restore inspection hooks, and compile-time stubs when seccomp is disabled.

Important APIs/types/functions: It defines `SECCOMP_FILTER_FLAG_MASK`, notification addfd size constants, `secure_computing()`, `__secure_computing()`, `secure_computing_strict()`, `prctl_get_seccomp()`, `prctl_set_seccomp()`, `seccomp_mode()`, `seccomp_filter_release()`, `get_seccomp_filter()`, `seccomp_get_filter()`, `seccomp_get_metadata()`, and optional `proc_pid_seccomp_cache()`.

Control flow: On syscall entry, architectures with filter support call `secure_computing()`, which checks syscall work for `SECCOMP` and calls `__secure_computing()` only when needed. Prctl/syscall paths set or query mode and filter state. Task teardown releases filter references, and checkpoint/restore paths can read filters/metadata when configured.

State and persistence behavior: Per-task seccomp state lives in `struct seccomp` from `seccomp_types.h`, including mode, filter count, and active filter pointer. Filter references must be retained and released across task lifetime and clone paths. Disabled configs return `-EINVAL` or no-op values.

Dependencies and integration points: It depends on UAPI seccomp constants, thread-info syscall work flags, architecture seccomp support, BPF filter implementation, checkpoint/restore, procfs cache debug, and task lifecycle.

Risks: `secure_computing()` is syscall-hot; added work there impacts every syscall. Filter pointer access is lockless from current-task context and relies on lifecycle rules. Flag masks must track UAPI additions or userspace may pass unsupported flags incorrectly.

Test signals: Syscall filter allow/deny/trap/user notification, strict mode, TSYNC and TSYNC_ESRCH, disabled config stubs, checkpoint/restore filter export, task exit filter release, and proc seccomp cache debug when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seccomp_types.h -->
# sources/distributed-fs/ceph-client/include/linux/seccomp_types.h

Purpose: `seccomp_types.h` isolates the task seccomp state structure so scheduler and task headers can carry seccomp fields without pulling in the full seccomp API.

Important APIs/types/functions: With `CONFIG_SECCOMP`, `struct seccomp` contains `mode`, `atomic_t filter_count`, and `struct seccomp_filter *filter`. The comment documents that `filter` must be valid or NULL and is accessed without locking during syscall entry. Disabled builds define empty `struct seccomp` and `struct seccomp_filter`.

Control flow: No functions are defined. Syscall entry and seccomp management code read and update this structure through APIs in `seccomp.h` and implementation files.

State and persistence behavior: This is per-task state. `mode` controls disabled/strict/filter behavior, `filter_count` tracks installed filter layers, and `filter` points to the active filter chain. The filter lifetime is managed by reference helpers outside this header.

Dependencies and integration points: It depends on basic types and atomic counters through `linux/types.h` and seccomp implementation code. It integrates with `task_struct`/thread state, clone, exec, and syscall entry.

Risks: Because `filter` is read locklessly, writers must preserve ordering and lifetime. Empty-struct disabled builds require callers to avoid assuming storage layout or fields under `!CONFIG_SECCOMP`.

Test signals: Build seccomp-enabled and disabled kernels, clone/exec task state propagation, stacked filters, lockless syscall-entry reads under concurrent task teardown, and filter reference accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seccomp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/secretmem.h -->
# sources/distributed-fs/ceph-client/include/linux/secretmem.h

Purpose: `secretmem.h` exposes recognition helpers for secret memory mappings. Secretmem provides memory that is intentionally inaccessible to the kernel direct map and guarded from ordinary core dump or mapping behavior by implementation code.

Important APIs/types/functions: With `CONFIG_SECRETMEM`, it declares `secretmem_aops`, `secretmem_mapping()`, `vma_is_secretmem()`, and `secretmem_active()`. Disabled builds return false for all helpers.

Control flow: Callers test an `address_space` through `secretmem_mapping()` or a VMA through `vma_is_secretmem()` before applying special handling. `secretmem_active()` lets subsystems cheaply decide whether any secretmem handling may be needed.

State and persistence behavior: The header owns no state. It compares `mapping->a_ops` to the secretmem address-space operations and delegates VMA/activity state to implementation code. Secret memory lifetime follows file/mapping/VMA lifetime.

Dependencies and integration points: It integrates with MM, VMA walking, address-space operations, page fault handling, and memory accounting. Consumers include dump, migration, reclaim, and other code that must avoid exposing secret pages.

Risks: Pointer comparison to `secretmem_aops` requires mappings to be initialized correctly. Disabled stubs must preserve behavior where secretmem cannot exist. Callers must not infer page secrecy solely from unrelated VMA flags.

Test signals: Build with and without `CONFIG_SECRETMEM`, create secretmem mappings, validate `vma_is_secretmem()` and `secretmem_mapping()`, test fork/mmap/munmap lifecycle, and ensure dump/reclaim paths respect secret pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/secretmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/secure_boot.h -->
# sources/distributed-fs/ceph-client/include/linux/secure_boot.h

Purpose: `secure_boot.h` provides a small architecture hook for querying platform secure boot status.

Important APIs/types/functions: `arch_get_secureboot()` is declared when `CONFIG_HAVE_ARCH_GET_SECUREBOOT` is enabled and otherwise returns false inline. The API returns true only when platform secure boot is enabled; disabled or unsupported platforms report false.

Control flow: Security or integrity code calls `arch_get_secureboot()` during policy setup or runtime decisions. The architecture implementation supplies firmware-specific detection; the generic fallback avoids conditional compilation at call sites.

State and persistence behavior: The header owns no state. The returned value reflects platform firmware or architecture state and is expected to be stable after boot.

Dependencies and integration points: It depends on architecture support and integrates with lockdown, module signature policy, kexec restrictions, and integrity subsystems that may strengthen policy under secure boot.

Risks: A false fallback means generic callers must not treat false as proof that the platform lacks secure boot support unless the architecture config is known. Architecture implementations must avoid late firmware calls that can sleep or fail unpredictably in early boot.

Test signals: Build with and without `CONFIG_HAVE_ARCH_GET_SECUREBOOT`, boot secure-boot enabled and disabled systems, and verify downstream policy decisions such as lockdown/module-loading behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/secure_boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/securebits.h -->
# sources/distributed-fs/ceph-client/include/linux/securebits.h

Purpose: `securebits.h` wraps UAPI securebits definitions and provides the kernel `issecure(X)` helper for checking the current credentials' securebits mask.

Important APIs/types/functions: It includes `<uapi/linux/securebits.h>` and defines `issecure(X)` as `issecure_mask(X) & current_cred_xxx(securebits)`. The UAPI header supplies bit numbers and masks controlling capability behavior across uid transitions and exec.

Control flow: Capability and credential-changing paths call `issecure()` to decide whether securebits alter default capability fixups. This header does not implement transitions itself.

State and persistence behavior: State lives in current credentials' `securebits` field and persists according to credential copy/commit semantics. Securebits are per-credential, not global.

Dependencies and integration points: It depends on current credential accessors and capability code. It integrates with `security_task_fix_setuid()`, `cap_task_prctl()`, setuid/setgid handling, and user namespace capability rules.

Risks: The helper references current credentials, so it is only appropriate for current-task decisions. Incorrect use for arbitrary target credentials can check the wrong security state.

Test signals: Securebits prctl operations, setuid/setgid transitions, keep-caps/no-setuid-fixup behavior, locked bit enforcement, and namespace capability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/securebits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/security.h -->
# sources/distributed-fs/ceph-client/include/linux/security.h

Purpose: `security.h` is the central Linux Security Module facade. It declares LSM event types, lockdown reasons, security contexts/properties, capability fallback functions, and hundreds of `security_*()` hooks spanning process, filesystem, IPC, networking, keys, audit, BPF, perf, io_uring, block devices, and securityfs.

Important APIs/types/functions: Key types include `enum lsm_event`, `struct dm_verity_digest`, `enum lsm_integrity_type`, `enum lockdown_reason`, `struct lsm_prop`, and `struct lsm_context`. Important helpers include `kernel_load_data_id_str()`, `lsmprop_init()`, `lsmprop_is_set()`, notifier registration, `security_init()`, `early_security_init()`, `security_locked_down()`, `lsm_fill_user_ctx()`, and the large hook families `security_bprm_*`, `security_inode_*`, `security_file_*`, `security_task_*`, `security_socket_*`, `security_xfrm_*`, `security_key_*`, `security_bpf_*`, `security_perf_event_*`, and `security_uring_*`.

Control flow: Callers in core kernel paths invoke `security_*()` hooks at decision or labeling points. With `CONFIG_SECURITY`, implementation files dispatch to registered LSM hooks and aggregate decisions. Without `CONFIG_SECURITY` or per-feature configs, this header provides inline fallbacks, mostly allow/no-op, with selected capability enforcement delegated to `cap_*()` functions. Conditional sections separately gate network, path, keys, audit, securityfs, BPF, perf, and io_uring hooks.

State and persistence behavior: The header itself stores no security state but describes how state is attached to credentials, inodes, superblocks, files, IPC objects, sockets, keys, BPF objects, perf events, block devices, and LSM property structures. Context buffers returned through `struct lsm_context` must be released with `security_release_secctx()`. Mount options and xattrs carry persistent labels for LSMs.

Dependencies and integration points: It depends on core VFS, task credentials, namespaces, IPC, sockets, XFRM, keys, audit, BPF, perf, io_uring, block layer, kernel file loading, and individual LSM property headers for SELinux, Smack, AppArmor, and BPF LSM. The lockdown enum must stay synchronized with `security/lockdown/lockdown.c`.

Risks: Hook placement is security-critical: missing a call site can bypass policy, while incorrect fallback semantics can change behavior when security configs are disabled. Context length and user-copy helpers must avoid truncation and UAF. Lockdown reasons are not stable fine-grained ABI, so policy should not expose brittle reason-level guarantees.

Test signals: Build matrices for `CONFIG_SECURITY` and each feature flag, LSM stacking property propagation, inode xattr labeling, mount option parsing, exec credential transitions, capability fallbacks, network socket and SCTP hooks, key/audit rules, BPF token checks, perf/io_uring policy, securityfs disabled stubs, and lockdown reason coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sed-opal-key.h -->
# sources/distributed-fs/ceph-client/include/linux/sed-opal-key.h

Purpose: `sed-opal-key.h` abstracts read/write access to stored Self-Encrypting Drive Opal authentication keys, allowing platform keystores to override key handling.

Important APIs/types/functions: It declares `sed_read_key(char *keyname, char *key, u_int *keylen)` and `sed_write_key(char *keyname, char *key, u_int keylen)` when `CONFIG_PSERIES_PLPKS_SED` is enabled. Otherwise both return `-EOPNOTSUPP`.

Control flow: Opal or platform code asks for a named key, receives bytes and length through caller buffers, or writes a replacement key. The actual persistent keystore access is implemented elsewhere.

State and persistence behavior: This header owns no state. Enabled implementations may persist keys in protected platform storage; disabled stubs explicitly indicate unsupported operation.

Dependencies and integration points: It depends on kernel error codes and integrates with pSeries PLPKS-backed SED boot PIN/key workflows and the Opal block layer.

Risks: Callers must size buffers correctly and handle unsupported platforms. Key material lifetime and zeroization are implementation responsibilities; APIs use raw char buffers, so misuse can leak secrets.

Test signals: Enabled and disabled config builds, missing key, key length boundary handling, read/write round trips, permission policy in the platform keystore, and secret buffer cleanup in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sed-opal-key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sed-opal.h -->
# sources/distributed-fs/ceph-client/include/linux/sed-opal.h

Purpose: `sed-opal.h` is the block-layer interface for TCG Opal Self-Encrypting Drive support. It exposes device initialization, suspend unlock, ioctl dispatch, and a helper for recognizing Opal ioctls.

Important APIs/types/functions: `struct opal_dev` is opaque. `sec_send_recv` abstracts SECURITY SEND/RECEIVE transport. With `CONFIG_BLK_SED_OPAL`, exported APIs are `init_opal_dev()`, `free_opal_dev()`, `opal_unlock_from_suspend()`, `sed_ioctl()`, and `is_sed_ioctl()`. The header defines boot key names `OPAL_AUTH_KEY` and `OPAL_AUTH_KEY_PREV`. Disabled builds return NULL/false/no-op or zero for ioctl dispatch.

Control flow: A block driver creates an Opal device with its transport callback, forwards recognized ioctls to `sed_ioctl()`, and frees the Opal context at teardown. Resume paths may call `opal_unlock_from_suspend()` to restore access.

State and persistence behavior: `struct opal_dev` owns runtime discovery and session state. Commands mutate persistent drive locking ranges, credentials, shadow MBR state, and ownership on the device. The key-name constants integrate with persistent boot PIN storage.

Dependencies and integration points: It depends on UAPI `sed-opal.h`, block device ioctl paths, SCSI/NVMe/security command transports, suspend/resume, and optional SED key storage.

Risks: Disabled `sed_ioctl()` returning zero can hide accidental dispatch unless callers gate with `is_sed_ioctl()`. Opal operations are security-sensitive and often destructive (`REVERT`, secure erase, password changes). Transport callbacks must preserve buffer lengths and command direction.

Test signals: All listed `IOC_OPAL_*` recognition, enabled/disabled config behavior, discovery, ownership, lock/unlock, LR setup/status, suspend unlock, password rotation, shadow MBR writes, generic table access, and error injection from the transport callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sed-opal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6.h -->
# sources/distributed-fs/ceph-client/include/linux/seg6.h

Purpose: `seg6.h` is a kernel wrapper for Segment Routing over IPv6 UAPI definitions.

Important APIs/types/functions: It includes `<uapi/linux/seg6.h>` and declares no additional kernel-only types or helpers in this snapshot.

Control flow: There is no executable control flow. Kernel code includes this wrapper to use shared SRv6 constants and structures.

State and persistence behavior: No state is owned by the header. SRv6 route, policy, and tunnel state live in networking subsystems that consume the UAPI definitions.

Dependencies and integration points: It integrates with IPv6 routing, lightweight tunnels, netlink configuration, and SRv6 headers.

Risks: The wrapper must stay aligned with UAPI definitions; adding kernel-only helpers here should avoid ABI confusion.

Test signals: Build users of SRv6 UAPI constants, route installation, packet encapsulation/decapsulation, and netlink dumps using the included definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_genl.h -->
# sources/distributed-fs/ceph-client/include/linux/seg6_genl.h

Purpose: `seg6_genl.h` is a kernel wrapper for SRv6 generic netlink UAPI definitions.

Important APIs/types/functions: It includes `<uapi/linux/seg6_genl.h>` and adds no local declarations.

Control flow: There is no local control flow. Generic netlink handlers use the UAPI attributes and command IDs through this wrapper.

State and persistence behavior: No state is stored here; netlink families and SRv6 configuration objects live in networking implementation files.

Dependencies and integration points: It integrates with generic netlink, iproute2-facing SRv6 configuration, and IPv6 segment-routing control paths.

Risks: Attribute numbering and command IDs must remain UAPI-compatible. Kernel-only changes should be made carefully to avoid userspace mismatch.

Test signals: Generic netlink policy validation, SRv6 command parsing, netlink dump compatibility, and builds of networking modules including this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_hmac.h -->
# sources/distributed-fs/ceph-client/include/linux/seg6_hmac.h

Purpose: `seg6_hmac.h` wraps UAPI definitions for SRv6 HMAC configuration.

Important APIs/types/functions: It includes `<uapi/linux/seg6_hmac.h>` and declares no additional helpers.

Control flow: No executable code is present. SRv6 HMAC code consumes the UAPI constants and structures to configure authentication keys/algorithms.

State and persistence behavior: Key and policy state are owned by SRv6 networking code, not this wrapper.

Dependencies and integration points: It integrates with IPv6 segment-routing HMAC validation, netlink configuration, and crypto algorithm selection.

Risks: UAPI drift can break userspace configuration. HMAC key handling must be implemented outside this header with proper secret lifetime controls.

Test signals: Netlink HMAC key configuration, packet validation with matching and failing HMACs, disabled SRv6-HMAC configs, and userspace ABI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_hmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/linux/seg6_iptunnel.h

Purpose: `seg6_iptunnel.h` wraps UAPI definitions for SRv6 IP tunnel encap/decap behavior.

Important APIs/types/functions: It includes `<uapi/linux/seg6_iptunnel.h>` and adds no kernel-only API.

Control flow: No control flow is implemented here. Tunnel code uses UAPI structures for route attributes and lightweight tunnel setup.

State and persistence behavior: Tunnel state is stored in route/lwtunnel objects outside this header.

Dependencies and integration points: It integrates with IPv6 route attributes, lwtunnel infrastructure, netlink, and SRv6 encapsulation modes.

Risks: Attribute layout must match userspace. Callers must validate segment list lengths and tunnel mode constraints in implementation code.

Test signals: Route add/delete with SRv6 tunnel encap, packet forwarding through tunnels, netlink dump round trips, and invalid attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_local.h -->
# sources/distributed-fs/ceph-client/include/linux/seg6_local.h

Purpose: `seg6_local.h` wraps UAPI definitions for SRv6 local actions.

Important APIs/types/functions: It includes `<uapi/linux/seg6_local.h>` and provides no local functions or structs.

Control flow: No local flow exists. SRv6 local action implementations use the included constants to parse route attributes and execute endpoint behaviors.

State and persistence behavior: Endpoint behavior configuration lives in routing/lwtunnel state, not in this header.

Dependencies and integration points: It integrates with IPv6 routing, local SRv6 endpoint actions, netlink, and lwtunnel infrastructure.

Risks: Local action IDs and attribute semantics are UAPI. Implementation code must enforce action-specific validation and privilege checks.

Test signals: Configure each supported local action, verify packet processing, reject malformed netlink attributes, and dump routes back to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seg6_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/selection.h -->
# sources/distributed-fs/ceph-client/include/linux/selection.h

Purpose: `selection.h` declares the VT console selection, paste, mouse reporting, color table, and screen-buffer helper interfaces shared among console, TTY, virtual terminal, vc_screen, and selection code.

Important APIs/types/functions: Selection APIs include `clear_selection()`, `set_selection_user()`, `set_selection_kernel()`, `paste_selection()`, `sel_loadlut()`, `mouse_reporting()`, `mouse_report()`, and `vc_is_sel()`. Screen helpers include `screen_pos()`, `screen_glyph()`, `screen_glyph_unicode()`, `complement_pos()`, `invert_screen()`, `getconsxy()`, `putconsxy()`, `vcs_scr_readw()`, `vcs_scr_writew()`, `vcs_scr_updated()`, `vc_uniscr_check()`, and `vc_uniscr_copy_line()`. It also exposes `console_blanked` and console color arrays.

Control flow: TTY ioctls or kernel callers set selections, paste them into TTY input, load selection lookup tables, and report mouse events. VT rendering code uses glyph and inversion helpers to highlight selections and update vc_screen consumers.

State and persistence behavior: Selection state, LUTs, console blanking, color tables, and virtual console buffers are owned by implementation files. Selection persists until cleared or replaced and is tied to console/TTY state, not this header.

Dependencies and integration points: It depends on `tiocl` UAPI data, VT buffer representation, TTY structures, and `vc_data`. It integrates with console rendering, mouse selection, paste into line discipline, and `/dev/vcs*`.

Risks: User pointers in `set_selection_user()` and `sel_loadlut()` require careful copy/validation. Screen offsets must match current console geometry. Selection and paste behavior crosses privilege and TTY boundaries, so ownership and active console checks matter.

Test signals: TIOCL selection ioctls, kernel selection setup, paste into TTY, mouse reporting modes, Unicode screen copy, blanked console behavior, color table use, and vc_screen update notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/selection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sem.h -->
# sources/distributed-fs/ceph-client/include/linux/sem.h

Purpose: `sem.h` ties SysV semaphore undo state to task lifecycle while including UAPI semaphore definitions.

Important APIs/types/functions: It includes `<uapi/linux/sem.h>` and `sem_types.h`, forward declares `struct task_struct`, and declares `copy_semundo()` plus `exit_sem()` under `CONFIG_SYSVIPC`. Disabled builds provide no-op success for copy and an empty exit hook.

Control flow: Fork/clone paths call `copy_semundo()` to share or duplicate semaphore undo state based on clone flags. Task exit calls `exit_sem()` to apply and release undo adjustments. Without SysV IPC, the hooks compile away.

State and persistence behavior: Per-task SysV semaphore undo state is represented by `struct sysv_sem` in `sem_types.h`; actual undo lists and semaphore arrays live in IPC implementation code. Undo adjustments persist for the task lifetime and are applied at exit.

Dependencies and integration points: It integrates with task cloning, task exit, SysV IPC semaphore operations, and UAPI semaphore commands.

Risks: Undo-list sharing semantics must match clone flags. Missing `exit_sem()` would leak or fail to apply undo adjustments. Disabled stubs must not leave callers expecting real IPC state.

Test signals: SysV semaphore create/op with `SEM_UNDO`, fork/clone sharing, task exit rollback, disabled `CONFIG_SYSVIPC` builds, and IPC namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sem_types.h -->
# sources/distributed-fs/ceph-client/include/linux/sem_types.h

Purpose: `sem_types.h` defines the task-embedded SysV semaphore state container without pulling in the full semaphore API.

Important APIs/types/functions: It forward declares `struct sem_undo_list` and defines `struct sysv_sem`, which contains `struct sem_undo_list *undo_list` only when `CONFIG_SYSVIPC` is enabled.

Control flow: No functions are present. Task lifecycle code and SysV IPC code manipulate the undo-list pointer through APIs declared in `sem.h`.

State and persistence behavior: The `undo_list` pointer is per-task state. It links a task to semaphore undo adjustments that must be applied or released at exit. Disabled builds intentionally make the structure empty.

Dependencies and integration points: It integrates with `task_struct`, SysV IPC namespaces, semaphore arrays, clone, and exit paths.

Risks: Conditional structure layout means code must not access `undo_list` without `CONFIG_SYSVIPC`. Lifetime and sharing of `sem_undo_list` require external locking/refcounting in implementation code.

Test signals: Build both configs, verify task struct layout users, fork/exit with undo entries, shared undo list handling, and IPC namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sem_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/semaphore.h -->
# sources/distributed-fs/ceph-client/include/linux/semaphore.h

Purpose: `semaphore.h` declares the classic sleeping semaphore primitive. It provides initialization macros, dynamic init, blocking acquire variants, trylock/timeout, release, and optional last-holder tracking for hung task diagnostics.

Important APIs/types/functions: `struct semaphore` contains a raw spinlock, count, first waiter pointer, and optional `last_holder`. Macros include `__SEMAPHORE_INITIALIZER()` and `DEFINE_SEMAPHORE()`. APIs are `sema_init()`, `down()`, `down_interruptible()`, `down_killable()`, `down_trylock()`, `down_timeout()`, `up()`, and `sem_last_holder()`.

Control flow: `down*()` decrements count or queues the caller on the semaphore wait list and sleeps according to interruptibility/timeout mode. `up()` increments count or wakes a waiter. `down_trylock()` and `up()` are documented as safe from interrupt context, unlike blocking `down()` variants.

State and persistence behavior: Semaphore state is entirely in the `struct semaphore`: count, waiters, lock, and optional last holder. It persists for the object lifetime and is initialized statically or by `sema_init()`.

Dependencies and integration points: It depends on raw spinlocks, lockdep, wait-list implementation in `kernel/locking/semaphore.c`, and hung-task diagnostics. It integrates with legacy synchronization sites where ownership tracking is not required.

Risks: Semaphores have no owner, so they are easier to misuse than mutexes for mutual exclusion. Blocking variants must not run in atomic context. Direct member access is discouraged because waiter internals and diagnostics may change.

Test signals: Static and dynamic initialization, blocking/wakeup ordering, interruptible and killable signal handling, timeout behavior, trylock from interrupt context, hung-task last-holder reporting, and lockdep class initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/semaphore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_buf.h -->
# sources/distributed-fs/ceph-client/include/linux/seq_buf.h

Purpose: `seq_buf.h` defines a fixed-size string/binary formatting buffer used by tracing and other code that wants seq-file-like formatting without a file. It tracks overflow explicitly and offers print, append, hex, path, user-copy, and printk helpers.

Important APIs/types/functions: `struct seq_buf` stores `buffer`, `size`, and `len`. Helpers include `DECLARE_SEQ_BUF()`, `seq_buf_clear()`, `seq_buf_init()`, `seq_buf_has_overflowed()`, `seq_buf_set_overflow()`, `seq_buf_buffer_left()`, `seq_buf_used()`, `seq_buf_str()`, `seq_buf_get_buf()`, `seq_buf_commit()`, and `seq_buf_pop()`. External APIs include `seq_buf_printf()`, `seq_buf_vprintf()`, `seq_buf_print_seq()`, `seq_buf_to_user()`, `seq_buf_puts()`, `seq_buf_putc()`, `seq_buf_putmem()`, `seq_buf_putmem_hex()`, `seq_buf_path()`, `seq_buf_hex_dump()`, optional `seq_buf_bprintf()`, and `seq_buf_do_printk()`.

Control flow: Callers initialize a buffer, append through typed helpers or reserve/commit raw bytes, detect overflow when `len > size`, and call `seq_buf_str()` before treating the storage as a NUL-terminated string. Negative `seq_buf_commit()` marks overflow.

State and persistence behavior: State is caller-owned memory plus the current length. Overflow is sticky until `seq_buf_clear()` resets length. No allocation is performed by the inline helpers.

Dependencies and integration points: It depends on `seq_file` for printing into seq files, bug/minmax helpers, path formatting, user copy, binary printf, and tracing/logging paths.

Risks: `seq_buf_str()` warns and returns an empty string for zero-sized buffers. `seq_buf_commit()` BUGs if callers commit more bytes than reserved unless they signal overflow with a negative value. `len > size` is the overflow sentinel and must be preserved.

Test signals: Zero-sized buffers, exact-fit and overflow appends, reserve/commit API, negative commit, NUL termination after overflow, user copy offsets, path escaping, hex dumps, and binary printf builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_file.h -->
# sources/distributed-fs/ceph-client/include/linux/seq_file.h

Purpose: `seq_file.h` declares the kernel sequential file API used by procfs, debugfs, and other virtual files to stream generated content safely across reads and seeks.

Important APIs/types/functions: `struct seq_file` holds buffer, count, positions, mutex, operations, file, and private data. `struct seq_operations` defines `start`, `stop`, `next`, and `show`. APIs include `seq_open()`, `seq_read()`, `seq_read_iter()`, `seq_lseek()`, `seq_release()`, `seq_write()`, `seq_printf()`, `seq_put*()`, decimal/hex helpers, escaping/path helpers, `single_open()`, private-open helpers, list/hlist/percpu iterators, and attribute macros `DEFINE_SEQ_ATTRIBUTE()`, `DEFINE_SHOW_ATTRIBUTE()`, `DEFINE_SHOW_STORE_ATTRIBUTE()`, and `DEFINE_PROC_SHOW_ATTRIBUTE()`.

Control flow: A file open installs a `seq_operations` table. Reads call `start()`, then repeatedly `show()` and `next()` until the buffer is full or iteration completes, with `stop()` cleaning up. Overflow causes the core to allocate a larger buffer and replay output. Single-show helpers simplify one-record virtual files.

State and persistence behavior: `seq_file` state tracks the current read index, byte positions, private pointer, and buffer contents for an open file. It is protected by `m->lock`. Caller private data can be attached through inode private data or explicit private-open APIs.

Dependencies and integration points: It depends on VFS file operations, mutexes, credentials/user namespace, string escaping, list/hlist iteration, procfs/debugfs-style virtual files, and mount-option display helpers.

Risks: Iterators must update positions correctly to avoid infinite loops or skipped records. `seq_commit()` BUGs on over-commit and uses `count == size` as overflow. `seq_show_option_n()` uses a stack buffer sized by a constant expression, so callers must avoid large lengths.

Test signals: Multi-read and seek behavior, buffer growth replay, list and RCU list iteration, private data propagation, mount option escaping, single_open files, proc attribute macros, user namespace lookup, and overflow detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_file_net.h -->
# sources/distributed-fs/ceph-client/include/linux/seq_file_net.h

Purpose: `seq_file_net.h` supplies small helpers for network namespace-aware seq files.

Important APIs/types/functions: It declares `seq_open_net()`, `seq_release_net()`, and `single_open_net()`. Inline helpers `seq_file_net()` returns the `struct net *` stored in `seq->private`, while `seq_net_private()` returns caller private data stored immediately after an internal `struct seq_net_private` header.

Control flow: Network proc/debug files open through `seq_open_net()` or `single_open_net()`, which bind the file to a net namespace and allocate optional private storage. Show/iterator code retrieves namespace or private storage from the seq file.

State and persistence behavior: Per-open state is allocated behind `seq->private`, containing a net namespace pointer and optional private bytes. It is released by `seq_release_net()`.

Dependencies and integration points: It depends on `seq_file`, `struct net`, and network namespace lifecycle. It integrates with `/proc/net`, per-net operations, and virtual network files.

Risks: Callers must use the matching release function or leak namespace references/private storage. `seq_net_private()` assumes the private layout created by `seq_open_net()`.

Test signals: Open/read/release under multiple network namespaces, private storage sizing, namespace teardown while files are open, single-open net files, and mismatched release error review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seq_file_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock.h -->
# sources/distributed-fs/ceph-client/include/linux/seqlock.h

Purpose: `seqlock.h` implements sequence counters and seqlocks: concurrency primitives optimized for lockless readers that retry when writers update protected data. It also provides associated-lock seqcount variants, latch seqcounts for NMI-safe double-buffering, seqlock writer/reader APIs, and scoped read helpers.

Important APIs/types/functions: Core APIs include `seqcount_init()`, `SEQCNT_ZERO()`, associated lock initializers (`seqcount_spinlock_init()` etc.), `read_seqcount_begin()`, `read_seqcount_retry()`, raw read variants, `write_seqcount_begin/end()`, raw write variants, `raw_write_seqcount_barrier()`, `write_seqcount_invalidate()`, latch APIs (`seqcount_latch_init()`, `read_seqcount_latch()`, `write_seqcount_latch_begin/write/end()`), `seqlock_init()`, `DEFINE_SEQLOCK()`, `read_seqbegin()`, `read_seqretry()`, write seqlock variants, exclusive read-lock variants, `read_seqbegin_or_lock()`, `need_seqretry()`, `done_seqretry()`, IRQ-save variants, and `scoped_seqlock_read()`.

Control flow: Lockless readers sample an even sequence, read protected fields, then retry if the sequence changed. Writers increment to odd, apply updates with ordering barriers, then increment to even. Associated-lock seqcounts assert or use lock state for writer serialization; on PREEMPT_RT, readers of preemptible associated locks may briefly take/release the writer lock to let preempted writers complete. Seqlocks embed a spinlock and sequence counter for automatic writer serialization.

State and persistence behavior: State is the sequence counter value, optional associated lock pointer, and embedded seqlock spinlock. Odd sequence means a writer is active; even sequence means stable. Latch seqcounts use the low bit to select one of two copies while writers update the inactive copy.

Dependencies and integration points: It depends on compiler annotations, cleanup attributes, KCSAN, lockdep, mutex/spinlock APIs, preemption control, barriers, and processor relax. It is used by timekeeping, networking, VFS, and other read-mostly data paths.

Risks: Protected data must not contain pointers whose lifetime can disappear under lockless readers. Plain seqcount writers must be externally serialized and non-preemptible; interrupt/BH disabling is required when readers can run there. Missing retry loops or barriers produce torn reads. PREEMPT_RT behavior changes writer/reader progress assumptions.

Test signals: Lockless reader retry loops, writer serialization lockdep assertions, PREEMPT_RT builds, KCSAN instrumentation, IRQ/BH writer variants, latch double-buffer correctness under NMI-like reads, raw barrier users, scoped read helper codegen, and pointer-lifetime misuse review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock_api.h -->
# sources/distributed-fs/ceph-client/include/linux/seqlock_api.h

Purpose: `seqlock_api.h` is a compatibility forwarding header that includes `linux/seqlock.h`.

Important APIs/types/functions: It declares no independent symbols; all seqcount and seqlock APIs come from `seqlock.h`.

Control flow: Inclusion simply exposes the main seqlock API. There is no runtime code.

State and persistence behavior: No state is owned by this wrapper.

Dependencies and integration points: It exists to satisfy include users that refer to the API-specific header while centralizing implementation in `seqlock.h`.

Risks: Because it is only one include line, any include-order or guard behavior is inherited from `seqlock.h`. Do not add partial duplicate definitions here.

Test signals: Build include users of `seqlock_api.h`, verify no symbol duplication, and ensure API availability matches direct inclusion of `seqlock.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock_types.h -->
# sources/distributed-fs/ceph-client/include/linux/seqlock_types.h

Purpose: `seqlock_types.h` contains the type definitions for sequence counters, associated-lock sequence counters, and `seqlock_t` without exposing the full API body.

Important APIs/types/functions: It defines `seqcount_t`, `seqcount_raw_spinlock_t`, `seqcount_spinlock_t`, `seqcount_rwlock_t`, `seqcount_mutex_t`, and `seqlock_t`. The `SEQCOUNT_LOCKNAME()` macro generates associated-lock structures with optional lock pointers under lockdep or PREEMPT_RT. `seqlock_t` contains a `seqcount_spinlock_t` and `spinlock_t`.

Control flow: No functions execute here. The generated type layout enables API macros in `seqlock.h` to associate counters with serialization locks and to support PREEMPT_RT reader progress.

State and persistence behavior: `seqcount_t` stores the sequence value and optional lockdep map. Associated variants store the actual `seqcount_t` plus optional lock pointer. `seqlock_t` embeds both sequence counter and spinlock for persistent synchronization state.

Dependencies and integration points: It depends on lockdep, mutex, and spinlock type headers. It integrates with the main seqlock API and with object definitions that need seqlock fields without all inline helpers.

Risks: Conditional `__SEQ_LOCK()` layout means structure size changes with lockdep/PREEMPT_RT. Writers must still follow the contracts documented in comments: serialization, non-preemptibility, and avoiding pointer-protected data for lockless readers.

Test signals: Compile structure users under lockdep, PREEMPT_RT, and minimal configs; static initializers; associated-lock pointer initialization; and ABI-sensitive embedded structure layout review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/seqlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serdev.h -->
# sources/distributed-fs/ceph-client/include/linux/serdev.h

Purpose: `serdev.h` defines the serial device bus abstraction that lets devices attached behind UART controllers bind to normal device drivers instead of ad hoc line-discipline plumbing.

Important APIs/types/functions: Core types are `struct serdev_device_ops`, `struct serdev_device`, `struct serdev_device_driver`, `enum serdev_parity`, `struct serdev_controller_ops`, and `struct serdev_controller`. APIs include device/controller allocation/add/remove/put helpers, driver register/unregister macros, open/close, devm open, baudrate, flow control, write buffer/write blocking/write flush/wait, modem control, break control, parity, TTY-port registration, ACPI UART resource lookup, and OF controller lookup.

Control flow: A UART controller registers a `serdev_controller`; discovery creates a `serdev_device`; a client driver binds, sets receive/write-wakeup ops, opens the device, configures serial parameters, and exchanges data through controller callbacks. Receive and write-wakeup calls flow from controller to client ops.

State and persistence behavior: Device/controller objects are device-model managed. `serdev_device` stores ops, completion, and write mutex; `serdev_controller` stores host, bus number, attached serdev, and ops. Open state, modem signals, and queued writes are maintained by implementation code.

Dependencies and integration points: It depends on the device model, completions, mutexes, termios, polling helpers, TTY core, ACPI, OF, and serial controller drivers. Disabled configs return `-ENODEV`, `-EOPNOTSUPP`, false, or NULL stubs.

Risks: `write_wakeup` must not sleep, while `receive_buf` may sleep. Controller callbacks must handle partial writes and lifetime of attached devices. Matching release/unregister functions are needed to avoid dangling device references.

Test signals: Controller add/remove, client probe/remove/shutdown, disabled config stubs, blocking writes with timeout, partial write wakeups, RX callback byte counts, CTS polling, RTS/parity/break controls, TTY-port bridge registration, ACPI/OF discovery, and hot-unplug races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial.h -->
# sources/distributed-fs/ceph-client/include/linux/serial.h

Purpose: `serial.h` provides common UART constants and counters layered over UAPI serial headers.

Important APIs/types/functions: It includes UAPI serial and 8250 register definitions, defines `UART_IER_ALL_INTR`, `UART_LCR_WLEN(x)`, `UART_LSR_BOTH_EMPTY`, `uart_lsr_tx_empty()`, `UART_MSR_STATUS_BITS`, and `struct async_icount` counters for modem/input line interrupts and RX/TX/error accounting.

Control flow: Serial drivers test line status with `uart_lsr_tx_empty()`, set interrupt-enable masks, derive word-length bits, and update `async_icount` as UART interrupts and errors occur.

State and persistence behavior: The header owns no state. `async_icount` is embedded in serial ports and persists as runtime statistics exposed through serial ioctls or diagnostics.

Dependencies and integration points: It integrates with UART drivers, 8250-compatible register definitions, TTY serial core, modem-control handling, and userspace serial APIs.

Risks: Register bit definitions are hardware-facing; using the wrong mask can miss interrupts or report transmit-empty too early. Counter overflow is possible on long-lived ports but uses 32-bit UAPI-compatible fields.

Test signals: TX-empty detection, interrupt mask setup, modem status counters, RX/TX/error counter increments, UAPI serial ioctl compatibility, and different UART word-length settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_8250.h -->
# sources/distributed-fs/ceph-client/include/linux/serial_8250.h

Purpose: `serial_8250.h` declares the shared 8250/16550 UART core interfaces, platform data, per-port state extension, IRQ/timer hooks, console setup, and helper routines used by 8250-compatible serial drivers.

Important APIs/types/functions: Key types are `struct plat_serial8250_port`, `struct uart_8250_ops`, `struct uart_8250_em485`, and `struct uart_8250_port`. APIs include `serial8250_register_8250_port()`, unregister/suspend/resume, early setup, uartclk update, termios/ldisc/mctrl/startup/shutdown/PM/divisor helpers, IRQ handlers, RX/TX helpers, modem status, init/defaults, console write/setup/exit, ISA configurator, `hp300_setup_serial_console()`, `rt288x_setup()`, and `au_platform_setup()`.

Control flow: Platform or bus drivers fill port data, register with the 8250 core, and let the core manage startup, interrupts, RX/TX, modem status, PM, and console paths. IRQ setup can use the shared 8250 IRQ chain or driver-specific callbacks. RS485 emulation uses hrtimers for start/stop transmit timing.

State and persistence behavior: `uart_8250_port` extends `uart_port` with saved register state (`acr`, `fcr`, `ier`, `lcr`, `mcr`), capabilities/bugs, FIFO load size, IRQ list node, DMA pointer, GPIO modem controls, RS485 emulation, runtime-PM TX activity, saved LSR/MSR flags, and overrun backoff work. This state persists for the registered port lifetime.

Dependencies and integration points: It depends on serial core, 8250 register definitions, platform devices, timers/workqueues, DMA support, modem GPIOs, earlycon, console, PM, and SoC-specific setup helpers.

Risks: Some UART status bits clear on read and must be saved in `lsr_saved_flags`/`msr_saved_flags`. Port locks protect divisor and register updates. Incorrect IRQ setup/release can break shared IRQ chains. Console and suspend paths must handle `canary`/no-console-suspend cases carefully.

Test signals: Register/unregister, shared and dedicated IRQ paths, RX/TX FIFO handling, break and SysRq handling, saved status bits, DMA and PIO paths, RS485 timers, overrun backoff, PM suspend/resume, earlycon, console setup/write/exit, and SoC-specific setup stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_bcm63xx.h -->
# sources/distributed-fs/ceph-client/include/linux/serial_bcm63xx.h

Purpose: `serial_bcm63xx.h` defines Broadcom BCM63xx UART register offsets and bit masks used by the platform serial driver.

Important APIs/types/functions: Macros cover control (`UART_CTL_REG` and reset, stop bit, bits-per-symbol, parity, loopback, RX/TX enable, baud generator bits), baud word, miscellaneous modem/FIFO threshold/fill register, external input configuration and modem interrupt bits, interrupt mask/status bits for TX/RX/error events, and FIFO data/error bits including `UART_FIFO_ANYERR_MASK`.

Control flow: The driver programs control and baud registers, configures FIFO thresholds, reads modem external inputs, services interrupt status bits, masks/unmasks interrupts, and reads FIFO bytes while checking frame/parity/break error bits.

State and persistence behavior: The header owns no state. The hardware registers retain programmed UART mode, modem outputs, FIFO thresholds, interrupt masks, and baud settings until changed or reset.

Dependencies and integration points: It integrates with the BCM63xx serial driver, platform resource mapping, UART/TTY serial core, and interrupt handling.

Risks: Bit definitions include hardware quirks such as overlapping TX parity shift values in this snapshot. Driver code must use masks consistently and avoid confusing interrupt mask and status halves. FIFO error bits must be consumed with the data byte they describe.

Test signals: Baud programming, RX/TX enable/disable, FIFO reset, interrupt mask/status handling for all TX/RX/error bits, modem input/output, parity/stop-bit settings, loopback mode, and error-byte reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_bcm63xx.h -->
