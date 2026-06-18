# Research Report: subset-b-006753

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/sound/asound.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/sound/asound.h

Purpose: This is a local perf copy of the ALSA userspace ABI header used by trace beauty generators, especially the PCM and control ioctl table scripts. It defines protocol-version helpers, ALSA device interface constants, structures, and ioctl command numbers for hwdep, PCM, rawmidi/UMP, timer, and control devices.

Important APIs/types/functions: The important exported contracts are macro families such as `SNDRV_PROTOCOL_VERSION`, `SNDRV_PCM_IOCTL_*`, and `SNDRV_CTL_IOCTL_*`; typed frame aliases `snd_pcm_uframes_t` and `snd_pcm_sframes_t`; and ABI structs such as `snd_pcm_info`, `snd_pcm_hw_params`, `snd_pcm_status`, `snd_pcm_sync_ptr`, `snd_rawmidi_info`, `snd_timer_info`, `snd_ctl_elem_info`, and `snd_ctl_elem_value`. The header also carries endianness and time64 compatibility choices through conditional definitions.

Control flow: There is no runtime control flow. Preprocessor branches select kernel versus userspace includes, time64 structures, endian-specific PCM format aliases, and ioctl aliases such as `SNDRV_TIMER_IOCTL_TREAD`.

State and persistence: The file defines persisted ioctl ABI layouts. Reserved fields, packed UMP structures, and time-size variants are part of the binary contract; changing them would affect generated perf decoding and compatibility with kernel/user ABI definitions.

Dependencies and integration points: `sndrv_pcm_ioctl.sh` and `sndrv_ctl_ioctl.sh` grep this file to generate `sndrv_pcm_ioctl_array.c` and `sndrv_ctl_ioctl_array.c`, which are included by `ioctl.c`. It depends on Linux type, byteorder, ioctl, and time declarations.

Risks: Regex-based consumers assume macro spelling and `_IO*('A'/'U', nr, ...)` shape. ABI drift, time64 structure changes, or copied-header staleness can silently omit newly added ALSA ioctls from perf trace beautification.

Test signals: Build perf generated beauty files and verify `perf trace` prints ALSA PCM/control ioctls as `SNDRV_PCM_*` and `SNDRV_CTL_*`. Compare generated arrays against `SNDRV_PCM_IOCTL_*` and `SNDRV_CTL_IOCTL_*` definitions and run header selftests or kernel UAPI sync checks if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/sound/asound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/ioctl.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/ioctl.c

Purpose: This file beautifies `ioctl` command arguments for `perf trace`, translating encoded `_IOC` command words into subsystem command names or a structured fallback tuple.

Important APIs/types/functions: `syscall_arg__scnprintf_ioctl_cmd` is the exported formatter. Static helpers handle TTY, DRM, ALSA PCM, ALSA control, KVM, vhost/virtio, perf event, and USBDEVFS command spaces. `ioctl__scnprintf_cmd` decodes `_IOC_DIR`, `_IOC_TYPE`, `_IOC_NR`, and `_IOC_SIZE`.

Control flow: The formatter first checks the traced file descriptor via `thread__files_entry`; USB device major 189 is treated as USBDEVFS even though it shares type letter `U` with ALSA control. Otherwise, the decoded ioctl type indexes a sparse ordered dispatch table. If no specialized table matches, the code prints `_IOC_NONE`, `_IOC_READ`, and/or `_IOC_WRITE` with the raw type, number, and size.

State and persistence: No persistent state is stored. It consumes live thread file metadata and generated static string arrays.

Dependencies and integration points: It includes generated arrays from beauty shell scripts and uses `struct syscall_arg`, `struct file`, `strarray`, `scnprintf`, and UAPI ioctl macros. It is wired into perf trace syscall argument formatting for x86 according to the source comment.

Risks: Type collisions are real, especially `U`, so file metadata quality determines USB versus ALSA decoding. Generated table omissions degrade output to raw tuples. The subsystem dispatch table relies on index arithmetic from `$` to `0xAF`.

Test signals: Exercise representative ioctl syscalls for TTY, KVM, perf event, ALSA control/PCM, and USB device fds. Confirm unknown commands print fallback tuples and `show_string_prefix` controls `_IOC_` prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp.c

Purpose: This formatter supports `kcmp(2)` argument rendering, especially the `type`, `idx1`, and `idx2` relationship.

Important APIs/types/functions: `syscall_arg__scnprintf_kcmp_type` maps `KCMP_*` values using the generated `kcmp_type_array.c`; `syscall_arg__scnprintf_kcmp_idx` formats file indexes as process file descriptors when type is `KCMP_FILE`; `kcmp__scnprintf_type` wraps the shared `strarray` lookup.

Control flow: The type formatter checks the selected comparison type and masks out `idx1`/`idx2` for all non-file comparisons because those arguments are ignored by the kernel. The index formatter reads syscall argument 2 for the type and falls back to numeric output unless it is `KCMP_FILE`; for file comparisons it chooses pid1 or pid2 based on the current argument index and calls `pid__scnprintf_fd`.

State and persistence: It mutates only `arg->mask` for display suppression. No data is persisted.

Dependencies and integration points: It depends on `uapi/linux/kcmp.h`, `machine.h`, generated type arrays, and perf thread/file descriptor lookup helpers.

Risks: Incorrect argument indexes would associate an fd with the wrong process. New `KCMP_*` values require regenerated arrays.

Test signals: Trace `kcmp` with `KCMP_FILE` and a non-file type. Verify fd arguments are named for file comparisons and hidden for non-file comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp_type.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp_type.sh

Purpose: Generates a C string array for `KCMP_*` comparison types.

Important APIs/types/functions: The script accepts an optional header directory, defaults to `tools/include/uapi/linux/`, greps `kcmp.h`, excludes `KCMP_TYPES`, and emits `static const char *kcmp_types[]`.

Control flow: It prints the array prologue, extracts enum assignments matching `KCMP_(\w+)`, transforms full names into index/name pairs with `sed`, formats entries with `xargs printf`, and prints the epilogue.

State and persistence: It writes generated C to stdout only; persistence is handled by the build rule redirecting output.

Dependencies and integration points: The output is included by `kcmp.c`. It depends on POSIX shell, `grep`, `sed -r`, and `xargs`.

Risks: The regex assumes enum entries have leading whitespace and a comma. If the header changes to macro definitions or initializer expressions, values may be dropped.

Test signals: Run the generator against the target UAPI header and compile `kcmp.c`; confirm every public `KCMP_*` except sentinel values appears in the array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp_type.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kvm_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kvm_ioctl.sh

Purpose: Builds the KVM ioctl command name table consumed by `ioctl.c`.

Important APIs/types/functions: It parses `KVM_*` `_IO`, `_IOR`, `_IOW`, and `_IOWR` definitions from `kvm.h` and emits `static const char *kvm_ioctl_cmds[]` indexed by ioctl number.

Control flow: The script selects a header directory, greps for `KVMIO`-based definitions with hexadecimal command numbers, strips unsupported or intentionally excluded architecture/debug commands, sorts the result, and formats array entries.

State and persistence: Output is stdout-generated C only.

Dependencies and integration points: The generated array is included in `ioctl__scnprintf_kvm_cmd`. Build correctness depends on UAPI `tools/include/uapi/linux/kvm.h` and standard text utilities.

Risks: The explicit exclusion list can hide valid commands if perf later wants broader KVM coverage. Regex drift can miss macros with nonstandard formatting.

Test signals: Regenerate the array, compile perf, and trace a KVM fd issuing common ioctls such as create VM/VCPU to verify `KVM_*` names appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kvm_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/madvise_behavior.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/madvise_behavior.sh

Purpose: Generates symbolic names for `madvise(2)` behavior values.

Important APIs/types/functions: It emits `static const char *madvise_advices[]` by parsing `MADV_*` decimal definitions from `mman-common.h`.

Control flow: Optional header directory selection is followed by a grep/sed/sort pipeline and `xargs printf` entry generation.

State and persistence: The script is stateless and writes generated C to stdout.

Dependencies and integration points: `mmap.c` includes the generated `madvise_behavior_array.c` and calls it from `syscall_arg__scnprintf_madvise_behavior`.

Risks: It only recognizes decimal values, so hex or expression-valued `MADV_*` definitions would be ignored. Duplicate or alias definitions may overwrite array slots depending on output order.

Test signals: Generate against current headers and trace `madvise` with common values such as `MADV_DONTNEED`; unknown values should print numerically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/madvise_behavior.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap.c

Purpose: Provides formatters for memory-management syscall arguments: mmap protections, mmap flags, mremap flags, and madvise behavior.

Important APIs/types/functions: Static formatters `syscall_arg__scnprintf_mmap_prot`, `syscall_arg__scnprintf_mmap_flags`, `syscall_arg__scnprintf_mremap_flags`, and `syscall_arg__scnprintf_madvise_behavior` are exposed via `SCA_MMAP_PROT`, `SCA_MMAP_FLAGS`, `SCA_MREMAP_FLAGS`, and `SCA_MADV_BHV` macros. It consumes generated arrays for `PROT_`, `MAP_`, `MREMAP_`, and `MADV_` names.

Control flow: Protection value zero is printed as `PROT_NONE`; otherwise flags go through `strarray__scnprintf_flags`. `MAP_ANONYMOUS` masks the ignored fd and offset syscall arguments. `MREMAP_FIXED` controls whether the new-address argument is displayed. `madvise` indexes directly into its generated advice table and falls back to a numeric string.

State and persistence: No persistent state; display state is changed by setting bits in `arg->mask`.

Dependencies and integration points: Integrated through perf trace syscall argument macros and the shared `strarray` flag formatter from this beauty subsystem.

Risks: The generated flag arrays require power-of-two indexing. Non-bitmask advice values use direct array indexes, so sparse values need NULL-safe fallback.

Test signals: Trace `mmap`, `mremap`, and `madvise` combinations, verifying argument masking for anonymous mappings and non-fixed remaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_flags.sh

Purpose: Generates a flag-indexed C table for `MAP_*` mmap flags across generic and architecture-specific headers.

Important APIs/types/functions: It emits `static const char *mmap_flags[]` plus compatibility `#ifndef MAP_*` definitions for found flags. It accepts either host architecture or explicit linux/generic/arch header directories.

Control flow: The script derives host arch when needed, parses architecture `mman.h`, Linux `mman.h`, `mman-common.h`, and generic `mman.h` depending on include relationships, excludes `MAP_UNINITIALIZED`, `MAP_TYPE`, and `MAP_SHARED_VALIDATE`, and indexes each flag as `ilog2(value) + 1`.

State and persistence: Output goes to stdout. It has no runtime state.

Dependencies and integration points: Output is included by `mmap.c`; `ilog2` indexing relies on `<linux/log2.h>` in the C consumer.

Risks: Non-power-of-two masks are unsuitable for this table and are filtered only for known cases. Duplicate generic/arch definitions may produce repeated slots.

Test signals: Regenerate on x86 and at least one non-x86 architecture header set, then compile and trace `mmap` flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_prot.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_prot.sh

Purpose: Generates the `PROT_*` protection flag table for mmap-like syscall formatting.

Important APIs/types/functions: It emits `static const char *mmap_prot[]` and fallback `#define PROT_*` guards, omitting `PROT_NONE` because zero is handled specially in `mmap.c`.

Control flow: The script chooses generic and architecture mman header directories, reads generic common flags when the arch header includes generic mman content, then reads arch-specific definitions when present. Each hex value is converted to an `ilog2(value) + 1` slot.

State and persistence: Stateless stdout generator.

Dependencies and integration points: The output is included by `mmap.c` and consumed by `strarray__scnprintf_flags`.

Risks: Decimal or expression values are not matched. Zero-valued or mask-valued protections are intentionally not suitable for this generated bit table.

Test signals: Compare generated table entries to `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, and arch-specific protection bits; trace mmap with combined protections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_prot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mode_t.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mode_t.c

Purpose: Formats `mode_t` arguments for syscalls such as `open`, `mkdir`, and permission-changing calls.

Important APIs/types/functions: `syscall_arg__scnprintf_mode_t` emits symbolic `S_*` file type and permission bits. Local fallback definitions cover common aggregate macros such as `S_IALLUGO`.

Control flow: The function iterates through aggregate and individual `S_*` macros using `P_MODE`, printing matching components with `|` separators and clearing handled bits. Unknown remaining bits are appended in hex.

State and persistence: No persistent state; only local formatting state.

Dependencies and integration points: It depends on POSIX stat mode macros and perf trace's syscall argument formatter macro `SCA_MODE_T`.

Risks: Aggregate macros are printed before individual bits, so output intentionally favors compact forms such as `S_IALLUGO`; tests must account for that ordering. If platform headers omit macros, fallback coverage is partial.

Test signals: Format file-type modes, permission-only modes, aggregate modes, and unknown high bits. Confirm `show_string_prefix` toggles `S_`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mode_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.c

Purpose: Beautifies `mount(2)` flag arguments and strips legacy mount magic before display.

Important APIs/types/functions: `syscall_arg__scnprintf_mount_flags` formats `MS_*` flags; `syscall_arg__mask_val_mount_flags` removes `MS_MGC_MSK` when it contains `MS_MGC_VAL`; `mount__scnprintf_flags` uses the generated mount flag array.

Control flow: The mask hook implements the kernel `do_mount` compatibility rule for pre-2.4 magic. The print hook passes the cleaned or original value through `strarray__scnprintf_flags`.

State and persistence: Stateless except for argument-value normalization during display.

Dependencies and integration points: Includes `<sys/mount.h>`, `linux/log2.h`, and `trace/beauty/generated/mount_flags_array.c`; called by perf trace syscall argument plumbing.

Risks: Generated table quality depends on the copied `mount.h`. Missing new flags fall back to numeric bits. Magic stripping must run in the appropriate mask hook path.

Test signals: Trace mounts with common flags and an artificial value containing `MS_MGC_VAL`; verify the magic bits are not shown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.sh

Purpose: Generates the `MS_*` mount flag string array.

Important APIs/types/functions: It parses `mount.h` from the beauty UAPI copy and emits `static const char *mount_flags[]`, supporting both numeric constants and `(1<<n)` forms.

Control flow: The first pipeline handles decimal definitions, filters out mask/magic/noisy constants, sorts numerically, and indexes zero specially. The second pipeline handles shift-expression definitions.

State and persistence: Stateless stdout generation.

Dependencies and integration points: Output is included by `mount_flags.c`; it requires `grep`, `sed`, `sort`, and `xargs`.

Risks: Hex constants in `mount.h` are not handled by the first regex. If a semantic flag is filtered by the broad `(MSK|VERBOSE|MGC_VAL)` exclusion it will not be shown.

Test signals: Regenerate and verify entries for common flags such as `MS_RDONLY`, `MS_NOSUID`, and `MS_BIND`; compile the consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount.c

Purpose: Formats `move_mount(2)` flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_move_mount_flags` is the exported formatter and delegates to `move_mount__scnprintf_flags`, which includes the generated `move_mount_flags_array.c` and defines `MOVE_MOUNT_` prefix metadata.

Control flow: The formatter reads `arg->val` and passes it directly to `strarray__scnprintf_flags`.

State and persistence: No persistent state and no argument masking.

Dependencies and integration points: Depends on perf beauty helpers and generated output from `move_mount_flags.sh`.

Risks: Unknown future flags print numerically. Correctness depends on generated entries being indexed by bit position.

Test signals: Trace `move_mount` calls with `MOVE_MOUNT_F_*` values and combined flags; verify symbolic output with and without prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount_flags.sh

Purpose: Generates the `MOVE_MOUNT_*` flag table.

Important APIs/types/functions: It reads the beauty copy of `uapi/linux/mount.h` and emits `static const char *move_mount_flags[]` with `ilog2(hex_value) + 1` indexes.

Control flow: Optional header directory selection is followed by one grep/sed/xargs pipeline matching hexadecimal `MOVE_MOUNT_` definitions.

State and persistence: stdout-only generator.

Dependencies and integration points: The output is consumed by `move_mount.c`.

Risks: Decimal or expression-valued flags would be missed. The regex requires at least one non-underscore character after `MOVE_MOUNT_`, so unusual names could fail.

Test signals: Regenerate and inspect entries for all current `MOVE_MOUNT_*` flags; compile and trace a syscall using those flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mremap_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mremap_flags.sh

Purpose: Generates `MREMAP_*` flag names for `mremap(2)` formatting.

Important APIs/types/functions: It parses `tools/include/uapi/linux/mman.h` or a supplied directory and emits `static const char *mremap_flags[]`, including fallback `#define MREMAP_*` guards.

Control flow: It matches hex or digit constants, converts each value into `ilog2(value) + 1`, and formats both the array entry and conditional macro definition.

State and persistence: Stateless stdout generator.

Dependencies and integration points: Included by `mmap.c` and consumed by `strarray__scnprintf_flags`.

Risks: Composite values would be incorrectly treated as single-bit flags; currently `MREMAP_*` flags are expected to be bit values.

Test signals: Verify generated entries for `MREMAP_MAYMOVE`, `MREMAP_FIXED`, and related flags; trace `mremap` and confirm `new_address` masking in the consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mremap_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/msg_flags.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/msg_flags.c

Purpose: Formats socket message flags for send/recv style syscalls.

Important APIs/types/functions: `syscall_arg__scnprintf_msg_flags` recognizes many `MSG_*` constants, including local fallbacks for newer flags such as `MSG_ZEROCOPY`, `MSG_SPLICE_PAGES`, and `MSG_CMSG_CLOEXEC`.

Control flow: Zero flags print as `NONE`. A macro-driven sequence appends known flags and clears them from the working value; leftover bits are appended as hex.

State and persistence: Stateless formatting only.

Dependencies and integration points: Depends on `<sys/socket.h>` and perf trace `SCA_MSG_FLAGS` binding.

Risks: Manual ordering can affect output expectations. New kernel flags need local fallback constants or generated support to avoid pure hex output on older build hosts.

Test signals: Trace send/recv syscalls with no flags, common flags, and unknown bits; verify prefix behavior and hex fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/msg_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/open_flags.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/open_flags.c

Purpose: Formats `open/openat/openat2` style file flags and hides the mode argument when it is ignored.

Important APIs/types/functions: `open__scnprintf_flags` is a reusable formatter; `syscall_arg__scnprintf_open_flags` wraps it for syscall arguments and sets `arg->mask` for the following mode parameter when `O_CREAT` is absent.

Control flow: The formatter handles access mode first, emitting `O_RDONLY` for zero. It then walks known `O_*` bits, handles platform `O_NONBLOCK` versus `O_NDELAY`, detects `O_SYNC` versus `O_DSYNC`, clears printed bits, and appends unknown leftovers.

State and persistence: It only mutates per-syscall display mask state.

Dependencies and integration points: Depends on `<fcntl.h>` and local fallbacks for flags missing on older libc headers. Used by perf trace syscall tables.

Risks: `O_TMPFILE` and access-mode combinations are subtle because some flags are masks rather than independent bits. Mode hiding only keys on `O_CREAT`, while some APIs may also require mode for `O_TMPFILE`.

Test signals: Trace `openat` with read-only, create, tmpfile, sync, nonblock, and unknown bits. Verify mode visibility follows expected kernel semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/open_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_event_open.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_event_open.c

Purpose: Beautifies `perf_event_open(2)` flags and, when available, the user `perf_event_attr` structure captured by syscall augmentation.

Important APIs/types/functions: `syscall_arg__scnprintf_perf_flags` formats `PERF_FLAG_*`; `perf_event_attr___scnprintf` formats a `struct perf_event_attr` by calling `perf_event_attr__fprintf`; `syscall_arg__scnprintf_perf_event_attr` prints augmented attributes or falls back to the pointer value. `SCA_PERF_ATTR_FROM_USER` marks augmented user memory arguments.

Control flow: Flag formatting is manual bit clearing with hex fallback. Attribute formatting builds `{ name: value, ... }` through an `attr__fprintf` callback that writes into the caller buffer. The syscall argument formatter first checks `arg->augmented.args`.

State and persistence: No persistent state. It reads augmented syscall capture buffers and honors `trace->show_zeros`.

Dependencies and integration points: Depends on perf event attr printing utilities and the syscall augmentation path that copies user memory.

Risks: Without augmentation the attr pointer is opaque. Buffer truncation behavior depends on cumulative `scnprintf` accounting. New `PERF_FLAG_*` values need updates.

Test signals: Trace `perf_event_open` with augmentation enabled and disabled; verify flag names and structured attr output for common event attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_event_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_ioctl.sh

Purpose: Generates perf event ioctl command names.

Important APIs/types/functions: It parses `PERF_EVENT_IOC_*` definitions from `perf_event.h` and emits `static const char *perf_ioctl_cmds[]`.

Control flow: Optional header directory selection is followed by a regex matching `_IO*('$', nr, ...)`, sed conversion to index/name pairs, sorting, and formatted output.

State and persistence: Stateless stdout generator.

Dependencies and integration points: The output is included by `ioctl__scnprintf_perf_cmd` in `ioctl.c`.

Risks: The regex is specialized to the dollar ioctl type and numeric command argument; formatting changes may drop entries.

Test signals: Regenerate and confirm entries for common perf ioctls such as enable, disable, reset, and set output; trace ioctl calls on perf event fds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pid.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pid.c

Purpose: Formats PID syscall arguments with the best-known command name.

Important APIs/types/functions: `syscall_arg__scnprintf_pid` prints the numeric pid and appends the thread comm when available.

Control flow: The function looks up or creates a thread in `trace->host`, lazily populates its comm from `/proc` if unset, appends `(<comm>)` when available, and releases the thread reference.

State and persistence: It can populate perf's in-memory thread cache with newly discovered comm values. No file state is written.

Dependencies and integration points: Depends on `machine__findnew_thread`, `thread__set_comm_from_proc`, `thread__comm_*`, and perf trace state.

Risks: PID reuse and `/proc` races can attach stale or missing names. Lookup can allocate during formatting.

Test signals: Trace syscalls with live, exited, and unknown PIDs; verify numeric output remains stable even when comm lookup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc.c

Purpose: Formats `pkey_alloc(2)` access-right flags and provides a shared flag-array formatter used by other beauty files.

Important APIs/types/functions: `strarray__scnprintf_flags` maps bitmask values to string-array entries indexed by bit position plus one. `syscall_arg__scnprintf_pkey_alloc_access_rights` formats `PKEY_*` access-right bits using generated `pkey_alloc_access_rights_array.c`.

Control flow: The shared formatter handles zero through entry 0 if present, then walks bit positions from index 1, appending names or numeric unknown bits. The pkey wrapper delegates directly.

State and persistence: Stateless formatting only.

Dependencies and integration points: Included by the beauty build as a utility provider for generated flag arrays. Consumes UAPI-derived `PKEY_*` definitions.

Risks: Unknown bits are printed with a suspicious `"0x%#"` format string in this snapshot, which may be a formatting bug. Arrays must follow the bit-position-plus-one convention.

Test signals: Unit-test zero, disable-access, disable-write, and unknown bits. Build all consumers that call `strarray__scnprintf_flags`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc_access_rights.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc_access_rights.sh

Purpose: Generates `PKEY_*` access-right flag names.

Important APIs/types/functions: It parses `mman-common.h` and emits `static const char *pkey_alloc_access_rights[]` with bit-indexed entries.

Control flow: The script selects a header directory, greps hex `PKEY_*` definitions, sorts the value/name tuples, and indexes each value as zero or `ilog2(value) + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `pkey_alloc.c`.

Risks: Decimal or expression-valued definitions are ignored. Non-bitmask constants would be badly indexed.

Test signals: Regenerate and confirm entries for `PKEY_DISABLE_ACCESS` and `PKEY_DISABLE_WRITE`; compile the consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc_access_rights.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl.c

Purpose: Beautifies `prctl(2)` option and selected option-dependent arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_prctl_option` maps `PR_*` options and masks unused trailing arguments; `syscall_arg__scnprintf_prctl_arg2` formats `PR_SET_MM` suboptions and `PR_SET_NAME` pointers specially; `syscall_arg__scnprintf_prctl_arg3` formats `PR_SET_MM` addresses as hex.

Control flow: The option formatter looks up a sparse local mask table keyed by option value and ORs the relevant ignored-argument bits into `arg->mask`. The arg2/arg3 formatters inspect syscall argument 0 to choose context-sensitive rendering.

State and persistence: Only per-call display mask state is mutated.

Dependencies and integration points: Uses generated `prctl_option_array.c`, Linux `prctl.h`, and shared `strarray` helpers. Perf trace syscall definitions bind these functions to argument positions.

Risks: The mask table covers only selected options; unknown or complex options may show noisy unused arguments. Pointer contents are not copied for `PR_SET_NAME`, so it prints an address.

Test signals: Trace `PR_SET_NAME`, `PR_GET_DUMPABLE`, `PR_SET_MM`, and unknown options; verify masked argument behavior and prefix control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl_option.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl_option.sh

Purpose: Generates string arrays for `prctl(2)` option names and `PR_SET_MM_*` suboptions.

Important APIs/types/functions: It emits `static const char *prctl_options[]` and `static const char *prctl_set_mm_options[]` from the beauty copy of `uapi/linux/prctl.h`.

Control flow: The first pass matches `PR_*` definitions, excludes `PR_SET_PTRACER`, sorts numerically, and prints entries. The second pass matches `PR_SET_MM_*` definitions and emits a separate suboption table.

State and persistence: Stateless stdout generation.

Dependencies and integration points: Output is included by `prctl.c`.

Risks: The option regex expects a specific one-space `#define` style and mostly numeric values; formatting changes can omit options. Excluding `PR_SET_PTRACER` is intentional but should be reviewed if perf wants it displayed.

Test signals: Regenerate and compile; confirm names for common `PR_*` and `PR_SET_MM_*` values are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl_option.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/rename_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/rename_flags.sh

Purpose: Generates `RENAME_*` flag names for `renameat2(2)`.

Important APIs/types/functions: It reads `fs.h` and emits `static const char *rename_flags[]`, indexing shift-expression values as `bit + 1`.

Control flow: Optional header directory selection is followed by a regex matching `(1 << n)` style definitions and formatting entries with `%d + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: The output is included by `renameat.c`.

Risks: Hex or decimal `RENAME_*` definitions would not match. The script assumes all relevant rename flags are one-bit shifts.

Test signals: Verify generated entries for `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`; trace `renameat2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/rename_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/renameat.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/renameat.c

Purpose: Formats the `flags` argument for `renameat2(2)`.

Important APIs/types/functions: `syscall_arg__scnprintf_renameat2_flags` delegates to `renameat2__scnprintf_flags`, which includes `rename_flags_array.c` and defines a `RENAME_` string array.

Control flow: The syscall wrapper reads `arg->val` and invokes `strarray__scnprintf_flags`.

State and persistence: Stateless display code.

Dependencies and integration points: Depends on generated output from `rename_flags.sh` and perf beauty helpers. Bound into perf trace for renameat2 flags.

Risks: Unknown flags fall back numerically. The generated array must follow the bit-position convention used by the shared formatter.

Test signals: Trace `renameat2` with individual and combined flags, checking prefix behavior and numeric fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/renameat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sched_policy.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sched_policy.c

Purpose: Formats scheduler policy values and policy flags for scheduling syscalls.

Important APIs/types/functions: `syscall_arg__scnprintf_sched_policy` recognizes base policies `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `ISO`, `IDLE`, and `DEADLINE`, plus `SCHED_RESET_ON_FORK`.

Control flow: The function splits the low policy byte from high flag bits using `SCHED_POLICY_MASK`, prints the base policy or raw hex, then appends recognized flags and remaining unknown bits.

State and persistence: Stateless formatting.

Dependencies and integration points: Uses `<sched.h>` plus fallback definitions for newer constants. Bound through `SCA_SCHED_POLICY`.

Risks: `SCHED_ISO` may not exist on all systems but is represented positionally in the local array. Future high-bit flags require updates for symbolic output.

Test signals: Format common policies, `SCHED_RESET_ON_FORK` combinations, and unknown values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sched_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/seccomp.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/seccomp.c

Purpose: Beautifies `seccomp(2)` operation and flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_seccomp_op` maps `SECCOMP_SET_MODE_STRICT` and `SECCOMP_SET_MODE_FILTER`; `syscall_arg__scnprintf_seccomp_flags` maps `SECCOMP_FILTER_FLAG_TSYNC`.

Control flow: The op formatter uses a switch with hex fallback. The flag formatter clears known bits and appends unknown leftovers.

State and persistence: Stateless formatting.

Dependencies and integration points: Local fallback definitions avoid depending on newer system headers. Bound through `SCA_SECCOMP_OP` and `SCA_SECCOMP_FLAGS`.

Risks: This snapshot only names `TSYNC`; newer seccomp filter flags will show as hex until updated.

Test signals: Trace strict/filter operations, zero flags, `TSYNC`, and unknown flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/signum.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/signum.c

Purpose: Formats signal numbers as symbolic `SIG*` names for syscall arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_signum` switches over standard POSIX signals plus conditional platform signals such as `SIGEMT`, `SIGSTKFLT`, and `SIGSWI`.

Control flow: Matching cases return immediately with optional `SIG` prefix; unknown signal numbers print as hex.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<signal.h>` and `SCA_SIGNUM`.

Risks: Real-time signals and platform-specific aliases are not exhaustively named. Alias values may make only the first matching case visible.

Test signals: Format common signals, optional platform signals when defined, real-time signals, and invalid numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/signum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_ctl_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_ctl_ioctl.sh

Purpose: Generates ALSA control ioctl command names.

Important APIs/types/functions: It greps `SNDRV_CTL_IOCTL_*` definitions in `asound.h` and emits `static const char *sndrv_ctl_ioctl_cmds[]` indexed by ioctl command number.

Control flow: Optional sound UAPI directory selection is followed by one grep/sed pipeline matching `_IO*('U', 0xNN, ...)` definitions.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_sndrv_ctl_cmd` in `ioctl.c`.

Risks: The sed pattern expects uppercase names and the literal control ioctl type `U`. Multi-line or alias macros may be missed.

Test signals: Regenerate from the copied ALSA header and confirm entries for card info, element read/write, and power ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_ctl_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_pcm_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_pcm_ioctl.sh

Purpose: Generates ALSA PCM ioctl command names.

Important APIs/types/functions: It parses `SNDRV_PCM_IOCTL_*` definitions in `asound.h` and emits `static const char *sndrv_pcm_ioctl_cmds[]` indexed by ioctl command number.

Control flow: Optional sound UAPI directory selection is followed by a grep/sed pipeline matching `_IO*('A', 0xNN, ...)` command definitions.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_sndrv_pcm_cmd` in `ioctl.c`.

Risks: Alias macros such as internal sync-pointer variants may not map cleanly if their names or `_IO*` shape changes. It assumes command names are uppercase/digit/underscore.

Test signals: Regenerate and inspect entries for hardware params, status, prepare/start/drop, and transfer ioctls; trace ALSA PCM ioctl calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sndrv_pcm_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.c

Purpose: Beautifies socket address pointer arguments when perf trace has captured augmented user memory.

Important APIs/types/functions: `syscall_arg__scnprintf_sockaddr` chooses augmented formatting or pointer fallback. `af_inet__scnprintf`, `af_inet6__scnprintf`, and `af_local__scnprintf` render protocol-specific fields. The generated `socket_families` array maps address families.

Control flow: If `arg->augmented.args` is absent, the pointer is printed as hex. Otherwise, the captured bytes are treated as `struct sockaddr`, the family name is printed, and a family-specific callback adds path, port/address, IPv6 flowinfo, or scope id when supported.

State and persistence: Reads captured syscall argument bytes only; no persistent state.

Dependencies and integration points: Depends on syscall augmentation, generated `sockaddr.c`, sockets headers, UNIX sockets, and `inet_ntop`.

Risks: Captured buffer size is not checked in this local code before casting to larger sockaddr variants. UNIX paths may not be NUL-terminated in malformed input.

Test signals: Trace bind/connect/sendto with AF_UNIX, AF_INET, AF_INET6, unsupported families, and augmentation disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.sh

Purpose: Generates address-family string names for sockaddr formatting.

Important APIs/types/functions: It reads `AF_*` definitions from the beauty copy of `include/linux/socket.h` and emits `static const char *socket_families[]`.

Control flow: The script selects a header directory, parses `#define AF_NAME number` lines, formats indexed entries, and filters aliases/noisy entries `UNIX` and `MAX`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `sockaddr.c` and wrapped as `DEFINE_STRARRAY(socket_families, "PF_")`.

Risks: It uses AF names but the formatter prefixes with `PF_`, relying on Linux AF/PF value equivalence. Non-decimal definitions are ignored.

Test signals: Regenerate and ensure families such as LOCAL, INET, INET6, NETLINK, and PACKET appear; compile `sockaddr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.c

Purpose: Formats socket protocol and socket option level arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_socket_protocol` maps protocol numbers to `IPPROTO_*` only for AF_INET/AF_INET6 domains. `syscall_arg__scnprintf_socket_level` maps levels, with special handling for `SOL_SOCKET`.

Control flow: The protocol formatter reads argument 0 for domain and either uses `socket__scnprintf_ipproto` or falls back to integer output. The level formatter accounts for architectures where `SOL_SOCKET` is `0xffff`, otherwise checks `1`, then uses the generated socket-level table.

State and persistence: Stateless formatting.

Dependencies and integration points: Includes generated `socket.c` from `socket.sh`, sockets headers, and perf syscall argument helpers.

Risks: Non-IP socket domains intentionally leave protocol numeric. Architecture-specific `SOL_SOCKET` handling must stay aligned with kernel ABI.

Test signals: Trace `socket(AF_INET, ..., IPPROTO_TCP)`, non-IP socket creation, and `setsockopt`/`getsockopt` levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.sh

Purpose: Generates socket protocol and socket level lookup tables.

Important APIs/types/functions: It emits `socket_ipproto[]`, `socket_level[]`, and `DEFINE_STRARRAY(socket_level, "SOL_")`.

Control flow: With optional UAPI and beauty header directories, it parses enum-style `IPPROTO_* = number` entries from `linux/in.h` and `SOL_*` decimal defines from `include/linux/socket.h`, sorts both numerically, and prints arrays.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `socket.c`.

Risks: It only accepts decimal `SOL_*` values and enum formatting for IP protocols. Architecture special cases are handled in the C consumer rather than this generator.

Test signals: Regenerate and confirm common protocols and levels; compile and trace socket calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket_type.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket_type.c

Purpose: Formats the combined socket type and type flags argument to `socket(2)`.

Important APIs/types/functions: `syscall_arg__scnprintf_socket_type` recognizes base `SOCK_*` types and flags `SOCK_CLOEXEC` and `SOCK_NONBLOCK`.

Control flow: The function splits the low type nibble using `SOCK_TYPE_MASK`, switch-formats the base type, then appends recognized high flags and unknown leftovers.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<sys/socket.h>` and local fallback definitions. Bound via `SCA_SK_TYPE`.

Risks: The flag-printing macro omits the optional `SOCK_` prefix for flags even when `show_string_prefix` is true, which may be intentional but is inconsistent with the base type behavior. ABI-specific type values are handled manually because MIPS may override values.

Test signals: Trace sockets with stream/dgram/raw and CLOEXEC/NONBLOCK combinations on multiple architectures when possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx.c

Purpose: Formats the `statx(2)` mask argument.

Important APIs/types/functions: `syscall_arg__scnprintf_statx_mask` delegates to `statx__scnprintf_mask`, which includes `statx_mask_array.c` and formats `STATX_*` bitmasks.

Control flow: The syscall wrapper reads `arg->val` and passes it through `strarray__scnprintf_flags` with prefix control.

State and persistence: Stateless display code.

Dependencies and integration points: Generated output comes from `statx_mask.sh`; the formatter is used by perf trace for statx.

Risks: Composite mask values such as `STATX_BASIC_STATS` are intentionally omitted by the generator, so output decomposes into individual bits. New bits require regeneration.

Test signals: Trace `statx` with basic, all, and individual masks; verify generated names and hex fallback for unknown bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx_mask.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx_mask.sh

Purpose: Generates the `STATX_*` mask bit table.

Important APIs/types/functions: It reads the beauty copy of `uapi/linux/stat.h` and emits `static const char *statx_mask[]`.

Control flow: The script matches hex `STATX_*` definitions, filters `STATX_ALL`, `STATX_BASIC_STATS`, and `STATX_ATTR_*`, and indexes each remaining bit as `ilog2(value) + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `statx.c`.

Risks: Composite masks and attribute masks are deliberately excluded. Decimal or expression-valued definitions are ignored.

Test signals: Regenerate and confirm entries for core statx request bits; compile and trace statx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx_mask.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.c

Purpose: Formats `sync_file_range(2)` flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_sync_file_range_flags` delegates to `sync_file_range__scnprintf_flags`, which recognizes the composite `SYNC_FILE_RANGE_WRITE_AND_WAIT` before formatting individual bits.

Control flow: The formatter first checks whether the input contains the full write-and-wait composite and prints that name while clearing the component bits. It then appends remaining flags through `strarray__scnprintf_flags`.

State and persistence: Stateless formatting.

Dependencies and integration points: Includes generated `sync_file_range_arrays.c`, Linux fs flags, and perf beauty helpers.

Risks: Composite-first output can produce no separator before later flags depending on `strarray__scnprintf_flags` behavior with a non-empty destination; tests should catch formatting around mixed composite and extra bits.

Test signals: Trace zero, wait-before, write, wait-after, full write-and-wait, and unknown flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.sh

Purpose: Generates individual `SYNC_FILE_RANGE_*` flag names.

Important APIs/types/functions: It parses `fs.h` and emits `static const char *sync_file_range_flags[]`.

Control flow: Optional header directory selection is followed by a regex for hex/digit flag values and `ilog2(value) + 1` entry formatting.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `sync_file_range.c`, whose C logic handles the composite write-and-wait alias.

Risks: Composite or zero-valued definitions would not be handled as desired by the generated bit table.

Test signals: Regenerate and verify wait/write bit entries; compile and trace `sync_file_range`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/syscalltbl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/syscalltbl.sh

Purpose: Generates C syscall-number lookup tables for all supported architectures.

Important APIs/types/functions: `build_tables` reads one syscall table and emits `syscall_num_to_name_<machine>[]` and `syscall_sorted_names_<machine>[]`. `build_outer_table` emits entries for the final `static const struct syscalltbl syscalltbls[]`.

Control flow: The script validates two arguments, removes the output file, writes common C definitions, then conditionally appends table definitions for alpha, arm, arm64, csky, mips, parisc, powerpc, riscv, s390, sh, sparc, x86, xtensa, and a generic `EM_NONE`. `build_tables` filters table rows by ABI, sorts by number for direct lookup, and sorts by padded syscall name for binary/name lookup behavior consistent with runtime string comparison.

State and persistence: It writes directly to the requested output header and uses a temporary file for sorted intermediate rows.

Dependencies and integration points: Consumed by perf trace syscall name resolution. Depends on kernel `tools/perf/arch/*/entry/syscalls` tables, `scripts/syscall.tbl`, `grep`, `sort`, `awk`, and `sed`.

Risks: Direct output writes are not atomic. ABI filter lists must track kernel table changes. The name-padding sort workaround is fragile for unusual names.

Test signals: Run generator with the tools directory and compile the generated header under native and `ALL_SYSCALLTBL` builds; verify number-to-name and sorted-name lookups for representative architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/syscalltbl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/timespec.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/timespec.c

Purpose: Formats `struct timespec *` syscall arguments when augmented user memory is available.

Important APIs/types/functions: `syscall_arg__scnprintf_timespec` prints either a structured `{ .tv_sec, .tv_nsec }` value or the raw pointer. `syscall_arg__scnprintf_augmented_timespec` does the structured rendering.

Control flow: The wrapper tests `arg->augmented.args`; present augmented data is cast to `struct timespec`, absent data falls back to hex pointer formatting.

State and persistence: Reads only captured syscall memory; no persistent state.

Dependencies and integration points: Depends on syscall augmentation, `struct timespec`, and `PRIu64` formatting.

Risks: The code assumes captured bytes are large enough for `struct timespec` and prints fields as unsigned 64-bit values. ABI time-size differences may need care on 32-bit builds.

Test signals: Trace syscalls with timespec pointers with augmentation on/off; test NULL and invalid pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/timespec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.c

Purpose: Formats and parses x86 IRQ vector numbers for tracepoint fields.

Important APIs/types/functions: `syscall_arg__scnprintf_x86_irq_vectors` maps vectors to names using generated `x86_arch_irq_vectors_array.c`; `syscall_arg__strtoul_x86_irq_vectors` parses symbolic input back to numeric values.

Control flow: Formatting calls `strarray__scnprintf_suffix` with `_VECTOR` suffix semantics. Parsing calls `strarray__strtoul`.

State and persistence: Stateless static lookup tables only.

Dependencies and integration points: Consumed by perf tracepoint beauty code for x86 vector fields; generated by `x86_irq_vectors.sh`.

Risks: Only generated vectors are named; unknown vector values use numeric fallback. Suffix formatting must match names generated without `_VECTOR`.

Test signals: Generate from x86 irq header, format known vectors such as local timer and spurious vectors, and parse symbolic names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.sh

Purpose: Generates x86 IRQ vector names for tracepoint beautification.

Important APIs/types/functions: It emits `static const char *x86_irq_vectors[]` by reading `irq_vectors.h`.

Control flow: The script resolves `FIRST_EXTERNAL_VECTOR` to its numeric value, substitutes it into the header stream, matches `NAME_VECTOR 0xNN` definitions, sorts by vector number, and formats array entries without the `_VECTOR` suffix.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `x86_irq_vectors.c`.

Risks: It only handles simple hex defines. If useful vector definitions become expressions beyond `FIRST_EXTERNAL_VECTOR`, they may be omitted.

Test signals: Regenerate and verify expected vector names; compile tracepoint formatter and parse/format known values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_irq_vectors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.c

Purpose: Formats and parses x86 model-specific register numbers for tracepoints.

Important APIs/types/functions: It defines three string arrays: low MSRs, x86-64-specific MSRs with an offset, and AMD-V/KVM MSRs with an offset. `syscall_arg__scnprintf_x86_MSR` formats through `strarrays__scnprintf`; `syscall_arg__strtoul_x86_MSR` parses with `strarrays__strtoul`.

Control flow: Formatting searches the grouped tables in order and falls back to hex. Parsing searches the same grouped tables.

State and persistence: Static generated lookup tables only.

Dependencies and integration points: Includes `x86_arch_MSRs_array.c` generated by `x86_msr.sh` and integrates with x86 tracepoint beauty formatting.

Risks: The generator intentionally covers selected MSR numeric ranges, so many valid MSRs may remain numeric. Overlapping definitions require exclusion handling in the script.

Test signals: Format and parse low, x86-64-specific, and AMD/KVM MSR names; verify unknown MSRs remain numeric.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.sh

Purpose: Generates selected x86 MSR lookup arrays.

Important APIs/types/functions: It emits `x86_MSRs[]`, `x86_64_specific_MSRs_offset`, `x86_64_specific_MSRs[]`, `x86_AMD_V_KVM_MSRs_offset`, and `x86_AMD_V_KVM_MSRs[]`.

Control flow: The first pass captures `MSR_*` values in the `0x00000...` range with exclusions for clashing/noisy entries. The second pass captures `0xc0000...` x86-64-specific values and excludes `K6_WHCR`. The third captures `0xc0010...` AMD-V/KVM values. Offset tables use the lowest matching value as the base.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `x86_msr.c`.

Risks: Coverage is intentionally partial for simple arrays. New ranges need new generated arrays or a different data structure.

Test signals: Regenerate against `msr-index.h`, compile, and verify names from all three ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/usbdevfs_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/usbdevfs_ioctl.sh

Purpose: Generates USBDEVFS ioctl command names.

Important APIs/types/functions: It parses `USBDEVFS_*` definitions in `usbdevice_fs.h` and emits `static const char *usbdevfs_ioctl_cmds[]`. It also emits a disabled `#if 0` block for 32-bit variants.

Control flow: The main regex handles `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `_IOC`-style macros with type `U`, filters `USBDEVFS_*32` commands, sorts entries, and prints them. A second pass emits the disabled 32-bit table.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_usbdevfs_cmd` in `ioctl.c`, selected when fd major is USB device major.

Risks: USBDEVFS shares ioctl type letter `U` with ALSA control, so consumer fd classification is required. Disabled 32-bit table means compat-specific names may not be used.

Test signals: Regenerate and trace common USBDEVFS ioctls on a USB device fd; verify ALSA control fds still use `SNDRV_CTL_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/usbdevfs_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/vhost_virtio_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/vhost_virtio_ioctl.sh

Purpose: Generates vhost/virtio ioctl command name tables.

Important APIs/types/functions: It emits `vhost_virtio_ioctl_cmds[]` for non-read or write-only commands and `vhost_virtio_ioctl_read_cmds[]` for commands with read direction.

Control flow: Two regex passes over `vhost.h` match `VHOST_*` macros using `VHOST_VIRTIO` and hexadecimal command numbers. The read table specifically matches `_IOWR`/read-containing forms so the C consumer can disambiguate by `_IOC_READ`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_vhost_virtio_cmd` in `ioctl.c`.

Risks: Direction-sensitive command names depend on the regex split matching kernel macros exactly. Non-hex command numbers or helper macros would be missed.

Test signals: Regenerate and trace vhost fd ioctls with read and write directions; verify the C consumer selects the expected table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/vhost_virtio_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/waitid_options.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/waitid_options.c

Purpose: Formats `waitid` option flags.

Important APIs/types/functions: `syscall_arg__scnprintf_waitid_options` recognizes `WNOHANG`, `WUNTRACED`, and `WCONTINUED`.

Control flow: A macro-driven sequence appends recognized options with optional `W` prefix and clears them; remaining bits print as hex.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<sys/wait.h>` and the perf trace `SCA_WAITID_OPTIONS` binding.

Risks: It covers only a subset of wait flags relevant to waitid-style calls. Platform-specific wait bits print numerically.

Test signals: Trace wait calls with zero, individual, combined, and unknown option bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/waitid_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/x86_arch_prctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/x86_arch_prctl.sh

Purpose: Generates lookup tables for x86 `arch_prctl` codes split by numeric ranges.

Important APIs/types/functions: The `print_range` shell function emits an offset macro and a `static const char *x86_arch_prctl_codes_<n>[]` array for codes with prefixes `0x1`, `0x2`, and `0x4`.

Control flow: The script selects the x86 UAPI asm directory, then calls `print_range` three times with base offsets `0x1001`, `0x2001`, and `0x4001`. Each pass parses `ARCH_*` definitions and formats index expressions relative to the first entry.

State and persistence: stdout-only generator.

Dependencies and integration points: The generated arrays are consumed by x86 arch-prctl beauty code elsewhere in the perf tree.

Risks: Codes outside the three hard-coded ranges will be omitted. Regex only handles simple hex definitions.

Test signals: Regenerate and verify entries such as `ARCH_SET_GS`, `ARCH_SET_FS`, and newer arch-prctl codes from each range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/x86_arch_prctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browser.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browser.c

Purpose: Implements the generic S-Lang text UI browser used by perf TUI views.

Important APIs/types/functions: Public functions in `browser.h` are implemented here: color selection, coordinate helpers, list/rbtree/argv seeking and refresh, title/helpline lifecycle, scrolling, event loop handling, warnings/help/dialogs, resize handling, color config, vertical lines, jump arrows, fused-instruction marks, and `ui_browser__init`.

Control flow: `ui_browser__show` initializes dimensions, title, and helpline under `ui__lock`. `ui_browser__run` repeatedly refreshes, reads keys, handles resize and navigation, updates `index`, `top_idx`, `top`, and `horiz_scroll`, and returns unhandled command keys to callers. Refresh delegates row writing to the browser-specific callback and then draws scrollbar/fill/no-samples UI.

State and persistence: State is held in `struct ui_browser`: current index, top entry, dimensions, title, helpline, current color, filters, and navigation flags. Configured colors are loaded from perf config into static color-set descriptors and S-Lang state.

Dependencies and integration points: Depends on S-Lang wrappers, perf UI locks, helpline stack, key symbols, Linux list/rbtree helpers, and perf config. Specialized browsers set callbacks and call this event loop.

Risks: Seeking callbacks must preserve `top`/`top_idx` invariants or navigation can assert or render wrong entries. List filtering assumes at least one unfiltered entry when entries exist. Terminal resize and lock ordering are important for TUI stability.

Test signals: Exercise list, rb-tree, and argv browsers; simulate navigation keys, resize, empty data, filtering, horizontal scroll, and color config. Run perf TUI annotate/header views under S-Lang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browser.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browser.h

Purpose: Declares the generic perf TUI browser abstraction and helper API.

Important APIs/types/functions: `struct ui_browser` carries navigation state, geometry, callbacks (`refresh_dimensions`, `refresh`, `write`, `seek`, `filter`), content metadata, and UI strings. The header declares color constants, drawing helpers, modal helpers, event loop functions, and ready-made backends for argv, rb-tree, and list-head data.

Control flow: The header has no runtime control flow, but its callback contract drives all browser implementations: callers provide data traversal and row rendering, while `browser.c` owns common navigation and display.

State and persistence: Browser instances store transient TUI state only. Titles and helplines are allocated/freed by show/hide.

Dependencies and integration points: Included by perf TUI modules such as annotation, header, hists, and data-type browsers. It depends on Linux integer types and standard varargs/types.

Risks: Callback signature misuse can corrupt browser state. `u16` dimensions and `u32 nr_entries` constrain maximum visible metadata but are adequate for terminal UI.

Test signals: Compile all TUI users, instantiate each backend type, and run navigation/resizing paths that use the declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate-data.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate-data.c

Purpose: Implements a TUI browser for annotated data types, showing per-field memory-access overhead in a foldable type tree.

Important APIs/types/functions: `struct browser_entry` represents one visible or foldable type member. `struct annotated_data_browser` embeds `ui_browser`. Key routines collect entries from `annotated_data_type`, aggregate per-byte histograms with `get_member_overhead`, traverse foldable trees, render overhead/type fields, toggle fold state, and expose `hist_entry__annotate_data_tui`.

Control flow: Collection recursively builds browser entries from `adt->self` and member children, adds synthetic closing-brace entries, folds by default, and counts visible rows. The browser seek/next/prev logic traverses visible folded state rather than the raw list. Runtime key handling supports navigation through the generic browser plus `e` and `E` fold toggles.

State and persistence: Browser state includes entry tree, current entry, visible entry counts, fold flags, and per-event histogram aggregates. It is allocated per invocation and freed before return.

Dependencies and integration points: Integrates with perf hist entries, grouped evsels, `annotated_data_type`, `type_hist`, symbol display options, and the generic `ui_browser`.

Risks: Recursive allocation failure can leak children already built because intermediate error cleanup is limited. `browser__write_overhead` initializes `nr_samples` to zero instead of using histogram samples, which affects sample-count display.

Test signals: Open data annotation on types with nested fields, empty event groups, skipped-empty events, fold/unfold recursively, and sample/period/percent display modes. Use leak checks on allocation-failure injection if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate.c

Purpose: Implements the main perf TUI annotation browser for disassembled symbols, source interleaving, hottest-instruction navigation, jump visualization, searching, and optional data-type display.

Important APIs/types/functions: `struct annotate_browser` embeds `ui_browser` and tracks current hot rb-node, selected annotation line, architecture, hist entry, debuginfo, evsel, type hash, and search state. Public entry points are `hist_entry__tui_annotate` and `__hist_entry__tui_annotate`. Major helpers render rows, calculate percent rb-trees, toggle source, jump/call to targets, search forward/backward, update titles, and manage debuginfo/type hash state.

Control flow: Entry initializes S-Lang tty state, ensures the symbol is annotated, configures browser callbacks, optionally selects a requested address, then enters `annotate_browser__run`. The run loop refreshes via the generic browser, recalculates hot lines for timers, handles many command keys, calls nested annotation for call targets, toggles source and display options, and exits on navigation/quit keys. Jump arrows are drawn after list refresh using current selection and local target lookup.

State and persistence: It mutates global annotation options, symbol annotation caches, hist decay state, helpline stack, optional static `annotate_he` copy for perf top, debuginfo handles, and an in-memory type hash. It writes annotation dumps only when the user presses `P`.

Dependencies and integration points: Deeply integrated with perf symbol/disassembly, map/dso/thread, hists/evsel, annotation writing, debuginfo, branch counters, script browser, and `ui_browser`.

Risks: The file has many stateful UI paths; stale selection after source toggles, rb-node invalidation after timer recalculation, and perf-top lifetime handling are key hazards. Source reannotation purges and rebuilds lists, so index preservation is delicate.

Test signals: TUI annotate a symbol with and without source, with timers, branch counters, jump arrows, searches, call targets, source toggling, offset/full-address toggles, type display with/without debuginfo, and perf top. Validate no use-after-free with repeated nested call navigation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/header.c

Purpose: Provides a TUI window for browsing perf session header information.

Important APIs/types/functions: `tui__header_window` is the public entry. `ui__list_menu` creates a generic argv-backed browser. `list_menu__run` handles the header browser event loop. `ui_browser__argv_write` renders one line with horizontal offset support.

Control flow: `tui__header_window` writes `perf_header__fprintf_info` into an `open_memstream`, counts newline-separated rows, builds an argv array by replacing newlines with NULs, and passes it to the list menu. The menu uses generic browser navigation, `LEFT`/`RIGHT` adjust the horizontal offset stored in `browser->priv`, help shows a static key list, and quit returns.

State and persistence: All state is transient: the memstream buffer, argv vector, and horizontal offset. No header data is modified.

Dependencies and integration points: Depends on perf session/header printing, generic `ui_browser` argv backend, key symbols, and S-Lang UI helpers.

Risks: If `open_memstream` fails, `fp` is not checked before use in this snapshot. The newline count drives allocation and assumes final parsing produces `argc + 1` positions, guarded by `BUG_ON`.

Test signals: Open header windows for normal and unusual perf.data files, exercise horizontal scrolling, help, resize, and exit paths. Test allocation/open_memstream failure where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/header.c -->
