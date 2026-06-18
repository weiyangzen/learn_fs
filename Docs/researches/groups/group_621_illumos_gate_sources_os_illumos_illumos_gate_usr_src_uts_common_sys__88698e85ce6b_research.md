# Group Research: group_621_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__88698e85ce6b

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time.h

## Purpose
Core illumos time header for timeval-based APIs, interval timers, high-resolution kernel time, tick/time conversions, and user-visible `gettimeofday`/`settimeofday` compatibility declarations.

## Main Interfaces
- Defines `time_t`, `suseconds_t`, `struct timeval`, `struct timezone`, `struct itimerval`, `struct itimerval32`, `todinfo_t`, and `hrtime_t`.
- Provides 32-bit conversion and overflow macros for `timeval` and `itimerval`.
- Defines timer utility macros: `timerisset`, `timercmp`, `timerclear`, `timeradd`, `timersub`, plus `TIMESPEC_TO_TIMEVAL` and `TIMEVAL_TO_TIMESPEC`.
- Defines interval timer IDs `ITIMER_REAL`, `ITIMER_VIRTUAL`, `ITIMER_PROF`, and `ITIMER_REALPROF`.
- Defines time constants and conversions between seconds, milliseconds, microseconds, nanoseconds, ticks, `timeval`, and `timestruc`.
- Kernel declarations include TOD/high-resolution clock routines such as `tod_get`, `tod_set`, `gethrtime`, `gethrestime`, `hrt2ts`, `ts2hrt`, `itimerfix`, and DTrace tick hooks.
- User declarations cover `adjtime`, `getitimer`, `setitimer`, `utimes`, `futimes`, `lutimes`, `gettimeofday`, `settimeofday`, `gethrtime`, and `gethrvtime`.

## Dependencies And Relationships
Includes `sys/types32.h`, `sys/types.h`, `sys/time_impl.h`, and kernel-only `sys/mutex.h`; user extensions pull in `time.h` and `sys/select.h`. It is the public bridge between POSIX/SVr4 time structures and kernel high-resolution time internals.

## Research Notes
The header is careful about standards exposure and 32-bit ABI conversion. Reviewers should treat the tick conversion macros as kernel-facing arithmetic helpers tied to globals like `hz`, `nsec_per_tick`, and `usec_per_tick`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_impl.h

## Purpose
Implementation-level time definitions shared by kernel and user headers, centered on POSIX `timespec`, `itimerspec`, clock IDs, and timer flags.

## Main Interfaces
- Defines `time_t` when not already provided.
- Defines `struct timespec`, `timestruc_t`, and `struct itimerspec`.
- Provides 32-bit conversion and overflow macros for `timespec` and `itimerspec`.
- Defines `timestruc` as an SVr4 alias for `timespec`.
- Defines clock IDs: `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, `CLOCK_PROCESS_CPUTIME_ID`, `CLOCK_VIRTUAL`, plus alternate names `CLOCK_HIGHRES` and `CLOCK_PROF`.
- Defines `CLOCK_MAX`, `TIMER_RELTIME`, and `TIMER_ABSTIME`.

## Dependencies And Relationships
Includes `sys/feature_tests.h` and, outside assembly, `sys/types32.h`. It is included by `sys/time.h` and timer-related headers that need stable clock/timer structure definitions without all of `sys/time.h`.

## Research Notes
This file owns the ABI-visible clock constants and 32-bit structure shims, so changes here affect libc, kernel timer code, and compatibility layers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_std_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_std_impl.h

## Purpose
Small standards-oriented time implementation header defining minimal `time_t` and underscored timespec structures.

## Main Interfaces
- Defines `time_t` when needed.
- Defines `_timespec` with `tv_sec` and `tv_nsec`.
- Defines `_timestruc_t` as the SVr4-compatible alias for `_timespec`.

## Dependencies And Relationships
Includes `sys/feature_tests.h`. This is a narrower companion to `time_impl.h` for standards namespace management where public names should be guarded.

## Research Notes
The file deliberately uses underscored type names to avoid exposing broader implementation details in stricter compilation environments.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_std_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timeb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timeb.h

## Purpose
Legacy System V/BSD `ftime(3C)` interface header.

## Main Interfaces
- Defines `struct timeb` with seconds, milliseconds, timezone offset, and DST flag.
- Declares `ftime(struct timeb *)`.

## Dependencies And Relationships
Includes `sys/types.h` for `time_t`. This is a compatibility header for old applications rather than a preferred time API.

## Research Notes
The interface is obsolete relative to `gettimeofday`, `clock_gettime`, and related APIs, but remains ABI-relevant for legacy source compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timeb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timer.h

## Purpose
Kernel timer implementation header for per-process POSIX timers, clock backends, old sigevent compatibility, and timespec helper routines.

## Main Interfaces
- Defines `_TIMER_MAX` and `_TIMER_ALLOC_INIT` for per-process timer arrays.
- Defines interval timer lock flags `ITLK_LOCKED`, `ITLK_WANTED`, and `ITLK_REMOVE`.
- Defines notification flags `IT_SIGNAL` and `IT_PORT`.
- Defines `itimer_t`, `struct itimer`, and `clock_backend_t`.
- `struct itimer` carries timer ID, process/LWP links, lock state, overrun accounting, sigevent data, backend pointer, and fire callback.
- `clock_backend_t` provides clock and timer method vectors for set/get/resolution/create/settime/gettime/delete/LWP binding.
- Declares backend registration and timer routines such as `clock_add_backend`, `clock_get_backend`, `timer_exit`, `timer_lwpexit`, `hzto`, `timespectohz`, `itimerspecfix`, `timespecadd`, `timespecsub`, and `xgetitimer`/`xsetitimer`.
- Defines `struct oldsigevent` and `struct oldsigevent32` for compatibility.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/proc.h`, `sys/thread.h`, and `sys/param.h`. It is consumed by kernel timer, signal, event port, and clock backend code.

## Research Notes
The design separates generic POSIX timer state from pluggable clock backend operations, allowing different clock IDs to supply their own implementation while sharing process timer bookkeeping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timerfd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timerfd.h

## Purpose
Timer file descriptor ABI header providing Linux-compatible timerfd constants and illumos ioctl commands.

## Main Interfaces
- Defines `TFD_CLOEXEC`, `TFD_NONBLOCK`, `TFD_TIMER_ABSTIME`, and `TFD_TIMER_CANCEL_ON_SET`.
- Defines timerfd ioctl base `TIMERFDIOC` and commands `TIMERFDIOC_CREATE`, `TIMERFDIOC_SETTIME`, and `TIMERFDIOC_GETTIME`.
- Defines `timerfd_settime_t` with file descriptor, flags, and `itimerspec`.
- User declarations include `timerfd_create`, `timerfd_settime`, and `timerfd_gettime`.
- Kernel minor names include `TIMERFDMNRN_TIMERFD` and `TIMERFDMNRN_CLONE`.
- Defines `TIMERFD_VALMAX` and Linux monotonic clock value `TIMERFD_MONOTONIC`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/time_impl.h`. It links the public libc timerfd calls to the kernel timerfd pseudo-device/ioctl implementation.

## Research Notes
The constants intentionally mirror Linux flag values where needed for compatibility, while the actual kernel interface is ioctl-based.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timerfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/times.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/times.h

## Purpose
Header for process CPU accounting returned by `times(2)`.

## Main Interfaces
- Defines `struct tms` with user, system, children-user, and children-system clock counters.
- Defines `struct tms32` for 32-bit ABI compatibility.
- Declares `clock_t times(struct tms *)`.

## Dependencies And Relationships
Includes `sys/types.h` for `clock_t`. Used by libc/syscall interfaces and process accounting code.

## Research Notes
This is a small, stable POSIX interface; the main compatibility concern is preserving `clock_t` sizing across native and 32-bit ABIs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/times.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timex.h

## Purpose
Network Time Protocol clock discipline interface and kernel timing parameter definitions.

## Main Interfaces
- Defines PLL/FLL scaling constants, phase/frequency limits, PPS averaging/watchdog constants, and leap status values.
- Defines mode flags such as `MOD_OFFSET`, `MOD_FREQUENCY`, `MOD_MAXERROR`, `MOD_ESTERROR`, `MOD_STATUS`, `MOD_TIMECONST`, `MOD_CLKA`, and `MOD_CLKB`.
- Defines status flags such as `STA_PLL`, `STA_PPSFREQ`, `STA_PPSTIME`, `STA_FLL`, `STA_INS`, `STA_DEL`, `STA_UNSYNC`, and read-only PPS/error bits.
- Defines `struct ntptimeval`, `struct ntptimeval32`, and `struct timex`.
- Declares `ntp_gettime` and `ntp_adjtime`.
- Kernel declarations include `clock_update` and `ddi_hardpps`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/syscall.h`, and `sys/inttypes.h`. It supports NTP adjustment syscalls and kernel hard-PPS discipline.

## Research Notes
The file encodes illumos’ NTP discipline ABI. Consumers should distinguish writable adjustment modes from read-only status/error bits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timod.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timod.h

## Purpose
STREAMS Transport Interface module ioctl and synchronization definitions.

## Main Interfaces
- Defines `TIMOD` ioctl base and commands including `TI_GETINFO`, `TI_OPTMGMT`, `TI_BIND`, `TI_UNBIND`, `TI_GETMYNAME`, `TI_GETPEERNAME`, `TI_SYNC`, `TI_GETADDRS`, and `TI_CAPABILITY`.
- Defines `struct ti_sync_req` and `struct ti_sync_ack`.
- Defines sync request flags such as `TSRF_INFO_REQ`, `TSRF_IS_EXP_IN_RCVBUF`, and `TSRF_QLEN_REQ`.
- Defines `TSAF_EXP_QUEUED` acknowledgement flag.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/stream.h`. Used by the TLI/XTI STREAMS module to coordinate user-level transport library state with provider state.

## Research Notes
The header is internal STREAMS/TLI plumbing. Its structures are small but ABI-sensitive because ioctl payloads cross the user/kernel boundary.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tirdwr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tirdwr.h

## Purpose
Placeholder public header for the `tirdwr` STREAMS module.

## Main Interfaces
- Contains only include guards and C++ linkage wrappers.
- Exposes no structures, constants, or prototypes.

## Dependencies And Relationships
Historically associated with the TLI read/write compatibility STREAMS module. It remains available for source compatibility.

## Research Notes
This is intentionally empty API surface; its value is preserving include compatibility for legacy transport applications.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tirdwr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tiuser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tiuser.h

## Purpose
User-level Transport Interface/TLI definitions for connection-oriented and connectionless transport programming.

## Main Interfaces
- Defines TLI event flags such as `T_LISTEN`, `T_CONNECT`, `T_DATA`, `T_EXDATA`, `T_DISCONNECT`, `T_UDERR`, and `T_ORDREL`.
- Defines send/receive flags `T_MORE` and `T_EXPEDITED`.
- Defines data structures `struct t_info`, `struct netbuf`, `struct netbuf32`, `struct t_bind`, `struct t_optmgmt`, `struct t_discon`, `struct t_call`, `struct t_unitdata`, and `struct t_uderr`.
- Defines allocation structure IDs `T_BIND`, `T_OPTMGMT`, `T_CALL`, `T_DIS`, `T_UNITDATA`, `T_UDERROR`, and `T_INFO`.
- Defines field masks `T_ADDR`, `T_OPT`, `T_UDATA`, `T_ALL`.
- Defines TLI states `T_UNINIT`, `T_UNBND`, `T_IDLE`, `T_OUTCON`, `T_INCON`, `T_DATAXFER`, `T_OUTREL`, `T_INREL`, and `T_BADSTATE`.
- Declares the classic TLI API: `t_open`, `t_bind`, `t_accept`, `t_connect`, `t_listen`, `t_rcv`, `t_snd`, `t_rcvudata`, `t_sndudata`, `t_optmgmt`, `t_sync`, `t_unbind`, `t_close`, and related routines.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/tpicommon.h`. It is the public TLI consumer header layered over common TPI error, service type, and option definitions.

## Research Notes
This is a legacy networking API. The structures are used both for library allocations and syscall/ioctl mediation, so field layout compatibility matters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tiuser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tl.h

## Purpose
Transport loopback option and ioctl definitions for peer credential retrieval.

## Main Interfaces
- Defines transport loopback protocol option level `TL_PROT_LEVEL`.
- Defines `TL_OPT_PEER_CRED` and `TL_OPT_PEER_UCRED`.
- Defines `tl_credopt_t`, which carries credential option metadata.
- Defines ioctl base `TL_IOC` and credential option ioctls `TL_IOC_CREDOPT` and `TL_IOC_UCREDOPT`.

## Dependencies And Relationships
Used by local transport/loopback STREAMS modules and consumers needing peer credentials or `ucred` access over local endpoints.

## Research Notes
The file is narrowly focused on local transport credential passing; `TL_OPT_PEER_UCRED` is the richer modern form.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/todio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/todio.h

## Purpose
TOD device ioctl command definitions.

## Main Interfaces
- Defines ioctl base `TOD_IOC`.
- Defines commands `TOD_GET_DATE`, `TOD_SET_ALARM`, and `TOD_CLEAR_ALARM`.

## Dependencies And Relationships
Used by time-of-day clock drivers and consumers issuing TOD device ioctls.

## Research Notes
This header only defines command numbers; payload structure is determined by the driver-side ioctl implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/todio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tpicommon.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tpicommon.h

## Purpose
Common Transport Provider Interface definitions shared by TLI/XTI headers.

## Main Interfaces
- Defines TPI/TLI error constants including `TBADADDR`, `TBADOPT`, `TACCES`, `TBADF`, `TNOADDR`, `TOUTSTATE`, `TBADSEQ`, `TSYSERR`, `TLOOK`, `TBUFOVFLW`, `TFLOW`, `TNOTSUPPORT`, `TPROTO`, and others.
- Defines service types `T_COTS`, `T_COTS_ORD`, `T_CLTS`, and `T_RDMA`.
- Defines option management flags `T_NEGOTIATE`, `T_CHECK`, `T_DEFAULT`, `T_SUCCESS`, `T_FAILURE`, `T_CURRENT`, `T_PARTSUCCESS`, `T_READONLY`, and `T_NOTSUPPORT`.
- Defines boolean and size sentinel constants such as `T_YES`, `T_NO`, `T_INFINITE`, `T_INVALID`, and `T_UNSPEC`.
- Defines `struct opthdr` plus `OPTLEN` and `OPTVAL` helpers for option buffers.

## Dependencies And Relationships
Includes `sys/feature_tests.h`. Included by `tiuser.h` and related transport headers to centralize common constants.

## Research Notes
The file is mostly ABI constants. Additions must avoid colliding with historical XTI/TLI values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tpicommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ts.h

## Purpose
Kernel header for the time-sharing scheduler class state and dispatch table entries.

## Main Interfaces
- Defines `tsdpent_t`, a dispatch table entry containing global priority, quantum, priority adjustment values, and maximum wait.
- Defines `tsproc_t`, per-thread time-sharing class state including CPU usage, user priority, nice-derived priority limits, interactive state, quantum, flags, thread pointer, and list links.
- Defines class flags such as `TSBACKQ`, `TSIA`, `TSIASET`, `TSIANICED`, and `TSRESTORE`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/thread.h`, and `sys/cpucaps.h`. Used by the TS scheduler class implementation and priority control interfaces.

## Research Notes
The scheduler state separates configured dispatch policy (`tsdpent_t`) from per-thread dynamic state (`tsproc_t`), including interactive heuristics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label.h

## Purpose
Trusted Extensions label API definitions for binary labels, ranges, multilevel ports, and kernel label reference objects.

## Main Interfaces
- Declares opaque `m_label_t` and compatibility aliases `blevel_t`, `bclear_t`, `bslabel_t`, and related label types from label macro internals.
- Defines dominance/equality check constants and label names `ADMIN_LOW` and `ADMIN_HIGH`.
- Defines `m_range_t`/`blrange_t` for lower and upper label ranges.
- Defines multilevel port structures `tsol_mlp_t`, `tsol_mlp_entry_t`, and `tsol_mlp_list_t`.
- Defines `ts_label_t`, which combines a reference count, DOI, flags, and binary sensitivity label.
- Defines `DEFAULT_DOI` and label flags `TSLF_UNLABELED`, `TSLF_IMPLICIT_IN`, and `TSLF_IMPLICIT_OUT`.
- Provides macros `CR_SL` and `is_system_labeled`.
- Declares label comparison/manipulation functions such as `blequal`, `bldominates`, `blstrictdom`, `blinrange`, `blmaximum`, `blminimum`, `bsllow`, `bslhigh`, `bclearlow`, and `bclearhigh`.
- Declares kernel label allocation/reference routines: `label_init`, `labelalloc`, `labeldup`, `label_hold`, `label_rele`, `label2bslabel`, `label2doi`, and `label_equal`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cred.h`, `sys/vnode.h`, and `sys/tsol/label_macro.h`. Used by Trusted Extensions credential, vnode, networking, and policy enforcement code.

## Research Notes
The public-looking names wrap a compact binary label implementation in `label_macro.h`; reference-counted `ts_label_t` is the kernel object used to carry labels through credentials and network attributes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label_macro.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label_macro.h

## Purpose
Low-level Trusted Extensions binary label layout and macro operations.

## Main Interfaces
- Defines classification, compartment, marking, sensitivity label, CMW label, clearance, and label range implementation structures.
- Defines `NMLP_MAX`, `NSLS_MAX`, label type IDs, classification bounds `LOW_CLASS` and `HIGH_CLASS`, and empty/universal bit sets.
- Defines type/access macros such as `_MTYPE`, `_MSETTYPE`, `_MGETTYPE`, `_MEQUAL`, `LCLASS`, `LCLASS_SET`, `ICLASS`, and `ICLASS_SET`.
- Defines label relation macros `BLTYPE`, `BLEQUAL`, `BLDOMINATES`, `BLSTRICTDOM`, and `BLINRANGE`.
- Defines label combination and initialization macros `BLMAXIMUM`, `BLMINIMUM`, `BCLLOW`, `BSLLOW`, `BSLHIGH`, `BILLOW`, `BCLEARLOW`, `BCLEARHIGH`, `BSLUNDEF`, and `BCLEARUNDEF`.
- Defines conversion macros such as `BCLTOSL`, `BCLTOIL`, `GETCSL`, `SETCSL`, `SETBLTYPE`, and `GETBLTYPE`.

## Dependencies And Relationships
Includes `sys/types.h`; included by `tsol/label.h` and other Trusted Extensions headers. It supplies the inlined primitive operations used by higher-level label APIs.

## Research Notes
This header is macro-heavy and layout-sensitive. It trades function calls for direct structure access, so type correctness and endian/bitset assumptions matter when modifying labels.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label_macro.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/priv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/priv.h

## Purpose
Trusted Extensions compatibility privilege header mapping old privilege macros and names to illumos privilege sets.

## Main Interfaces
- Defines `priv_ftype` for file privilege typing.
- Maps legacy macros such as `PRIV_ASSERT`, `PRIV_CLEAR`, `PRIV_EQUAL`, `PRIV_EMPTY`, `PRIV_FILL`, `PRIV_ISASSERT`, `PRIV_ISEMPTY`, `PRIV_ISFULL`, `PRIV_ISSUBSET`, `PRIV_INTERSECT`, `PRIV_INVERSE`, and `PRIV_UNION` onto `priv_*set` operations.
- Defines Trusted Extensions privilege name aliases including file label upgrade/downgrade, audit, translated labels, and window-system privileges.

## Dependencies And Relationships
Includes `sys/priv.h`. Used by older TSOL-aware code that expects historical privilege macro names.

## Research Notes
Most content is compatibility mapping. The privilege names are string constants passed into the regular illumos privilege framework.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tndb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tndb.h

## Purpose
Trusted network database definitions for remote host templates, CIPSO options, multilevel ports, caches, and labeled network lookup helpers.

## Main Interfaces
- Defines `tnaddr_t` for IPv4/IPv6 addresses and helpers for comparing addresses.
- Defines database operation enum `tsol_dbops_t`.
- Defines remote host entries/string forms `tsol_rhent_t` and `tsol_rhstr_t`.
- Defines CIPSO constants, tag type 1 structure, and `cipso_option_t`.
- Defines well-known Trusted Solaris classifications and compartment authority bits.
- Defines template strings such as `TP_UNLABELED`, `TP_CIPSO`, `TP_ZONE`, `TP_HOSTTYPE`, `TP_DOI`, `TP_DEFLABEL`, `TP_MINLABEL`, `TP_MAXLABEL`, and `TP_SET`.
- Defines template structures for unlabeled and CIPSO hosts, collected in `tsol_tpent_t` and `tsol_tpstr_t`.
- Defines multilevel port entry `tsol_mlpent_t` and zone cache entry `tsol_zcent_t`.
- Defines cached template and remote-host cache objects `tsol_tpc_t` and `tsol_tnrhc_t`, with hold/release macros.
- Defines cache sizing and hashing macros for IPv4/IPv6 address and mask lookup.
- Declares `tnrhc_free`, `tpc_free`, `find_tpc`, `tcache_init`, `tsol_next_port`, `tsol_mlp_port_type`, `tsol_mlp_findzone`, `tsol_mlp_anon`, `tsol_print_label`, `rtsa_validate`, `gcgrp_lookup`, `gcgrp_inactive`, and `tnrh_load`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/zone.h`, TSOL label headers, and networking headers. Used by Trusted Extensions network policy, routing security attributes, and multilevel port enforcement.

## Research Notes
This is the central TSOL labeled-network data model. It combines persistent database concepts with in-kernel reference-counted caches, so lifetime macros are as important as structure layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tndb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tnet.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tnet.h

## Purpose
Trusted Extensions labeled networking function declarations.

## Main Interfaces
- Defines `TSOL_MAX_IPV6_OPTION`.
- Declares host/template lookup and checking routines such as `tsol_tnrh_chk` and `find_rhc`.
- Declares IPv4/IPv6 security option manipulation routines: `tsol_prepend_option`, `tsol_prepend_option_v6`, `tsol_remove_secopt`, and `tsol_remove_secopt_v6`.
- Declares gateway security attribute allocation/free and initialization helpers.
- Declares packet label and receive-attribute routines such as `tsol_get_pkt_label`, `tsol_attr_to_zoneid`, `tsol_get_option_v4`, and `tsol_get_option_v6`.
- Declares routing/forwarding helpers including `tsol_ire_match_gwattr`, `tsol_rtsa_init`, `tsol_ire_init_gwattr`, `tsol_ip_forward`, and `tsol_pmtu_adjust`.

## Dependencies And Relationships
Includes STREAMS, TSOL label/database headers, IPv4/IPv6, IP, and routing headers. It is consumed by IP stack code enforcing labeled networking rules.

## Research Notes
The header separates database/cache definitions in `tndb.h` from packet-path operations that add, strip, inspect, and route security label options.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tnet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tsyscall.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tsyscall.h

## Purpose
Trusted Extensions syscall subcommand number definitions.

## Main Interfaces
- Defines `TSOL_SYSLABELING`, `TSOL_TNRH`, `TSOL_TNRHTP`, `TSOL_TNMLP`, `TSOL_GETLABEL`, and `TSOL_FGETLABEL`.

## Dependencies And Relationships
Used by the Trusted Extensions syscall dispatcher and user/kernel request routing for label and trusted-network database operations.

## Research Notes
This is a command-number header only; argument structures live in other TSOL headers and syscall implementation files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tsyscall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tspriocntl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tspriocntl.h

## Purpose
Priority-control definitions for the time-sharing scheduler class.

## Main Interfaces
- Defines `tsparms_t` with user priority limit and user priority.
- Defines `tsinfo_t` with maximum user priority.
- Defines `TS_NOCHANGE`.
- Defines key IDs `TS_KY_UPRILIM` and `TS_KY_UPRI`.
- Defines admin payloads `tsadmin32_t` and `tsadmin_t` for dispatch table management.
- Defines admin commands `TS_GETDPSIZE`, `TS_GETDPTBL`, and `TS_SETDPTBL`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/thread.h`; relies on `struct tsdpent` from the TS scheduler class. Used by `priocntl` administration for the time-sharing class.

## Research Notes
The 32-bit and native admin structures differ in how dispatch table pointers are represented, so consumers must use the correct command ABI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tspriocntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttcompat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttcompat.h

## Purpose
State definitions for the STREAMS terminal compatibility module handling old tty ioctls.

## Main Interfaces
- Defines compatibility message/state structures holding old and new tty settings, ioctl state, and transparent ioctl bookkeeping.
- Uses legacy tty structures such as `sgttyb`, `tchars`, and `ltchars`.
- Defines state flags `TS_FREE`, `TS_INUSE`, `TS_W_IN`, `TS_W_OUT`, `TS_IOCWAIT`, and `TS_TIOCNAK`.

## Dependencies And Relationships
Works with old tty definitions in `ttold.h` and modern STREAMS/termios code. It supports conversion between legacy BSD/SVr3 terminal ioctls and current terminal behavior.

## Research Notes
This header is compatibility plumbing. The state flags reflect multi-step STREAMS ioctl translation rather than direct device operation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttcompat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttold.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttold.h

## Purpose
Legacy BSD/SVr3 terminal structure, ioctl, mode, and line discipline definitions.

## Main Interfaces
- Defines old terminal character structures `struct tchars`, `struct tc`, `struct sgttyb`, `struct ltchars`, and `struct winsize`.
- Defines old tty ioctl command base `tIOC` and commands such as `TIOCGETD`, `TIOCSETD`, `TIOCGETP`, `TIOCSETP`, `TIOCSETN`, `TIOCSETC`, `TIOCGETC`, `TIOCLBIS`, `TIOCLBIC`, `TIOCLSET`, `TIOCLGET`, `TIOCSBRK`, `TIOCCBRK`, `TIOCGWINSZ`, and `TIOCSWINSZ`.
- Defines old mode bits including hangup, tab expansion, lowercase simulation, echo, CR mapping, raw mode, parity, newline/tab/CR/VT/BS delays, tandem flow control, cbreak, local CRT erase modes, literal output, background stop, no-flush, and pass-8.
- Defines local mode aliases such as `LCRTBS`, `LPRTERA`, `LCRTERA`, `LMDMBUF`, `LLITOUT`, `LTOSTOP`, `LNOFLSH`.
- Defines line discipline constants `OTTYDISC`, `NETLDISC`, `NTTYDISC`, `TABLDISC`, `NTABLDISC`, `MOUSELDISC`, and `KBDLDISC`.

## Dependencies And Relationships
Used by tty compatibility code, especially `ttcompat.h`, to support programs using pre-termios terminal interfaces.

## Research Notes
This file preserves many obsolete constants. New code should use termios, but compatibility modules need these exact values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttold.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tty.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tty.h

## Purpose
Common STREAMS tty state header.

## Main Interfaces
- Defines `tty_common_t` with flags, termios settings, and window size.
- Defines `TS_XCLUDE` and `TS_SOFTCAR`.
- Declares `ttycommon_close`, `ttycommon_qfull`, and `ttycommon_ioctl`.

## Dependencies And Relationships
Includes `sys/stream.h` and `sys/termios.h`. Used by STREAMS terminal drivers that share common termios/window-size handling.

## Research Notes
This is a compact helper interface for tty drivers, not a full terminal subsystem definition.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttychars.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttychars.h

## Purpose
Default legacy tty special character definitions.

## Main Interfaces
- Defines `struct ttychars` with erase, kill, interrupt, quit, start/stop, EOF, break, suspend, delayed suspend, reprint, flush, word erase, literal-next, and status characters.
- Defines `CTRL(c)` and defaults such as `CERASE`, `CKILL`, `CINTR`, `CQUIT`, `CSTART`, `CSTOP`, `CEOF`, `CBRK`, `CSUSP`, `CDSUSP`, `CRPRNT`, `CFLUSH`, `CWERASE`, `CLNEXT`, and `CSTATUS`.

## Dependencies And Relationships
Used by legacy terminal code and compatibility layers that need old default control-character values.

## Research Notes
The constants are historical defaults and should not be confused with modern termios configurable indexes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttychars.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttydev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttydev.h

## Purpose
Legacy tty baud-rate constant definitions.

## Main Interfaces
- Defines speed constants from `B0` through `B38400`.
- Defines aliases `EXTA` and `EXTB`.

## Dependencies And Relationships
Used by old tty interfaces and compatibility code; modern terminal code usually gets speed constants through termios.

## Research Notes
The values are compact legacy encodings rather than literal bit-per-second values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttydev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tuneable.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tuneable.h

## Purpose
Kernel tunable structure definition for historical VM/system parameters.

## Main Interfaces
- Defines `struct tune` with tunable fields including maximum process size, core size, stack size, and other system sizing values.
- Defines `GETPGSMSK` as `PG_REF | PG_NDREF`.

## Dependencies And Relationships
Used by old kernel code and compatibility paths expecting a `tune` structure. It relates to VM/page flag handling through `GETPGSMSK`.

## Research Notes
This is largely historical; modern illumos tunables are typically handled through more specific subsystem variables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tuneable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/turnstile.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/turnstile.h

## Purpose
Kernel priority-inheritance turnstile structure and operation declarations.

## Main Interfaces
- Defines queue indexes `TS_WRITER_Q`, `TS_READER_Q`, and `TS_NUM_Q`.
- Defines opaque `turnstile_t` and `struct turnstile`.
- `struct turnstile` contains sleep queues for reader/writer waiters, inheritor thread, owner sobj, free-list pointer, lock, and block timestamp.
- Declares `turnstile_lookup`, `turnstile_exit`, `turnstile_wakeup`, `turnstile_change_pri`, `turnstile_unsleep`, `turnstile_stay_asleep`, and `turnstile_pi_recalc`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/param.h`, `sys/sleepq.h`, `sys/mutex.h`, and `sys/lwp_timer_impl.h`. Used by synchronization object implementations that need blocking queues and priority inheritance.

## Research Notes
Turnstiles are shared synchronization infrastructure; their reader/writer queue split supports both exclusive and shared synchronization objects.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/turnstile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types.h

## Purpose
Foundational illumos system type header defining scalar aliases, ABI-sized types, synchronization public structures, file/process/device identifiers, time types, limits, and compatibility aliases.

## Main Interfaces
- Defines common aliases such as `longlong_t`, `u_longlong_t`, `t_scalar_t`, `t_uscalar_t`, `uchar_t`, `ushort_t`, `uint_t`, `ulong_t`, `caddr_t`, `daddr_t`, `cnt_t`, and `ptrdiff_t`.
- Defines memory/storage and filesystem types including `pfn_t`, `pgcnt_t`, `spgcnt_t`, `off_t`, `off64_t`, `ino_t`, `blkcnt_t`, `fsblkcnt_t`, `fsfilcnt_t`, and their 64-bit forms.
- Defines `boolean_t` plus boolean conversion helpers.
- Defines alignment/padding unions and integer aliases for 32/64-bit ABI cleanliness.
- Defines identifiers including `id_t`, `lgrp_id_t`, `major_t`, `minor_t`, `pri_t`, old UID/device/inode types, `key_t`, `mode_t`, `uid_t`, `gid_t`, `datalink_id_t`, `taskid_t`, `projid_t`, `poolid_t`, `zoneid_t`, and `ctid_t`.
- Defines public pthread-compatible structures for mutexes, condition variables, rwlocks, once objects, attributes, and spinlocks.
- Defines `dev_t`, `nlink_t`, `pid_t`, `size_t`, `ssize_t`, `time_t`, `clock_t`, `clockid_t`, and `timer_t`.
- Defines limits such as `CHAR_BIT`, integer min/max values, `OFF_MIN`, `OFF_MAX`, and sentinel values `P_MYPID`, `P_MYID`, `NOPID`, `NODEV`, `NODEV32`, `PFN_INVALID`, and `PFN_SUSPENDED`.
- Includes `sys/select.h` at the end for legacy exposure requirements.

## Dependencies And Relationships
Includes `sys/feature_tests.h`, `sys/isa_defs.h`, `sys/machtypes.h`, integer type headers, and `sys/types32.h`. Almost every kernel and user-facing system header depends directly or indirectly on this file.

## Research Notes
This file is standards- and ABI-conditional throughout. Many typedefs vary by `_LP64`, large-file settings, XPG/POSIX feature macros, and kernel visibility, so changes here have broad compatibility impact.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types32.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types32.h

## Purpose
Fixed-width 32-bit ABI companion types for use by 64-bit kernels and compatibility code.

## Main Interfaces
- Defines 32-bit address, disk, offset, inode, block count, ID, device, key, mode, UID/GID, link count, PID, size, time, clock, and pointer integer aliases.
- Defines `struct timeval32`, `timespec32_t`, `timestruc32_t`, and `struct itimerspec32`.

## Dependencies And Relationships
Includes `sys/int_types.h`. Used by 64-bit kernel code translating ILP32 system call arguments and structures.

## Research Notes
This header is strictly layout-oriented; its definitions should remain fixed-width and independent of native compilation model.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tzfile.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tzfile.h

## Purpose
Time zone file format and calendrical constant definitions.

## Main Interfaces
- Defines zoneinfo paths and defaults: `TZDIR`, `TZDEFAULT`, and `TZDEFRULES`.
- Defines `struct tzhead`, the on-disk time zone file header.
- Defines maximum counts for transitions, types, abbreviations, and leap corrections.
- Defines calendar constants for seconds/minutes/hours/days/months, weekday and month indexes, epoch year/weekday, and `isleap`.
- Provides alternate uppercase constant names such as `SECS_PER_MIN`, `MINS_PER_HOUR`, and `DAYS_PER_LYEAR`.

## Dependencies And Relationships
Used by timezone parsing and libc time conversion code that reads zoneinfo files.

## Research Notes
The file reflects the historical tzfile layout and should be kept aligned with timezone data reader expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tzfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep.h

## Purpose
UTF-8/Unicode conversion, validation, comparison, and normalization option definitions.

## Main Interfaces
- Defines Unicode conversion endian/BOM/null handling flags for UTF-8, UTF-16, and UTF-32 conversion.
- Declares `uconv_u16tou8`, `uconv_u32tou8`, `uconv_u8tou16`, and `uconv_u8tou32`.
- Defines string comparison and normalization flags for case-sensitive/case-insensitive comparison, canonical/compatibility decomposition, canonical composition, NFD/NFC/NFKD/NFKC, uppercase/lowercase mapping, ignore-null, ignore-invalid, and no-wait behavior.
- Defines Unicode version selectors `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST`.
- Defines validation flags and illegal/out-of-range character sentinel values.
- Declares `u8_validate`, `u8_strcmp`, and kernel-only text preparation routines.

## Dependencies And Relationships
Includes `sys/isa_defs.h`, `sys/types.h`, and `sys/errno.h`. Used by filesystem/name handling and other consumers needing Unicode-normalized string behavior.

## Research Notes
The API combines conversion and normalization controls. Callers must choose flags carefully because comparison can imply normalization and case conversion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uadmin.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uadmin.h

## Purpose
Administrative reboot, shutdown, dump, suspend, remount, fast reboot, and boot-configuration command definitions.

## Main Interfaces
- Defines `uadmin` command values such as `A_REBOOT`, `A_SHUTDOWN`, `A_FREEZE`, `A_REMOUNT`, `A_DUMP`, `A_FTRACE`, `A_SWAPCTL`, `A_SDTTEST`, and `A_CONFIG`.
- Defines action values such as `AD_HALT`, `AD_BOOT`, `AD_IBOOT`, `AD_SBOOT`, `AD_SIBOOT`, `AD_POWEROFF`, `AD_NOSYNC`, `AD_FASTREBOOT`, and `AD_FASTREBOOT_DRYRUN`.
- Defines suspend/CPR actions including `AD_COMPRESS`, `AD_FORCE`, `AD_CHECK`, `AD_SUSPEND_TO_DISK`, `AD_SUSPEND_TO_RAM`, and reusable-state actions.
- Defines fast reboot SMF FMRI/property names and flags `UA_FASTREBOOT_DEFAULT` and `UA_FASTREBOOT_ONPANIC`.
- Kernel declarations include `mdboot`, `mdpreboot`, `kadmin`, and `killall`.
- User declaration exposes `uadmin(int, int, uintptr_t)`.

## Dependencies And Relationships
Includes `sys/types.h` and kernel-only `sys/cred.h`. Used by system administration tools, kernel reboot paths, crash dump handling, CPR, and boot configuration management.

## Research Notes
This header is command-number central for privileged system lifecycle operations; command/action combinations are interpreted in kernel administrative paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uadmin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ucred.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ucred.h

## Purpose
User credential export structure and helper macros for process credentials, privileges, audit data, and labels.

## Main Interfaces
- Defines `struct ucred_s` with total size and offsets to embedded credential, privilege, audit, and label records.
- Defines accessor macros `UCCRED`, `UCPRIV`, `UCAUD`, and `UCLABEL`.
- Defines `UCREDSYS_UCREDGET` and `UCREDSYS_GETPEERUCRED` syscall subcommands.
- Defines kernel/user size macros for serialized `ucred` payloads.
- Declares `ucredminsize`, `pgetucred`, `get_audit_ucrsize`, and `_ucred_alloc`.

## Dependencies And Relationships
Includes process credential, privilege, TSOL label, and audit headers. Used by `getpeerucred`, procfs-style exported credentials, and local transport credential reporting.

## Research Notes
The structure is an offset-based packed export format. Consumers should use access macros rather than assuming fixed embedded offsets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ucred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uio.h

## Purpose
Scatter/gather I/O vector and kernel `uio` definitions for read/write movement, async direct-copy support, and extended zero-copy I/O.

## Main Interfaces
- Defines `iovec_t`/`struct iovec` and `struct iovec32`.
- Defines `uio_seg_t` address-space enum values `UIO_USERSPACE`, `UIO_SYSSPACE`, and `UIO_USERISPACE`.
- Defines `uio_t` with iovec pointer/count, offset, segment flag, residual count, file limit, and flags.
- Defines `uioa_page_t`, `uioa_t`, `xuio_t`, `xuio_type`, and XUIO zero-copy helper macros.
- Defines `uio_rw_t` with `UIO_READ` and `UIO_WRITE`.
- Defines `UIO_COPY_DEFAULT`, `UIO_COPY_CACHED`, `UIO_ASYNC`, and `UIO_XUIO`.
- Defines `uioasync_t` global capability state.
- Kernel declarations include `uiomove`, `uio_prefaultpages`, `uiocopy`, `ureadc`, `uwritec`, `uioskip`, `uiodup`, `uioamove`, `uioainit`, and `uioafini`.
- User declarations expose `readv`, `writev`, `preadv`, `pwritev`, and large-file `preadv64`/`pwritev64` variants.

## Dependencies And Relationships
Includes `sys/feature_tests.h` and `sys/types.h`. Used by VFS, device drivers, filesystems, and libc scatter/gather APIs.

## Research Notes
The header is a key boundary between user scatter/gather ABI and kernel data movement. Large-file remapping and `uio_offset` layout are compilation-environment dependent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ulimit.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ulimit.h

## Purpose
Legacy `ulimit(2)` command definitions.

## Main Interfaces
- Defines command constants for querying and setting file size and related process limits, including historical forms such as `UL_GETFSIZE`, `UL_SETFSIZE`, `UL_GMEMLIM`, `UL_GDESLIM`, and `UL_GTXTOFF`.

## Dependencies And Relationships
Used by libc and syscall compatibility for the legacy `ulimit` interface. Modern code generally uses `getrlimit`/`setrlimit`.

## Research Notes
This header preserves old command values for source and binary compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ulimit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/un.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/un.h

## Purpose
UNIX-domain socket address definition.

## Main Interfaces
- Defines `sa_family_t` when not already defined.
- Defines `struct sockaddr_un` with `sun_family` and `sun_path[108]`.
- Under extension visibility, declares `strlen` as needed and defines `SUN_LEN`.
- Kernel-only declaration includes `unp_discard`.

## Dependencies And Relationships
Used by AF_UNIX socket APIs and kernel UNIX-domain protocol code. The public version is also normally exposed through socket-related headers.

## Research Notes
The comment notes illumos does not use a BSD-style `sun_len` field, so `SUN_LEN` is based on family size plus path length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/un.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unistd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unistd.h

## Purpose
Implementation-specific constants behind public `unistd.h`, especially `confstr`, `sysconf`, `pathconf`, and standards feature values.

## Main Interfaces
- Defines `confstr` names such as `_CS_PATH`, large-file build options, XBS5, and POSIX V6 compilation environments.
- Defines many `sysconf` names for POSIX, SVR4, XPG, realtime, threads, hardware cache/CPU properties, UNIX 98/03/08 features, IPv6, and raw sockets.
- Defines `pathconf` names for path/name limits, async/prioritized/synchronized I/O, allocation transfer sizes, symlink behavior, ACLs, case behavior, system attributes, timestamp resolution, file size bits, and extended attributes.
- Defines related values such as `_PC_LAST`, `_CASE_SENSITIVE`, `_CASE_INSENSITIVE`, `_ACL_ACLENT_ENABLED`, and `_ACL_ACE_ENABLED`.
- Defines standards version and support macros including `_POSIX_VERSION`, `_POSIX2_VERSION`, `_XOPEN_XPG3`, `_XOPEN_XPG4`, `_XOPEN_UNIX`, `_XOPEN_REALTIME`, `_XOPEN_ENH_I18N`, `_XOPEN_SHM`, and POSIX2 capability flags.

## Dependencies And Relationships
Includes `sys/feature_tests.h`. This file explicitly warns applications to include public `<unistd.h>` instead; it is the implementation constant source used by libc and system headers.

## Research Notes
The numeric `_SC`, `_PC`, and `_CS` values are externally observable through `sysconf`, `pathconf`, and `confstr`, so additions must preserve existing values and update consumers like tracing tools when required.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unix_bb_info.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unix_bb_info.h

## Purpose
Kernel boot black-box information structure definition.

## Main Interfaces
- Defines `NMI_LEVEL`.
- Defines `struct bb_info` with linked-list pointer and boot/debug metadata fields.

## Dependencies And Relationships
Used by low-level kernel/platform code that records black-box information for diagnostics.

## Research Notes
This is a small diagnostic data structure header; its consumers are platform/kernel internals rather than public APIs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unix_bb_info.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ac/usb_ac.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ac/usb_ac.h

## Purpose
Private/shared header for the USB audio control driver coordinating audio-control, audio-streaming, HID controls, mixer, power management, and plumbed stream state.

## Main Interfaces
- Declares `usb_ac_open`, `usb_ac_close`, `usb_audio_attach`, `usb_ac_get_audio`, `usb_ac_send_audio`, and `usb_ac_stop_play`.
- Defines unit and plumbing structures such as `usb_ac_unit_list_t`, `usb_ac_plumbed_t`, `usb_ac_to_as_req_t`, `usb_ac_streams_info_t`, and `usb_ac_power_t`.
- Defines audio format and engine structures `usb_audio_format_t` and `usb_audio_eng_t`.
- Defines `usb_audio_ctrl_t` for mixer/control state.
- Defines central `usb_ac_state_t`/`struct usb_ac_state` with DDI/USB handles, descriptors, streams, plumbed endpoints, power state, audio control lists, format/engine data, and synchronization state.
- Defines state and flag constants for plumbed/unplumbed restore states, default open state, plumbed stream types, registration/setup, stereo control packing, and gain limits.

## Dependencies And Relationships
Includes `sys/sunldi.h`, `sys/sysmacros.h`, and `sys/usb/usba/usbai_private.h`. It works with `usb_audio.h`, `usb_as.h`, `usb_ah.h`, and `usb_mixer.h` in the USB audio client stack.

## Research Notes
This header is the integration point for USB audio control. It tracks topology units and plumbs child audio streaming/HID pieces into a single audio device view.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ac/usb_ac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ah/usb_ah.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ah/usb_ah.h

## Purpose
USB audio HID helper state header for audio button/report handling.

## Main Interfaces
- Defines report indexes `USB_AH_INPUT_RPT`, `USB_AH_OUTPUT_RPT`, and `USB_AH_FEATURE_RPT`.
- Defines state flags `USB_AH_OPEN` and `USB_AH_QWAIT`.
- Defines `usb_ah_button_descr_t`, `usb_ah_rpt_t`, and `usb_ah_state_t`.
- `usb_ah_state_t` tracks STREAMS queues, report data, USB pipe/request state, mutex/CV synchronization, and HID report descriptors.
- Defines `USB_AH_TIMEOUT`.

## Dependencies And Relationships
Includes `sys/stream.h`. Used by the USB audio HID client that handles hardware audio buttons and related HID reports.

## Research Notes
The state includes a small fixed report array for input, output, and feature reports, reflecting the narrow HID usage in audio controls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ah/usb_ah.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_as/usb_as.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_as/usb_as.h

## Purpose
USB audio streaming driver state header for playback/recording streams, alternate settings, isochronous requests, and stream power state.

## Main Interfaces
- Defines queue watermarks `USB_AS_HIWATER` and `USB_AS_LOWATER`.
- Defines `usb_as_alt_descr_t` for alternate interface/audio format metadata.
- Defines `usb_as_power_t` for power management state.
- Defines central `usb_as_state_t` with USB handles, interface descriptors, pipes, queues, transfer state, format state, taskq arguments, power state, and synchronization.
- Defines taskq argument `usb_as_tq_arg_t` and request wrapper `usb_as_req_t`.
- Defines default availability values, send-result values, stream states such as idle/active/paused/stop-polling, request counts, open/dismantling flags, buffer size, and minor number helpers.

## Dependencies And Relationships
Includes `sys/usb/usba/usbai_private.h`. Cooperates with `usb_ac.h` for control-driver coordination and `usb_mixer.h` for audio framework registration.

## Research Notes
The header models USB audio streaming around alternate interface descriptors and isochronous request management, with explicit play-pause and stop-polling states.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_as/usb_as.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_audio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_audio.h

## Purpose
USB Audio Class descriptor, request, control, format, terminal, and debug constant definitions.

## Main Interfaces
- Defines USB audio class-specific descriptor types for device, configuration, string, interface, and endpoint descriptors.
- Defines AudioControl subtype constants for header, input/output terminal, mixer, selector, feature, processing, and extension units.
- Defines AudioStreaming subtype constants and processing-unit subtype constants.
- Defines class request constants `USB_AUDIO_SET_CUR`, `GET_CUR`, `SET_MIN`, `GET_MIN`, `SET_MAX`, `GET_MAX`, `SET_RES`, `GET_RES`, `SET_MEM`, `GET_MEM`, and `GET_STAT`.
- Defines feature/control selector constants for mute, volume, bass, treble, AGC, delay, loudness, sampling frequency, pitch, and processing-specific controls.
- Defines descriptor structures for AC headers, terminals, mixer units, selector units, feature units, processing units, extension units, associated interfaces, AS interfaces, isochronous endpoints, and type 1 format descriptors.
- Defines descriptor unpack format strings and sizes used by USB descriptor parsing.
- Defines audio format constants for PCM/PCM8/IEEE float/ALAW/MULAW, MPEG/AC, IEC1937 variants, and format type IDs.
- Defines many terminal type constants for streaming, microphones, speakers, telephony, connectors, and media devices.
- Defines debug print masks, packet size bounds, mute values, and precision values.

## Dependencies And Relationships
Consumed by USB audio control/streaming/mixer drivers as the shared class-specification vocabulary. Other USB audio headers refer to these descriptor and selector values.

## Research Notes
This is a specification-mapping header: most values are USB Audio Class wire constants, and descriptor structures match parsed USB configuration data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_audio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_mixer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_mixer.h

## Purpose
USB audio mixer registration and request definitions shared with audio streaming/control code.

## Main Interfaces
- Defines `USB_AUDIO_MIXER_REGISTRATION`.
- Defines `usb_audio_formats_t`, `usb_audio_play_req_t`, and `usb_as_registration_t`.
- Defines maximum format count `USB_AS_N_FORMATS`.
- Defines mixer/audio operation commands such as setup, teardown, start/stop/pause play, start/stop record, set format, and set sample frequency.
- Defines control-change IDs for volume, balance, mute, bass, and treble.

## Dependencies And Relationships
Used by USB audio components to register streaming capabilities and issue control/playback requests through the mixer/audio framework integration.

## Research Notes
The header is a compact contract between USB audio streaming and mixer control code rather than a USB wire-format header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_mixer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/ccid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/ccid.h

## Purpose
USB CCID smart-card class protocol constants, descriptor layout, parameter structures, interrupt messages, command/response codes, and status/error definitions.

## Main Interfaces
- Defines class voltage, mechanical feature, class feature, and PIN support enums.
- Defines `ccid_class_descr_t`, matching the CCID class descriptor.
- Defines CCID version helpers and descriptor type/length constants.
- Defines protocol parameter structures `ccid_params_t0_t`, `ccid_params_t1_t`, and union `ccid_params_t`.
- Defines sequence range constants `CCID_SEQ_MIN` and `CCID_SEQ_MAX`.
- Defines interrupt slot and hardware error structures plus interrupt code enums.
- Defines request codes for host-to-reader messages and response codes for reader-to-host messages.
- Defines `ccid_header_t` and `ccid_data_clock_t`.
- Defines reply ICC/status extraction macros and enums for ICC status, command status, and command errors.
- Defines `CCID_APDU_LEN_MAX`.

## Dependencies And Relationships
Includes `sys/stdint.h`. Used by the kernel CCID driver and user ioctl layer to build and parse USB CCID messages.

## Research Notes
The structures mirror USB CCID wire formats and use fixed-width integer types. Command status and ICC status are packed into response bytes, so helper macros should be used for decoding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/ccid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/uccid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/uccid.h

## Purpose
User-facing ioctl ABI for the USB CCID smart-card driver.

## Main Interfaces
- Defines APDU and ATR maximum sizes.
- Defines ioctl base `UCCID_IOCTL`, version constants, and current version.
- Defines transaction commands `UCCID_CMD_TXN_BEGIN` and `UCCID_CMD_TXN_END` with flags for nonblocking, reset, and release behavior.
- Defines status command `UCCID_CMD_STATUS` and status flags for card presence, active card, product, serial, and parameters validity.
- Defines ICC modification command `UCCID_CMD_ICC_MODIFY` and actions for power on, power off, and warm reset.
- Defines payload structures `uccid_cmd_txn_begin_t`, `uccid_cmd_txn_end_t`, `uccid_cmd_status_t`, and `uccid_cmd_icc_modify_t`, plus status enum.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/usb/clients/ccid/ccid.h`. It is the user/kernel ABI layer above the lower-level CCID USB protocol definitions.

## Research Notes
The ioctl structs carry version fields, which allows future ABI extension while preserving current command numbers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/uccid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid.h

## Purpose
USB HID descriptor, request, report, protocol, event, and ioctl definitions.

## Main Interfaces
- Defines HID descriptor type and descriptor size constants.
- Defines HID class requests `HID_GET_REPORT`, `HID_GET_IDLE`, `HID_GET_PROTOCOL`, `HID_SET_REPORT`, `HID_SET_IDLE`, and `HID_SET_PROTOCOL`.
- Defines `usb_hid_descr_t` for HID class descriptors.
- Defines `hid_vid_pid_t` and `hid_req_t`.
- Defines maximum report data size and report type constants for input, output, and feature reports.
- Defines idle/protocol request lengths and boot/report protocol values.
- Defines control/event values such as `HID_GET_PARSER_HANDLE`, `HID_GET_VID_PID`, `HID_POWER_OFF`, `HID_FULL_POWER`, `HID_DISCONNECT_EVENT`, and `HID_CONNECT_EVENT`.
- Defines report descriptor type, HID version, ioctl base `HIDIOC`, and direct keyboard/mouse ioctls.

## Dependencies And Relationships
Includes `sys/note.h`. Used by USB HID client drivers and consumers that issue HID ioctls or parse HID descriptors.

## Research Notes
This header is a mix of USB HID wire constants and illumos HID driver control codes; the report type values include request direction/type encoding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid_polled.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid_polled.h

## Purpose
USB HID polled-input callback interface for low-level input polling.

## Main Interfaces
- Defines commands `HID_OPEN_POLLED_INPUT` and `HID_CLOSE_POLLED_INPUT`.
- Defines interface version `HID_POLLED_INPUT_V0`.
- Defines opaque `hid_polled_handle_t`.
- Defines `hid_polled_input_callback_t` with version, handle, argument, and callbacks for enter, exit, and input polling.

## Dependencies And Relationships
Used by HID keyboard/mouse paths that need polled input, such as console/debugger or early/low-level input contexts.

## Research Notes
The interface is callback-based and explicitly versioned, allowing HID providers to expose polling without publishing internal driver state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid_polled.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidminor.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidminor.h

## Purpose
USB HID minor number encoding helpers.

## Main Interfaces
- Defines masks and shifts for HID minor bits, ugen bits, and instance bits.
- Defines internal minor marker `HID_MINOR_INTERNAL`.
- Defines macros to mark/test internal opens, test ugen opens, extract instance numbers, and construct internal or external minors.

## Dependencies And Relationships
Used by the USB HID driver when creating and decoding device minor numbers for internal HID consumers and external generic USB access.

## Research Notes
The minor encoding reserves bit space for internal opens and ugen-style external opens, so all consumers should use these macros instead of hand-decoding minors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidminor.h -->