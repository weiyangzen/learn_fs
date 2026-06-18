# subset-b-006350 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/network.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/network.c

## Purpose

This file implements TOMOYO's network policy parser, auditor, and LSM-side socket permission checks for INET and UNIX sockets. It translates policy lines such as `network inet stream bind ...` and `network unix dgram send ...` into ACL objects, then checks bind, listen, connect, and datagram send operations against those ACLs.

## Important APIs, types, and functions

The local address carriers are `tomoyo_inet_addr_info`, `tomoyo_unix_addr_info`, and `tomoyo_addr_info`. Public helpers include `tomoyo_parse_ipaddr_union`, `tomoyo_print_ip`, `tomoyo_write_inet_network`, `tomoyo_write_unix_network`, `tomoyo_socket_listen_permission`, `tomoyo_socket_connect_permission`, `tomoyo_socket_bind_permission`, and `tomoyo_socket_sendmsg_permission`. Internal matchers and mergers include `tomoyo_same_inet_acl`, `tomoyo_same_unix_acl`, `tomoyo_merge_inet_acl`, `tomoyo_merge_unix_acl`, `tomoyo_check_inet_acl`, and `tomoyo_check_unix_acl`. The `tomoyo_inet2mac` and `tomoyo_unix2mac` tables map protocol/operation pairs into TOMOYO MAC indices.

## Control Flow

Policy writes parse protocol and operation tokens, build permission bitmaps, parse IP/name and port/number unions, then call `tomoyo_update_domain()` with duplicate detection and bitmap merge callbacks. Runtime hooks first reject kernel threads and unsupported families/protocols, then normalize the kernel socket operation into a `tomoyo_addr_info`. INET checks decode sockaddr family, address, and port before `tomoyo_inet_entry()` initializes a request, scans ACLs, and sends an audit/supervisor request. UNIX checks encode abstract or pathname socket names through `tomoyo_encode2()`, fill path metadata, then follow the same request/audit loop.

## State and Persistence

Persistent policy is stored in domain ACL lists updated through TOMOYO common code. This file keeps no long-lived mutable state beyond static lookup tables. Request-local state includes sockaddr-derived address pointers and temporary encoded UNIX names. Permission bitmaps are updated with `READ_ONCE()`/`WRITE_ONCE()` because readers can race with policy merge paths.

## Dependencies and Integration Points

It depends on TOMOYO common parsers, groups, request initialization, ACL traversal, audit/supervisor logging, and path encoding. It is called from LSM socket hooks registered in `tomoyo.c`. It depends on kernel networking types, `in4_pton`, `in6_pton`, sockaddr layout, and socket operation callbacks such as `getname`.

## Risks and Test Signals

Risks include sockaddr length mistakes, IPv4/IPv6 range comparison errors, raw-socket protocol-as-port handling, abstract UNIX socket encoding, unsupported protocol table entries mapping to zero and silently disabling checks, and policy merge races. Useful signals are policy parser tests for address ranges/groups and port ranges, bind/listen/connect/sendmsg tests for INET and UNIX sockets, audit replay tests, and LSM integration tests for kernel-thread bypass and unsupported family bypass.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/network.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/realpath.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/realpath.c

## Purpose

This file converts kernel paths and binary socket/path strings into TOMOYO's canonical, printable policy names. It provides realpath-like resolution that ignores chroot roots where appropriate, appends directory trailing slashes, prefixes local filesystem or device names for non-global paths, and escapes non-printable bytes.

## Important APIs, types, and functions

Public APIs are `tomoyo_encode2()`, `tomoyo_encode()`, `tomoyo_realpath_from_path()`, and `tomoyo_realpath_nofollow()`. Internal helpers are `tomoyo_get_absolute_path()`, `tomoyo_get_dentry_path()`, and `tomoyo_get_local_path()`. `tomoyo_encode2()` is also used by network code for UNIX socket names.

## Control Flow

Encoding first computes the escaped output length, allocates with `GFP_NOFS`, doubles backslashes, keeps printable ASCII above space and below DEL, and emits other bytes as octal `\ooo`. Path resolution grows a temporary buffer by powers of two, uses `d_dname()` for pseudo dentries, otherwise chooses local or absolute naming based on filesystem capabilities and device requirements. If `d_absolute_path()` returns `-EINVAL`, it falls back to local path naming. Successful paths are encoded before returning.

## State and Persistence

The file stores no persistent state. It allocates temporary buffers and returns allocated encoded strings owned by callers. The local path branch uses filesystem metadata, device numbers, procfs pid namespace information, and root inode operations at the time of the call.

## Dependencies and Integration Points

It depends on VFS path helpers, procfs magic and pid namespaces, superblock metadata, device major/minor values, TOMOYO OOM warning, and common TOMOYO path consumers. `tomoyo_realpath_nofollow()` integrates with `kern_path()` and `path_put()`.

## Risks and Test Signals

Risks include buffer growth loops under persistent path errors, incorrect proc `/self` rewriting, missing trailing slash for directories, escaping mismatches with parser validation, and allocation failures under `GFP_NOFS`. Tests should cover procfs, anonymous pipes/sockets, device-backed and device-less filesystems, non-renamable filesystems, long paths, binary bytes, backslashes, and nofollow lookup failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/realpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/securityfs_if.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/securityfs_if.c

## Purpose

This file exposes TOMOYO's securityfs control interface under `/sys/kernel/security/tomoyo/` and implements the special `self_domain` file for reading or manually changing the current task's TOMOYO domain.

## Important APIs, types, and functions

The key externally used function is `tomoyo_interface_init()`, registered as TOMOYO's `initcall_fs`. File operation handlers include `tomoyo_write_self`, `tomoyo_read_self`, `tomoyo_open`, `tomoyo_release`, `tomoyo_poll`, `tomoyo_read`, and `tomoyo_write`. `tomoyo_check_task_acl()` validates manual domain transition ACLs. `tomoyo_create_entry()` creates typed securityfs files using `i_private` keys.

## Control Flow

`tomoyo_interface_init()` exits early if TOMOYO is disabled or not yet attached to the kernel domain. It creates the `tomoyo` securityfs directory, adds query, policy, audit, stat, profile, manager, version, process status, and `self_domain` files, then loads built-in policy. Generic file operations forward to TOMOYO control-buffer helpers. `tomoyo_write_self()` copies a user domain string, normalizes it, validates domain syntax, checks `task manual_domain_transition` permission under the read lock, assigns or finds the new domain, and swaps the current task's domain reference counts.

## State and Persistence

Securityfs dentries persist after initialization. Manual domain transitions mutate the current task's `tomoyo_task.domain_info` pointer and atomic user counts. Policy data and control buffer state are managed by common TOMOYO code; this file only routes file operations to it.

## Dependencies and Integration Points

It depends on Linux securityfs, TOMOYO control I/O helpers, domain assignment, request initialization, ACL checks, line normalization, and path/domain validators. The created files are the user-space policy management ABI.

## Risks and Test Signals

Risks include permissive `0666` `self_domain` relying entirely on TOMOYO ACL checks, partial read offsets, domain reference count imbalance, securityfs creation failures not being checked, and user input size handling. Tests should cover securityfs file presence, read/write behavior, invalid domains, denied and allowed manual transitions, concurrent transitions, and policy load ordering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/securityfs_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/tomoyo.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/tomoyo.c

## Purpose

This is TOMOYO's LSM registration and hook dispatch file. It maps kernel security hooks for exec, file, path, mount, socket, and task lifecycle operations into TOMOYO policy-checking helpers, and initializes TOMOYO task security blobs.

## Important APIs, types, and functions

Public state includes `tomoyo_blob_sizes`, `tomoyo_ss`, and `tomoyo_enabled`. `tomoyo_domain()` returns the current thread's domain and clears stale exec rollback state. Hook implementations include `tomoyo_cred_prepare`, `tomoyo_bprm_committed_creds`, `tomoyo_bprm_creds_for_exec`, `tomoyo_bprm_check_security`, many `tomoyo_path_*` wrappers, `tomoyo_file_open`, `tomoyo_file_fcntl`, `tomoyo_file_ioctl`, mount hooks, socket hook wrappers, `tomoyo_task_alloc`, and `tomoyo_task_free`.

## Control Flow

Initialization registers `tomoyo_hooks`, sets the initial task to `tomoyo_kernel_domain`, initializes memory management, and requests securityfs initialization through `initcall_fs`. Exec handling first loads policy when userspace loader support is enabled, then `tomoyo_bprm_check_security()` either finds the next domain for the initial exec check or checks interpreter read permission in the next domain. Path and file hooks build `struct path` wrappers around VFS arguments and call TOMOYO path, path-number, path2, mkdev, mount, or open helpers. Task allocation inherits the parent's domain and increments references; task free decrements active and saved exec domain references.

## State and Persistence

The task security blob stores `domain_info` and `old_domain_info`. `old_domain_info` persists across exec credential transitions so failed execs can roll back, then is cleared after committed credentials. The global SRCU `tomoyo_ss` protects policy traversal and GC. `tomoyo_enabled` is `__ro_after_init` and controlled by LSM setup.

## Dependencies and Integration Points

It integrates with the Linux LSM framework, task blob allocation, binprm lifecycle, VFS path hooks, socket hooks, mount hooks, TOMOYO policy helpers, and securityfs initialization. Network checks are delegated to `network.c`.

## Risks and Test Signals

Risks include reference count leaks around exec rollback, missing hook coverage for a sensitive operation, path construction using the wrong mount for link/rename, bypassing file-open checks for `__FMODE_EXEC`, and policy loader ordering. Tests should include exec success/failure/interpreter paths, domain inheritance through fork, path operation denial coverage, mount and pivotroot checks, socket hook dispatch, and module boot with TOMOYO enabled/disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/tomoyo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/util.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/util.c

## Purpose

This file contains TOMOYO's shared utility layer for policy parsing, path/domain validation, pattern matching, request initialization, mode lookup, time conversion, executable lookup, and learning-mode quota enforcement.

## Important APIs, types, and functions

Important exported helpers include `tomoyo_convert_time`, `tomoyo_permstr`, `tomoyo_read_token`, `tomoyo_get_domainname`, `tomoyo_parse_ulong`, `tomoyo_print_ulong`, `tomoyo_parse_name_union`, `tomoyo_parse_number_union`, `tomoyo_str_starts`, `tomoyo_normalize_line`, `tomoyo_correct_word`, `tomoyo_correct_path`, `tomoyo_correct_domain`, `tomoyo_domain_def`, `tomoyo_find_domain`, `tomoyo_fill_path_info`, `tomoyo_path_matches_pattern`, `tomoyo_get_exe`, `tomoyo_get_mode`, `tomoyo_init_request_info`, and `tomoyo_domain_quota_is_ok`. Global state includes `tomoyo_policy_lock`, `tomoyo_policy_loaded`, and `tomoyo_index2category`.

## Control Flow

Parsing helpers destructively tokenize policy lines, parse decimal/octal/hex values and ranges, and resolve `@` group references. Validation walks TOMOYO escape syntax, path requirements, domain names, recursion patterns, and character classes. Pattern matching first compares constant prefixes, then recursively handles component patterns, subtraction `\-`, repetition `\{...\}`, wildcards, byte escapes, and digit/hex/alpha classes. Request initialization chooses the active domain and computes mode from profile, category defaults, and global default. Quota checking counts effective ACL permission bits while tolerating races, then logs and flags the domain when learning-mode quota is exceeded.

## State and Persistence

`tomoyo_policy_lock` serializes policy mutations. `tomoyo_policy_loaded` gates enforcement modes so policy is disabled before load. Parsed path info stores hash, constant prefix length, directory flag, and patterned flag in caller-provided objects. Quota warnings persist in domain flags to avoid repeated learning-mode logs.

## Dependencies and Integration Points

It depends on TOMOYO domain, profile, group, ACL, logging, and path intern tables; on kernel hashing, time conversion, executable lookup, and character helpers; and on SRCU policy traversal. Most TOMOYO parsers and checkers depend on these utilities.

## Risks and Test Signals

Risks include parser mutation surprises, escape grammar drift, recursive pattern backtracking cost, race-tolerant quota counts, mode defaults masking policy expectations, and group reference lifetime handling. Tests should cover every escape form, invalid words/domains, numeric bases/ranges, pattern subtraction and repetition, directory-vs-file matching, profile inheritance, learning quota warnings, and current executable path lookup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/Kconfig -->
# sources/distributed-fs/ceph-client/security/yama/Kconfig

## Purpose

This Kconfig entry declares `SECURITY_YAMA`, the build option for the Yama Linux Security Module. Yama adds system-wide DAC-hardening controls, currently focused on ptrace restrictions, and is stackable with other LSMs.

## Important APIs, types, and functions

The file defines a single boolean config symbol, `SECURITY_YAMA`, depending on `SECURITY` and defaulting to `n`. Its help text points administrators to `Documentation/admin-guide/LSM/Yama.rst`.

## Control Flow

There is no runtime control flow. The Kconfig symbol controls whether `security/yama/Makefile` builds `yama.o` and whether Yama registration code is available to the LSM framework.

## State and Persistence

The selected value persists in the kernel `.config`. Runtime state such as `ptrace_scope` is implemented in `yama_lsm.c`, not here.

## Dependencies and Integration Points

It integrates with the kernel security menu and requires the general `SECURITY` infrastructure. It is consumed by the Yama Makefile.

## Risks and Test Signals

Risks are configuration-level: missing `SECURITY` disables Yama, and default `n` means it is absent unless selected. Test signals are Kconfig dependency checks and build matrix coverage with Yama enabled and disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/Makefile -->
# sources/distributed-fs/ceph-client/security/yama/Makefile

## Purpose

This Makefile builds the Yama LSM object when `CONFIG_SECURITY_YAMA` is enabled.

## Important APIs, types, and functions

It declares `obj-$(CONFIG_SECURITY_YAMA) := yama.o` and composes `yama-y := yama_lsm.o`.

## Control Flow

The Kbuild conditional includes or omits Yama based on the config symbol. There is no runtime logic.

## State and Persistence

No state is stored. The output is the linked `yama.o` built from `yama_lsm.o`.

## Dependencies and Integration Points

It depends on the Kconfig symbol from `Kconfig` and on `yama_lsm.c`. It integrates with the kernel security directory's recursive build.

## Risks and Test Signals

Risks are limited to build wiring. Tests should compile with `CONFIG_SECURITY_YAMA=y`, `m` if permitted by surrounding build rules, and `n` to verify no stale references.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/yama_lsm.c -->
# sources/distributed-fs/ceph-client/security/yama/yama_lsm.c

## Purpose

This file implements the Yama LSM's ptrace hardening policy. It restricts `PTRACE_ATTACH`, `PTRACE_TRACEME`, and related ptrace-like access according to `/proc/sys/kernel/yama/ptrace_scope`, while allowing explicit tracee-selected exceptions through `PR_SET_PTRACER`.

## Important APIs, types, and functions

The main state is `ptrace_scope`, `ptracer_relations`, and `ptracer_relations_lock`. `struct ptrace_relation` records one tracee's allowed tracer ancestor and an invalidation flag. Key functions are `yama_task_prctl`, `yama_ptracer_add`, `yama_ptracer_del`, `yama_relation_cleanup`, `task_is_descendant`, `ptracer_exception_found`, `yama_ptrace_access_check`, `yama_ptrace_traceme`, `yama_dointvec_minmax`, `yama_init_sysctl`, and `yama_init`. LSM hooks are ptrace access, ptrace traceme, task prctl, and task free.

## Control Flow

`PR_SET_PTRACER` records, replaces, clears, or broadens a tracee exception at process-group granularity. Ptrace attach checks consult `ptrace_scope`: disabled allows normal DAC, relational requires target to be a descendant, an explicit exception, or CAP_SYS_PTRACE in the target user namespace, capability mode requires CAP_SYS_PTRACE, and no-attach denies all attaches. `PTRACE_TRACEME` is denied in capability/no-attach modes unless the parent has the needed capability. Denials are reported through deferred task work when command-line access can sleep.

## State and Persistence

Ptracer exceptions live in an RCU-protected list. Task exit marks related relations invalid and schedules work to remove and free them with `kfree_rcu`. `ptrace_scope` persists as a sysctl value during runtime; once set to maximum scope, the sysctl handler locks the minimum to the maximum so it cannot be reduced.

## Dependencies and Integration Points

It depends on LSM hooks, sysctl, ptrace, prctl constants, RCU, spinlocks, task work, task lifetime helpers, user namespace capability checks, and ratelimited logging. It registers with `DEFINE_LSM(yama)`.

## Risks and Test Signals

Risks include stale task pointers in exception records, lock ordering around task locks and RCU, namespace capability semantics, one-exception-per-tracee replacement behavior, and irreversible max-scope sysctl behavior. Tests should cover all `ptrace_scope` values, `PR_SET_PTRACER` pid/ANY/clear flows, task exit cleanup, namespace capability cases, `PTRACE_MODE_NOAUDIT`, and concurrent prctl/exit/attach races.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/yama/yama_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/Kconfig -->
# sources/distributed-fs/ceph-client/sound/Kconfig

## Purpose

This top-level sound Kconfig file declares legacy sound support, OSS compatibility controls, ALSA, all ALSA child driver menus, and the generic legacy `AC97_BUS` symbol that can be selected by non-sound drivers sharing AC97 hardware.

## Important APIs, types, and functions

Important symbols are `SOUND`, `SOUND_OSS_CORE`, `SOUND_OSS_CORE_PRECLAIM`, `SND`, and `AC97_BUS`. The file sources Kconfig files for sound core, drivers, ISA, PCI, HDA, PowerPC, AC97, AOA, ARM, USB, FireWire, SoC, virtio, and other platform-specific sound trees.

## Control Flow

Kconfig nesting gates OSS and ALSA options under `SOUND`; ALSA submenus appear only under `SND`. `AC97_BUS` is outside the `SOUND` block so it remains buildable without the full sound subsystem.

## State and Persistence

Selected config values persist in `.config` and control compiled sound subsystems. There is no runtime state.

## Dependencies and Integration Points

It integrates with the kernel configuration system and the top-level sound Makefile. AC97 and AOA files researched in this item are sourced from here.

## Risks and Test Signals

Risks include dependency ordering for bus-specific Kconfig files, misplaced options causing missing symbols, and AC97 buildability when sound is disabled. Test signals are `allyesconfig`, `allmodconfig`, and minimal configs selecting only `AC97_BUS`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/Makefile -->
# sources/distributed-fs/ceph-client/sound/Makefile

## Purpose

This top-level sound Makefile wires configured sound subsystems into the kernel build, including soundcore, ALSA directories, Apple Onboard Audio, and both old and new AC97 bus implementations.

## Important APIs, types, and functions

The important Kbuild variables are `obj-$(CONFIG_SOUND)`, `obj-$(CONFIG_DMASOUND)`, `obj-$(CONFIG_SND)`, `obj-$(CONFIG_SND_AOA)`, `obj-$(CONFIG_AC97_BUS)`, `obj-$(CONFIG_AC97_BUS_NEW)`, and `soundcore-y`.

## Control Flow

Kbuild conditionals include directory subtrees or objects according to `.config`. `last.o` is added only when `CONFIG_SND=y`, preserving ALSA link ordering.

## State and Persistence

No runtime state exists. Build output depends on selected config symbols.

## Dependencies and Integration Points

It integrates Kconfig selections with directory recursion. It intentionally allows `ac97_bus.o` to build even when sound is otherwise disabled.

## Risks and Test Signals

Risks include link-order regressions, missing subdirectory inclusion for enabled drivers, and AC97 dependency mistakes. Build tests with sound disabled but AC97 enabled, ALSA built-in, ALSA modular, and AOA enabled are useful.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/Kconfig -->
# sources/distributed-fs/ceph-client/sound/ac97/Kconfig

## Purpose

This file declares the newer AC97 bus Kconfig symbols used by drivers that want automatic AC97 codec probing and optional compatibility with older `struct snd_ac97` users.

## Important APIs, types, and functions

It defines `AC97_BUS_NEW` as a tristate bus type and `AC97_BUS_COMPAT` as a bool depending on `AC97_BUS_NEW` and `!AC97_BUS`.

## Control Flow

Drivers select `AC97_BUS_NEW` when they need the new AC97 controller/codec bus. `AC97_BUS_COMPAT` enables the compatibility object only when the legacy AC97 bus is not separately selected.

## State and Persistence

Configuration choices persist in `.config`; runtime bus state is implemented by `bus.c`.

## Dependencies and Integration Points

It is sourced from the top-level sound Kconfig and consumed by `sound/ac97/Makefile`.

## Risks and Test Signals

Risks include selecting both legacy and compat paths at once, or missing compat support for old SoC codecs. Build tests should exercise `AC97_BUS_NEW` with and without `AC97_BUS_COMPAT`, and combinations with legacy `AC97_BUS`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/Makefile -->
# sources/distributed-fs/ceph-client/sound/ac97/Makefile

## Purpose

This Makefile builds the new AC97 bus module and optionally includes the compatibility layer.

## Important APIs, types, and functions

It defines `obj-$(CONFIG_AC97_BUS_NEW) += ac97.o`, `ac97-y += bus.o codec.o`, and `ac97-$(CONFIG_AC97_BUS_COMPAT) += snd_ac97_compat.o`.

## Control Flow

Kbuild composes `ac97.o` from the core bus and codec compilation units, adding `snd_ac97_compat.o` only when enabled.

## State and Persistence

No runtime state exists here. It controls object composition.

## Dependencies and Integration Points

It consumes `AC97_BUS_NEW` and `AC97_BUS_COMPAT` from Kconfig and builds the files that export new AC97 controller and codec-driver APIs.

## Risks and Test Signals

Risks are build-level: missing compat object when needed or duplicate reset symbols when legacy AC97 is enabled. Test by compiling all intended AC97 config combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/ac97_core.h -->
# sources/distributed-fs/ceph-client/sound/ac97/ac97_core.h

## Purpose

This private header shares minimal helpers between the new AC97 bus core and compatibility layer.

## Important APIs, types, and functions

It declares `snd_ac97_bus_scan_one()` and defines `ac97_ids_match(id1, id2, mask)`, which compares two vendor IDs under a mask.

## Control Flow

There is no complex control flow. The inline helper performs a masked equality check; the scan declaration is implemented in `bus.c`.

## State and Persistence

No state is stored.

## Dependencies and Integration Points

It integrates `bus.c` with `snd_ac97_compat.c`, letting compatibility reset code reuse new-bus scanning and ID matching.

## Risks and Test Signals

Risks include mask direction mistakes and mismatched declarations if scan semantics change. Tests should check exact, masked, invalid, and zero vendor ID reset cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/ac97_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/bus.c -->
# sources/distributed-fs/ceph-client/sound/ac97/bus.c

## Purpose

This file implements the new AC97 controller/codec bus. It lets digital controllers register available codec slots, scans AC97 vendor IDs, creates codec devices, matches codec drivers by ID table, exposes reset operations through sysfs, and handles runtime PM and codec clocks.

## Important APIs, types, and functions

Public exports include `snd_ac97_codec_driver_register`, `snd_ac97_codec_driver_unregister`, `snd_ac97_codec_get_platdata`, `snd_ac97_controller_register`, `snd_ac97_controller_unregister`, `snd_ac97_bus_scan_one`, and `ac97_bus_type`. Internal state includes `ac97_controllers_mutex`, `ac97_adapter_idr`, and `ac97_controllers`. Important callbacks include `ac97_codec_release`, `ac97_codec_add`, `ac97_bus_scan`, `cold_reset_store`, `warm_reset_store`, `ac97_add_adapter`, `ac97_del_adapter`, `ac97_pm_runtime_suspend`, `ac97_pm_runtime_resume`, `ac97_bus_match`, `ac97_bus_probe`, and `ac97_bus_remove`.

## Control Flow

A controller registration allocates an `ac97_controller`, copies optional per-codec platform data, registers an adapter device, resets the bus, and scans available slots. Scanning reads vendor ID registers through controller ops and creates `ac97_codec_device` children. Driver matching rejects invalid IDs and walks the codec driver's ID table with masked comparisons. Probe enables an `ac97_clk`, activates runtime PM, and invokes the codec driver's probe; failure unwinds PM and clock state. Removal resumes the device, calls driver remove, disables the clock, and disables runtime PM.

## State and Persistence

Controllers are tracked in an IDR and global list under a mutex. Each controller owns codec pointers by slot, platform data, parent device, adapter device, and ops. Codec devices persist in the driver model until unregistered; device release clears the controller slot and frees OF node references. Runtime PM and clock state are tied to bound codec devices.

## Dependencies and Integration Points

It depends on Linux driver core, OF child matching, IDR, mutexes, clocks, PM runtime, sysfs attributes, and AC97 public headers. Controller drivers call the exported register API; codec drivers register on `ac97_bus_type`.

## Risks and Test Signals

Risks include controller lifetime races with codec devices, sysfs reset while drivers are active, missing controller ops checks, clock/PM imbalance on probe/remove errors, OF child compatibility matching errors, and ignored `ac97_bus_scan()` return from registration. Tests should cover multi-slot probing, invalid IDs, masked driver matching, probe failure unwind, runtime suspend/resume, controller unregister with bound codecs, and sysfs reset paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/codec.c -->
# sources/distributed-fs/ceph-client/sound/ac97/codec.c

## Purpose

This is a stub compilation unit for the new AC97 bus codec side. It currently only includes the relevant AC97, driver-core, allocation, and SoC compatibility headers.

## Important APIs, types, and functions

No functions or data are defined in this file. Its presence lets `ac97.o` reserve a separate codec compilation unit for future or configuration-dependent codec-side code.

## Control Flow

There is no runtime control flow.

## State and Persistence

No state is stored.

## Dependencies and Integration Points

The includes connect it to `<sound/ac97_codec.h>`, `<sound/ac97/codec.h>`, `<sound/ac97/controller.h>`, Linux device/slab APIs, and `<sound/soc.h>`.

## Risks and Test Signals

Risks are minimal, but stale empty objects can hide missing implementation expectations. Build tests should ensure `ac97.o` links cleanly and no symbols are expected from this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/snd_ac97_compat.c -->
# sources/distributed-fs/ceph-client/sound/ac97/snd_ac97_compat.c

## Purpose

This file provides a compatibility wrapper that exposes a legacy `struct snd_ac97` object on top of a new `ac97_codec_device`, allowing older AC97/ASoC code paths to use new AC97 controller operations.

## Important APIs, types, and functions

Public exports are `snd_ac97_compat_alloc`, `snd_ac97_compat_release`, and a compatibility implementation of `snd_ac97_reset`. Internal bus ops are `compat_ac97_reset`, `compat_ac97_warm_reset`, `compat_ac97_write`, and `compat_ac97_read`, collected in `compat_snd_ac97_bus_ops` and `compat_soc_ac97_bus`.

## Control Flow

Allocation creates a zeroed `snd_ac97`, points private data at the new codec device, assigns a synthetic legacy AC97 bus, initializes a child device named with `-compat`, and registers it. Legacy read/write/reset callbacks translate through `adev->ac97_ctrl->ops`. Reset optionally tries warm reset first, rescans the slot via `snd_ac97_bus_scan_one()`, and accepts success if the scanned ID matches the codec vendor ID under the supplied mask; otherwise it performs cold plus warm reset and repeats the scan.

## State and Persistence

The compatibility `snd_ac97` persists as a registered child device until `snd_ac97_compat_release()`. It does not own the underlying controller or codec device; it stores the pointer in `private_data`.

## Dependencies and Integration Points

It depends on the new AC97 bus controller structures, legacy `<sound/ac97_codec.h>` semantics, ASoC AC97 callbacks, and the private `ac97_core.h` scan and ID helper. It is only built when `CONFIG_AC97_BUS_COMPAT` is enabled.

## Risks and Test Signals

Risks include lifetime mismatch between compat objects and underlying codec devices, missing controller ops, reset ID comparisons ignoring the `id` argument and using `adev->vendor_id`, and duplicate `snd_ac97_reset` when legacy AC97 is also built. Tests should cover allocation failure unwind, device release, warm reset success, cold reset success, masked ID mismatch, and controller unregister while compat objects exist.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97/snd_ac97_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97_bus.c -->
# sources/distributed-fs/ceph-client/sound/ac97_bus.c

## Purpose

This file implements the legacy AC97 bus interface: a simple driver-model bus type and a reset helper for old `struct snd_ac97` users.

## Important APIs, types, and functions

Public exports are `snd_ac97_reset` and `ac97_bus_type`. Internal `snd_ac97_check_id()` reads vendor ID registers and validates them against an optional expected ID and mask. Module init and exit register and unregister the bus.

## Control Flow

`snd_ac97_reset()` optionally performs a warm reset, checks the vendor ID, and returns `1` if warm reset was enough. Otherwise it performs cold reset if available, then warm reset if available, checks the vendor ID again, and returns `0` on success or `-ENODEV` on mismatch. Bus registration happens at `subsys_initcall`.

## State and Persistence

The only persistent state is the globally exported `ac97_bus_type`. Individual `snd_ac97` state is owned by callers and updated with the read vendor ID.

## Dependencies and Integration Points

It depends on legacy `<sound/ac97_codec.h>`, driver core bus registration, and AC97 bus ops supplied by controller drivers. It is selected by the top-level sound Makefile through `CONFIG_AC97_BUS`.

## Risks and Test Signals

Risks include invalid vendor ID handling, optional reset callbacks being NULL, and symbol conflicts with new-bus compatibility. Tests should cover reset paths with warm-only success, cold fallback, missing callbacks, invalid IDs, and masked expected IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ac97_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/Kconfig -->
# sources/distributed-fs/ceph-client/sound/aoa/Kconfig

## Purpose

This file declares the Apple Onboard Audio top-level config menu and sources fabric, codec, and soundbus submenus.

## Important APIs, types, and functions

It defines `SND_AOA`, a tristate option depending on `PPC_PMAC` and selecting `SND_PCM`.

## Control Flow

When `SND_AOA` is enabled, Kconfig sources `sound/aoa/fabrics/Kconfig`, `sound/aoa/codecs/Kconfig`, and `sound/aoa/soundbus/Kconfig`.

## State and Persistence

The config selection persists in `.config`. Runtime AOA state is implemented in the subdirectories.

## Dependencies and Integration Points

It integrates AOA with ALSA and PowerMac platform support. It is consumed by `sound/aoa/Makefile`.

## Risks and Test Signals

Risks include exposing AOA on unsupported architectures or missing PCM dependency selection. Build tests should cover PowerMac configs with AOA built-in and modular, plus non-PowerMac configs where it is unavailable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/Makefile

## Purpose

This Makefile recurses into Apple Onboard Audio core, soundbus, fabrics, and codec subdirectories according to config selections.

## Important APIs, types, and functions

It adds `core/`, `soundbus/`, `fabrics/`, and `codecs/` through `obj-$(CONFIG_SND_AOA)` and `obj-$(CONFIG_SND_AOA_SOUNDBUS)`.

## Control Flow

Kbuild includes the core, fabric, and codec pieces when AOA is enabled, and includes the soundbus layer when its config is enabled.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is driven by the AOA Kconfig symbols and feeds Kbuild recursion for all AOA files researched here.

## Risks and Test Signals

Risks include missing soundbus recursion for fabric dependencies and incorrect built-in/module ordering. Build tests should cover AOA with and without soundbus and each codec/fabric as modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/aoa-gpio.h -->
# sources/distributed-fs/ceph-client/sound/aoa/aoa-gpio.h

## Purpose

This header defines the GPIO abstraction used by Apple Onboard Audio fabrics and codecs to control amplifiers, mute lines, reset pins, and jack-detect notifications independent of the underlying PMF or direct feature-call implementation.

## Important APIs, types, and functions

It defines `notify_func_t`, `enum notify_type`, `struct gpio_methods`, `struct gpio_notification`, and `struct gpio_runtime`. `gpio_methods` covers init/exit, all-amp muting/restoring, headphone/speaker/lineout/master switching, get methods, hardware reset, notification registration, and detect-state reads.

## Control Flow

There is no executable logic. Runtime code fills a `gpio_runtime` with a `gpio_methods` implementation and calls through function pointers. Notifications are represented as delayed work plus callback data and a mutex.

## State and Persistence

`gpio_runtime` stores the selected device node, methods, implementation-private bitfield, and notification records. Implementations persist callback registrations and detect IRQ state.

## Dependencies and Integration Points

It depends on Linux workqueues and mutexes. It is used by AOA core, layout fabric, PMF GPIO, feature-call GPIO, and codec reset/clock-switch code.

## Risks and Test Signals

Risks include NULL method calls, callback lifetime after fabric removal, inconsistent implementation-private bit meanings, and detect notification races. Tests should exercise PMF and feature GPIO implementations, callback register/unregister, amp restore state, and suspend/remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/aoa-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/aoa.h -->
# sources/distributed-fs/ceph-client/sound/aoa/aoa.h

## Purpose

This is the central Apple Onboard Audio public header. It defines the codec/fabric registration contracts, shared ALSA helper entry points, and exported GPIO method providers.

## Important APIs, types, and functions

Key types are `struct aoa_codec`, `struct aoa_fabric`, and `struct aoa_card`. Important APIs are `aoa_codec_register`, `aoa_codec_unregister`, `aoa_fabric_register`, `aoa_fabric_unregister`, `aoa_fabric_unlink_codec`, `aoa_snd_device_new`, `aoa_get_card`, and `aoa_snd_ctl_add`. It also declares `pmf_gpio_methods` and `ftr_gpio_methods`.

## Control Flow

The header specifies that codecs register independently, a fabric later claims codecs through `found_codec`, fills soundbus/GPIO/connection fields, calls codec `init`, and then receives `attached_codec`. Removal flows through codec `exit` and fabric `remove_codec`.

## State and Persistence

`aoa_codec` instances store codec name, owner, OF node, assigned soundbus device, GPIO runtime, connection bitmask, fabric data, list linkage, and fabric pointer. `aoa_fabric` stores callbacks and module ownership. `aoa_card` wraps one ALSA card.

## Dependencies and Integration Points

It depends on ALSA core/control headers, modules, AOA GPIO, and soundbus definitions. Codecs, core, fabric, and soundbus all share this contract.

## Risks and Test Signals

Risks include single-card/single-fabric assumptions, module reference imbalance, codec fields being used before fabric assignment, and connection bit meanings differing by codec. Tests should cover codec-before-fabric and fabric-before-codec registration, unregister ordering, and multiple codec layouts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/aoa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/Kconfig -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/Kconfig

## Purpose

This file declares Apple Onboard Audio codec driver options for Onyx, TAS, and Toonie chips.

## Important APIs, types, and functions

It defines `SND_AOA_ONYX`, `SND_AOA_TAS`, and `SND_AOA_TOONIE`. Onyx and TAS select `I2C` and `I2C_POWERMAC`; Toonie has no I2C dependency because it is a simple DAC codec wrapper.

## Control Flow

Kconfig selections control whether the matching codec modules are built and can be auto-requested by layout fabric.

## State and Persistence

Selected symbols persist in `.config`. Runtime codec state is in the `.c` files.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the codecs Makefile. The layout fabric requests modules named `snd-aoa-codec-*`.

## Risks and Test Signals

Risks include missing I2C dependencies and fabric requesting unavailable codec modules. Build tests should compile each codec alone and in combination with the layout fabric.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/Makefile

## Purpose

This Makefile builds the AOA codec modules for Onyx, TAS, and Toonie.

## Important APIs, types, and functions

It maps `snd-aoa-codec-onyx-y := onyx.o`, `snd-aoa-codec-tas-y := tas.o`, and `snd-aoa-codec-toonie-y := toonie.o`, then adds each object according to its config symbol.

## Control Flow

Kbuild conditionally builds codec modules when selected in Kconfig.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is consumed by AOA directory recursion and produces module names that layout fabric can request.

## Risks and Test Signals

Risks are build-wiring issues. Tests should build each codec as module and built-in, verifying module aliases and request_module names line up.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.c -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.c

## Purpose

This file implements the Apple Onboard Audio Onyx/PCM3052 codec driver. It registers as an I2C driver, exposes an `aoa_codec`, initializes the codec registers, creates ALSA mixer and IEC958 controls based on connected endpoints, and attaches PCM capabilities to an AOA soundbus device.

## Important APIs, types, and functions

The core state is `struct onyx`, containing a write-only register cache, I2C client, AOA codec, initialization and lock flags, open count, optional codec info copy, and mutex. Important functions include `onyx_read_register`, `onyx_write_register`, mixer callbacks for volume/input gain/capture/mute/single-bit/SPDIF controls, `onyx_set_spdif_pcm_rate`, `onyx_register_init`, `onyx_usable`, `onyx_prepare`, `onyx_open`, `onyx_close`, `onyx_switch_clock`, PM suspend/resume callbacks, `onyx_init_codec`, `onyx_exit_codec`, `onyx_i2c_probe`, and `onyx_i2c_remove`.

## Control Flow

I2C probe allocates state, reads the control register to verify hardware, fills codec callbacks, and registers with AOA core. Fabric attachment calls `onyx_init_codec()`, which resets hardware through GPIO, initializes cached registers, creates an ALSA codec device, tailors transfer capabilities for connected inputs/outputs, attaches to soundbus, and adds ALSA controls. Runtime ALSA callbacks lock the mutex, read from cache or hardware, validate ranges, and write I2C registers. PCM prepare locks or disables S/PDIF or analog paths depending on format/rate; close unlocks when the last stream closes.

## State and Persistence

Write-only registers 65-80 are cached in `onyx->cache`. ALSA controls persist on the single AOA card. `spdif_locked`, `analog_locked`, and `open_count` persist across stream lifetime. PM resume restores registers from cache after GPIO reset. The codec node reference is held from probe to remove.

## Dependencies and Integration Points

It depends on I2C SMBus, OF nodes, ALSA controls, IEC958 constants, AOA core helpers, soundbus attach/detach, and fabric-provided GPIO. The layout fabric assigns `connected`, GPIO, and soundbus fields before init.

## Risks and Test Signals

Risks include cache desynchronization for write-only registers, I2C errors ignored by some setters, ALSA controls created without full rollback on partial failure, single-card assumptions, lock flags leaving controls busy, and rate-dependent S/PDIF disable behavior. Tests should cover probe/remove, register init, all mixer controls, S/PDIF status/rate controls, connected-bit permutations, PM suspend/resume, PCM open/prepare/close, and error unwinds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.h -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.h

## Purpose

This header defines PCM3052/Onyx register numbers and bit masks used by the Onyx codec driver.

## Important APIs, types, and functions

It defines registers for DAC attenuation, control, DAC control, deemphasis, filter, output phase, ADC control, ADC high-pass bypass, and digital info bytes. Bit definitions include reset, suspend, mute, S/PDIF enable, word length, input selection, gain mask, and channel status masks. `FIRSTREGISTER` anchors the cache index.

## Control Flow

There is no executable logic. The macros are consumed by `onyx.c`.

## State and Persistence

The macro layout determines the size and indexing of the Onyx register cache in `struct onyx`.

## Dependencies and Integration Points

It includes I2C and PowerMac low-I2C headers and is private to the Onyx driver.

## Risks and Test Signals

Risks include wrong register offsets corrupting cache writes, bit-mask mistakes for mute/SPDIF/status, and cache indexing outside the 65-80 range. Tests should validate register writes from mixer callbacks against expected addresses and masks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-basstreble.h -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-basstreble.h

## Purpose

This header provides TAS3004 bass and treble lookup tables used by the TAS codec driver to convert ALSA control indices into hardware tone-control values.

## Important APIs, types, and functions

It defines min, max, and zero constants for treble and bass, `tas3004_treble_table`, `tas3004_bass_diff_to_treble`, and inline helpers `tas3004_treble()` and `tas3004_bass()`.

## Control Flow

The treble helper directly indexes the table. The bass helper starts from the treble table and adds a compact difference table for indices 50 and above.

## State and Persistence

The lookup arrays are static const data included exactly once by `tas.c`. They encode datasheet-derived tone curves.

## Dependencies and Integration Points

It depends on kernel integer types from the includer. `tas.c` uses these helpers in tone setter callbacks and reset initialization.

## Risks and Test Signals

Risks include out-of-range indices if ALSA validation changes, table/data-sheet mismatches, and the compact bass delta hiding off-by-one errors. Tests should verify min/max/zero controls and expected hardware values at low, zero, and high tone settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-basstreble.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-gain-table.h -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-gain-table.h

## Purpose

This header embeds the TAS gain table used to map user-visible half-dB volume and mixer indices to fixed-point hardware gain values.

## Important APIs, types, and functions

The main artifact is `static const int tas_gaintable[]`, with entries from mute/negative infinity through -70.0 dB to +18.0 dB. A commented C/math generator documents the formula used to create the table.

## Control Flow

There is no executable runtime logic except array indexing by `tas.c`. Volume code converts each integer entry into three bytes for TAS volume or mixer registers.

## State and Persistence

The static const table persists in the driver image. It is included exactly once.

## Dependencies and Integration Points

It is included by `tas.c`, which clamps indices to 177 before indexing. It relies on the includer for C type definitions.

## Risks and Test Signals

Risks include index/value mismatch, integer truncation differences from the documented generator, and out-of-range indexing if callers fail validation. Tests should check representative indices, mute, 0 dB, maximum gain, and mixer/volume byte packing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-gain-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.c -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.c

## Purpose

This file implements the Apple Onboard Audio TAS3004 codec driver. It registers an I2C codec, manages TAS hardware reset and register programming, exposes ALSA controls for volume, mute, mixer, dynamic range compression, capture source, treble, and bass, and attaches PCM capabilities to a soundbus device.

## Important APIs, types, and functions

State lives in `struct tas`: AOA codec, I2C client, mute/control/DRC/hardware flags, cached volume, mixer arrays, tone values, analog control register, DRC range, and mutex. Important functions are `tas_write_reg`, `tas3004_set_drc`, `tas_set_treble`, `tas_set_bass`, `tas_set_volume`, `tas_set_mixer`, ALSA control callbacks, `tas_reset_init`, `tas_switch_clock`, PM suspend/resume wrappers, `tas_init_codec`, `tas_exit_codec`, `tas_i2c_probe`, and `tas_i2c_remove`.

## Control Flow

I2C probe allocates and initializes software state, sets default DRC range, fills codec callbacks, and registers with AOA. Fabric init calls `tas_init_codec()`, which resets via GPIO, programs main control, analog power-down/up, DRC, tone, and then attaches to soundbus and creates ALSA controls. Control callbacks update cached software state under the mutex and write hardware only if `hw_enabled`. Clock switch prepare mutes amps and marks hardware disabled; clock restore resets hardware and reapplies cached volume/mixer state.

## State and Persistence

Unlike Onyx, TAS state is mostly software-cached control state rather than register cache. `hw_enabled` gates writes across clock transitions and suspend. `acr`, DRC, volume, mixer, bass, treble, and mute state persist across reinitialization and are replayed on resume or clock restore.

## Dependencies and Integration Points

It depends on I2C SMBus block writes, OF, AOA core, ALSA controls, soundbus attachment, fabric-provided GPIO, and TAS lookup headers. The layout fabric supplies connection data, but this driver notes it does not fully honor `aoa_codec.connected`.

## Risks and Test Signals

Risks include controls not reflecting actual hardware when disconnected endpoints exist, out-of-range mixer writes because mixer put lacks explicit range validation, partial control creation unwind, I2C write errors being ignored in setters, mono microphone assumptions, and reset timing sensitivity. Tests should cover probe/remove, all ALSA controls, cached state replay after clock switch and PM resume, DRC limits, capture source bits, and hardware absent/I2C failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.h -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.h

## Purpose

This header defines TAS3004 register addresses, bit fields, and DRC limits used by the TAS codec driver.

## Important APIs, types, and functions

It defines main control, DRC, volume, treble, bass, left/right mixer, analog control, main control 2, biquad/loudness registers, and `TAS3001_DRC_MAX`/`TAS3004_DRC_MAX`. Bit fields cover serial clock, sport mode, word length, mono/input selection, deemphasis, analog power down, and all-pass.

## Control Flow

There is no executable logic. Macros are consumed by `tas.c`.

## State and Persistence

The values determine TAS register programming and cached `acr` semantics.

## Dependencies and Integration Points

It is private to the TAS driver and included by `tas.c`.

## Risks and Test Signals

Risks include wrong bit shifts or register constants causing hardware misconfiguration. Tests should validate reset-init register writes and ALSA control writes against expected register/value pairs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/toonie.c -->
# sources/distributed-fs/ceph-client/sound/aoa/codecs/toonie.c

## Purpose

This file implements the simple Toonie codec driver used on Mac Mini hardware. Toonie is treated as an analog-output-only DAC with no I2C register programming.

## Important APIs, types, and functions

State is a single global `struct toonie *toonie` containing an `aoa_codec`. Important functions are `toonie_init_codec`, `toonie_exit_codec`, `toonie_usable`, optional PM no-op callbacks, module `toonie_init`, and `toonie_exit`. `toonie_transfers` advertises big-endian 16/24-bit output rates from 32 kHz through 96 kHz.

## Control Flow

Module init allocates the codec, fills name/owner/init/exit, and registers with AOA. Fabric init requires `connected == 1`, creates an ALSA codec device, and attaches to the soundbus. Exit detaches the soundbus codec; module exit unregisters and frees the singleton.

## State and Persistence

The singleton codec persists for the module lifetime. There is no hardware register cache or mutable control state.

## Dependencies and Integration Points

It depends on AOA core, ALSA device helpers, and soundbus attach/detach. The layout fabric sets `connected` and soundbus fields for supported Mac Mini layouts.

## Risks and Test Signals

Risks include singleton assumptions, no controls for mute/power, and strict connected-bit matching. Tests should cover registration before/after fabric, attach/detach, unsupported connection masks, and PCM capability exposure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/codecs/toonie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/core/Makefile

## Purpose

This Makefile builds the AOA core module that contains codec/fabric coordination, ALSA helper functions, and GPIO implementations.

## Important APIs, types, and functions

It adds `snd-aoa.o` under `CONFIG_SND_AOA` and composes it from `core.o`, `alsa.o`, `gpio-pmf.o`, and `gpio-feature.o`.

## Control Flow

Kbuild links the core pieces into one module or built-in object when AOA is enabled.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is controlled by AOA Kconfig and provides exported symbols consumed by codecs and fabrics.

## Risks and Test Signals

Risks include missing GPIO implementation objects or link-order issues. Build tests should enable AOA core with PMF and feature GPIO users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/alsa.c -->
# sources/distributed-fs/ceph-client/sound/aoa/core/alsa.c

## Purpose

This file manages the single ALSA card used by Apple Onboard Audio and provides helper wrappers for codec/fabric code to create ALSA devices and controls.

## Important APIs, types, and functions

Public APIs are `aoa_alsa_init`, `aoa_get_card`, `aoa_alsa_cleanup`, `aoa_snd_device_new`, and `aoa_snd_ctl_add`. Module parameter `index` controls ALSA card index. Static `aoa_card` stores the active card wrapper.

## Control Flow

`aoa_alsa_init()` rejects a second card, allocates an ALSA card with private `aoa_card`, fills names, registers the card, and unwinds on failure. Device creation gets the current card, calls `snd_device_new`, immediately registers the device, and frees it if registration fails. Control addition forwards to `snd_ctl_add`.

## State and Persistence

`aoa_card` is a singleton global. The ALSA card persists until `aoa_alsa_cleanup()` frees it and clears the pointer.

## Dependencies and Integration Points

It depends on ALSA core device/control APIs and is called from AOA fabric registration and codec init paths through `aoa.h`.

## Risks and Test Signals

Risks include the single-card assumption, immediate device registration ordering, NULL card failures reported as `-ENOMEM`, and controls not being freed on later codec errors. Tests should cover init/cleanup, duplicate init, device/control failure unwinds, and codec registration before card creation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/alsa.h -->
# sources/distributed-fs/ceph-client/sound/aoa/core/alsa.h

## Purpose

This private header declares AOA ALSA card initialization and cleanup helpers for the core.

## Important APIs, types, and functions

It declares `aoa_alsa_init(char *name, struct module *mod, struct device *dev)` and `aoa_alsa_cleanup()`.

## Control Flow

There is no executable logic.

## State and Persistence

No state is stored in the header. The implementation's singleton state is in `alsa.c`.

## Dependencies and Integration Points

It includes `../aoa.h` and is used by `core.c` and `alsa.c`.

## Risks and Test Signals

Risks are limited to prototype drift. Build tests catch mismatches between declarations and implementation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/alsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/core.c -->
# sources/distributed-fs/ceph-client/sound/aoa/core/core.c

## Purpose

This file coordinates AOA codec and fabric registration. It enforces the single-fabric model, keeps the global codec list, attaches codecs to the active fabric, and manages module references and ALSA card lifetime.

## Important APIs, types, and functions

Public exports are `aoa_codec_register`, `aoa_codec_unregister`, `aoa_fabric_register`, `aoa_fabric_unregister`, and `aoa_fabric_unlink_codec`. Internal state is `fabric` and `codec_list`. `attach_codec_to_fabric()` is the core attach sequence.

## Control Flow

When a codec registers, it is attached immediately if a fabric exists, then added to the list. Fabric registration creates the ALSA card, stores the fabric, and walks existing codecs for attachment. Attachment gets the codec module, calls fabric `found_codec`, sets `c->fabric`, calls codec `init`, and notifies `attached_codec`. Failures call fabric `remove_codec` and release the module reference. Fabric unregister unlinks all attached codecs and cleans up the ALSA card.

## State and Persistence

The global fabric pointer and codec list persist for module lifetime. Codec structs are owned by codec drivers. Module references are held while codecs are attached to a fabric.

## Dependencies and Integration Points

It depends on AOA header contracts and ALSA helper initialization. Codecs and fabrics use these exported functions to rendezvous.

## Risks and Test Signals

Risks include no explicit locking around `codec_list` and `fabric`, module_put on unregister paths for codecs never attached, attach failure ordering, and single-fabric/card limitations. Tests should cover codec/fabric registration order, attach failures, unregister ordering, and repeated fabric registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/gpio-feature.c -->
# sources/distributed-fs/ceph-client/sound/aoa/core/gpio-feature.c

## Purpose

This file implements AOA GPIO methods using direct PowerMac feature calls to GPIO registers. It controls mute/reset GPIOs, reads jack-detect GPIOs, maps IRQs, and schedules process-context notifications.

## Important APIs, types, and functions

The exported provider is `ftr_gpio_methods`. Key helpers are `get_gpio`, `get_irq`, generated `ftr_gpio_set_*`/`get_*` methods, `ftr_gpio_set_hw_reset`, `ftr_gpio_all_amps_off`, `ftr_gpio_all_amps_restore`, `ftr_handle_notify`, `gpio_enable_dual_edge`, `ftr_gpio_init`, `ftr_gpio_exit`, `ftr_handle_notify_irq`, `ftr_set_notify`, and `ftr_get_detect`. Static globals store GPIO numbers, active states, OF nodes, and IRQ numbers.

## Control Flow

Initialization discovers named GPIO nodes or `audio-gpio` properties, normalizes register offsets, reads active-state properties, enables dual-edge detection, maps IRQs, turns amps off, and initializes delayed work and mutexes. Setters read the GPIO register, update output-enable/output bits according to active state, write the register, and update `implementation_private`. Notification registration serializes per notification, allocates or frees IRQ handlers, and schedules delayed work from IRQ context. Exit unregisters IRQs, cancels work, destroys mutexes, and mutes amps.

## State and Persistence

This implementation uses many file-global GPIO numbers and node pointers, so it effectively supports one active hardware layout. Per-runtime state in `implementation_private` tracks logical amp states for restore. Notification callbacks persist in `gpio_runtime` until unregistered or exit.

## Dependencies and Integration Points

It depends on OF GPIO nodes, OF IRQ mapping, interrupt APIs, PowerMac feature calls, workqueues, and AOA GPIO abstractions. The layout fabric selects this implementation for specific layouts.

## Risks and Test Signals

Risks include global state preventing multiple cards, leaked OF node references from `get_gpio`, IRQ free conditions inconsistent between `notify` and `gpio_private`, active-state inversion mistakes, and no locking around GPIO read-modify-write. Tests should cover all supported GPIO names/aliases, detect IRQ registration, autoswitch notifications, amp restore behavior, and layout remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/gpio-feature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/gpio-pmf.c -->
# sources/distributed-fs/ceph-client/sound/aoa/core/gpio-pmf.c

## Purpose

This file implements AOA GPIO methods using PowerMac platform functions (PMF). It provides amp mute, reset, jack detection, and notification callbacks for layouts where PMF functions describe audio GPIO behavior.

## Important APIs, types, and functions

The exported provider is `pmf_gpio_methods`. Generated setters/getters cover headphone, amp/speakers, and lineout. Other important functions are `pmf_gpio_set_hw_reset`, `pmf_gpio_all_amps_off`, `pmf_gpio_all_amps_restore`, `pmf_handle_notify`, `pmf_gpio_init`, `pmf_gpio_exit`, `pmf_handle_notify_irq`, `pmf_set_notify`, and `pmf_get_detect`.

## Control Flow

Setters call named PMF functions like `headphone-mute`, passing inverted logical state for mute, then update `implementation_private`. Init mutes amps and initializes delayed work and mutexes. Notification registration allocates a `pmf_irq_client`, registers it against a named detect function, stores it as `gpio_private`, and schedules delayed work from the PMF IRQ handler. Removal unregisters PMF IRQ clients, cancels work, frees clients, and mutes amps.

## State and Persistence

Per-runtime `implementation_private` stores logical output states. `gpio_notification.gpio_private` owns PMF IRQ client allocations while notifications are active.

## Dependencies and Integration Points

It depends on PowerMac PMF APIs, AOA GPIO abstractions, workqueues, mutexes, and slab allocation. The layout fabric selects this implementation for most layouts.

## Risks and Test Signals

Risks include missing PMF functions, inverted mute semantics, notification client leaks, detect calls returning platform-specific values, and callback races during exit. Tests should cover PMF call failures, register/unregister notifications, detect reads, amp restore, and suspend/remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/core/gpio-pmf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/Kconfig -->
# sources/distributed-fs/ceph-client/sound/aoa/fabrics/Kconfig

## Purpose

This file declares the AOA layout-id fabric option, which binds codecs to soundbus devices based on PowerMac device-tree layout or device IDs.

## Important APIs, types, and functions

It defines `SND_AOA_FABRIC_LAYOUT`, a tristate option selecting `SND_AOA_SOUNDBUS` and `SND_AOA_SOUNDBUS_I2S`.

## Control Flow

Selecting this option builds the layout fabric and its required soundbus/I2S support.

## State and Persistence

Configuration persists in `.config`. Runtime state is implemented in `layout.c`.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the fabrics Makefile.

## Risks and Test Signals

Risks include missing soundbus dependencies and unavailable fabric for supported machines. Build tests should compile this fabric with AOA and I2S bus enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/fabrics/Makefile

## Purpose

This Makefile builds the AOA layout fabric module.

## Important APIs, types, and functions

It maps `snd-aoa-fabric-layout-y += layout.o` and adds `snd-aoa-fabric-layout.o` under `CONFIG_SND_AOA_FABRIC_LAYOUT`.

## Control Flow

Kbuild conditionally compiles `layout.c` into the fabric object.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes the layout fabric Kconfig symbol and produces a module that registers a soundbus driver.

## Risks and Test Signals

Risks are limited to build wiring and module naming used by users/configs. Build tests should cover built-in and modular layout fabric.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/layout.c -->
# sources/distributed-fs/ceph-client/sound/aoa/fabrics/layout.c

## Purpose

This file implements the AOA layout fabric. It identifies supported Apple audio layouts from device-tree `layout-id` or `device-id`, requests matching codec modules, assigns codecs to soundbus/GPIO runtime data, creates output/detect ALSA controls, and manages autoswitching for headphone and line-out detection.

## Important APIs, types, and functions

Important data structures are `struct codec_connection`, `struct codec_connect_info`, `struct layout`, `struct layout_dev_ptr`, and `struct layout_dev`. Static layout tables map many PowerMac layout IDs and device IDs to codec names and connection bitmasks. Key functions are `find_layout_by_id`, `find_layout_by_device`, `use_layout`, `check_codec`, `layout_found_codec`, `layout_remove_codec`, `layout_notify`, `layout_attached_codec`, `aoa_fabric_layout_probe`, `aoa_fabric_layout_remove`, suspend/resume callbacks, and module init/exit.

## Control Flow

Soundbus probe locates a `soundchip` child node, reads layout or device ID, finds a layout table entry, allocates `layout_dev`, chooses feature-call or PMF GPIO methods, initializes GPIO, registers the AOA fabric, sets PCM name/id, requests required codec modules, and enables autoswitch defaults. When a codec registers, `layout_found_codec()` matches by name and optional OF phandle reference, assigns soundbus/GPIO pointers, computes codec-specific `connected` bits, and stores fabric data. After codec init, `layout_attached_codec()` creates amp/detect ALSA controls, registers notification callbacks, sets initial output state, and emits control notifications on jack changes.

## State and Persistence

The file uses global `layouts_list`, `layouts_list_items`, and singleton `layout_device`, matching the wider single-card AOA model. Each `layout_dev` persists while its soundbus device is bound and owns GPIO runtime state, control pointers, detect booleans, autoswitch flags, sound node reference, and layout pointer.

## Dependencies and Integration Points

It depends on the AOA core fabric API, soundbus driver API, OF node properties and phandles, `request_module`, ALSA controls, and PMF/feature GPIO methods. It also relies on codec drivers using names such as `onyx`, `tas`, `toonie`, and `topaz`.

## Risks and Test Signals

Risks include hard-coded layout data drift, singleton limitations, `layout_remove_codec()` not clearing codec array entries, autoswitch races, duplicate ALSA control names when lineout is labeled headphone, missing OF references with multiple soundbuses, and cleanup ordering with pending notifications. Tests should cover known layout IDs/device IDs, codec phandle matching, PMF vs feature GPIO selection, module request names, jack-detect autoswitch behavior, suspend/resume muting, and soundbus remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/fabrics/layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/Kconfig -->
# sources/distributed-fs/ceph-client/sound/aoa/soundbus/Kconfig

## Purpose

This file declares the generic Apple Soundbus option and the I2S soundbus implementation option.

## Important APIs, types, and functions

It defines `SND_AOA_SOUNDBUS`, selecting `SND_PCM`, and `SND_AOA_SOUNDBUS_I2S`, depending on `SND_AOA_SOUNDBUS && PCI`.

## Control Flow

Kconfig selections control generic soundbus support and I2S bus implementation availability.

## State and Persistence

Configuration persists in `.config`. Runtime bus state is in `soundbus/core.c` and `i2sbus` files.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the soundbus Makefile. The layout fabric selects both symbols.

## Risks and Test Signals

Risks include missing PCI dependency for I2S or missing PCM selection for soundbus. Build tests should cover generic soundbus only and full I2S support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/soundbus/Makefile

## Purpose

This Makefile builds the generic AOA soundbus core and optionally recurses into the I2S bus implementation.

## Important APIs, types, and functions

It defines `obj-$(CONFIG_SND_AOA_SOUNDBUS) += snd-aoa-soundbus.o`, composes it from `core.o sysfs.o`, and adds `i2sbus/` under `CONFIG_SND_AOA_SOUNDBUS_I2S`.

## Control Flow

Kbuild includes generic bus code and sysfs support when soundbus is enabled, then recurses into I2S when selected.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes soundbus Kconfig symbols and builds the bus exported to fabrics and I2S devices.

## Risks and Test Signals

Risks include omitting sysfs support or failing to recurse into I2S. Build tests should cover both symbols independently where dependencies allow.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/core.c -->
# sources/distributed-fs/ceph-client/sound/aoa/soundbus/core.c

## Purpose

This file implements the generic Apple Soundbus driver-model bus. It registers the `aoa-soundbus` bus type, manages soundbus device references, dispatches probe/remove/shutdown to soundbus drivers, emits OF uevents, and exports add/remove/register APIs.

## Important APIs, types, and functions

Public exports are `soundbus_dev_get`, `soundbus_dev_put`, `soundbus_add_one`, `soundbus_remove_one`, `soundbus_register_driver`, and `soundbus_unregister_driver`. Internal callbacks are `soundbus_probe`, `soundbus_uevent`, `soundbus_device_remove`, and `soundbus_device_shutdown`. `soundbus_bus_type` defines bus operations and sysfs groups.

## Control Flow

Bus init registers the bus at `subsys_initcall`. `soundbus_add_one()` validates required fields, names the OF-backed device, assigns the bus, and registers it. Driver registration fills common driver fields and calls `driver_register`. Probe gets an extra device reference before invoking the driver's probe and drops it on failure. Remove invokes the driver's remove callback and drops the reference. Uevent generation exports OF name, type, compatible strings, compatible count, and modalias.

## State and Persistence

The bus type persists until module exit. A static `devcount` names devices monotonically. Bound soundbus devices hold references through probe/remove lifetime.

## Dependencies and Integration Points

It depends on Linux driver core, OF platform device registration, sysfs groups declared elsewhere, and AOA soundbus structures. Layout fabric registers as a soundbus driver; I2S bus code creates soundbus devices.

## Risks and Test Signals

Risks include reference leaks if probe/remove paths mispair, uevent compatible-string length handling, sanity checks rejecting valid devices, and modalias mismatch preventing module autoload. Tests should cover add/remove, driver probe failure, uevent content for multi-string compatible properties, and shutdown/remove callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/Makefile -->
# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/Makefile

## Purpose

This Makefile builds the Apple I2S soundbus implementation module.

## Important APIs, types, and functions

It adds `snd-aoa-i2sbus.o` under `CONFIG_SND_AOA_SOUNDBUS_I2S` and composes it from `core.o`, `pcm.o`, and `control.o`.

## Control Flow

Kbuild conditionally links the I2S bus core, PCM, and control routines.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes the I2S soundbus Kconfig symbol and builds code used by the layout fabric through generic soundbus devices.

## Risks and Test Signals

Risks are build-wiring issues. Build tests should compile I2S support built-in and modular.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/control.c -->
# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/control.c

## Purpose

This file implements low-level control helpers for Apple I2S soundbus devices. It discovers platform functions for enabling the bus, cell, and clocks, and falls back to KeyLargo FCR register bits for bus 0 and 1 when platform functions are absent.

## Important APIs, types, and functions

Public functions are `i2sbus_control_init`, `i2sbus_control_destroy`, `i2sbus_control_add_dev`, `i2sbus_control_remove_dev`, `i2sbus_control_enable`, `i2sbus_control_cell`, and `i2sbus_control_clock`. State is carried in `struct i2sbus_control` and `struct i2sbus_dev` fields declared in `i2sbus.h`.

## Control Flow

Initialization allocates a control object, initializes its list, and records the macio chip. Adding a device discovers PMF functions named `enable`, `cell-enable`, `clock-enable`, `cell-disable`, and `clock-disable`; nonzero/nonone bus numbers require all PMF functions because FCR fallback is only known for buses 0 and 1. Enable/cell/clock operations prefer PMF calls, otherwise check macio base and set or clear the matching KeyLargo FCR bit. Device removal deletes the device list item and destroys the control object when the list becomes empty.

## State and Persistence

The control object persists while at least one I2S device is on its list. Each I2S device stores PMF function handles discovered at add time. Hardware enable state is in PMF-managed firmware or KeyLargo FCR registers.

## Dependencies and Integration Points

It depends on macio, PowerMac feature and platform-function APIs, KeyLargo register macros, I/O access macros, and I2S bus structures. Higher-level I2S core/PCM code calls these helpers around bus and clock operations.

## Risks and Test Signals

Risks include unbalanced PMF function references on normal remove, fallback register writes lacking locking as noted by comments, destroying shared control while callers still hold pointers, unsupported bus numbers without full PMF data, and invalid enable values. Tests should cover PMF-present and FCR-fallback paths, buses 0/1 and unsupported buses, enable/disable sequencing, list lifetime, and error returns for missing macio base.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/control.c -->
