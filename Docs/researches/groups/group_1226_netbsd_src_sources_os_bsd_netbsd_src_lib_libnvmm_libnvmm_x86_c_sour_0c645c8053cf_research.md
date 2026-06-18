# Group Research: group_1226_netbsd_src_sources_os_bsd_netbsd_src_lib_libnvmm_libnvmm_x86_c_sour_0c645c8053cf

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Each listed source file was read completely and is reported below in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm_x86.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm_x86.c

## Purpose
Implements x86-specific userland assistance for NetBSD NVMM virtual CPUs. It provides VCPU state dumping, guest virtual-to-physical translation, I/O exit handling, memory/MMIO instruction decoding, and selected x86 instruction emulation.

## Main Interfaces
- `nvmm_vcpu_dump()` fetches full x64 state and prints GPRs, segments, EFER, and control registers.
- `nvmm_gva_to_gpa()` fetches CR/MSR state and translates a guest virtual address to guest physical address plus protection bits.
- `nvmm_assist_io()` handles `NVMM_VCPU_EXIT_IO`, including string I/O, REP counts, segment selection, direction flag behavior, and callback dispatch.
- `nvmm_assist_mem()` handles `NVMM_VCPU_EXIT_MEMORY` by fetching/decoding the instruction and emulating supported MMIO-touching operations.

## Address Translation
Contains walkers for 32-bit non-PAE paging, 32-bit PAE paging, and 64-bit paging. The 64-bit path validates canonical addresses and handles 1 GiB and 2 MiB large pages. Protection starts as `NVMM_PROT_ALL` and is narrowed as page-table entries clear user/write/execute permissions. Nonpaged mode maps GVA directly to GPA.

## Instruction Decode and Emulation
Uses a compact x86 decoder with legacy prefixes, REX prefixes, ModRM/SIB addressing, direct-memory offsets, immediates, displacements, and string-operation special cases. Supported operations include OR, AND, SUB, XOR, CMP, TEST, XCHG, MOV, MOVZX, MOVS, CMPS, STOS, and LODS. Unsupported instructions fail out of `nvmm_assist_mem()` with `ENODEV`.

## Control Flow and State
Guest memory access first translates GVA to GPA, then uses direct HVA memory if mapped or the VCPU memory callback for MMIO. Cross-page reads/writes recurse over page boundaries. Arithmetic/logical emulation uses inline assembly to reproduce x86 flags and then merges selected RFLAGS bits. REP/REPN/REPE handling decrements RCX-sized counters and advances RIP only when the repeat condition completes.

## Dependencies and Risks
Depends on NVMM kernel/user structures, x86 PTE and special-register definitions, `nvmm_vcpu_getstate/setstate`, `nvmm_gpa_to_hva`, and user-provided I/O and memory callbacks. Segment checks are explicitly incomplete, the decoder is intentionally narrow, and correctness is sensitive to operand/address-size handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm_x86.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/nvmm.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/nvmm.h

## Purpose
Public libnvmm userland API header. It wraps kernel NVMM ioctl types and declares userland machine, VCPU, mapping, state, run, assist, and x86 helper APIs.

## Main Contents
Defines `NVMM_USER_VERSION` as 2, declares `struct nvmm_machine`, `struct nvmm_vcpu`, `struct nvmm_io`, `struct nvmm_mem`, and `struct nvmm_assist_callbacks`, and exposes protection flags `NVMM_PROT_READ`, `WRITE`, `EXEC`, `USER`, and `ALL`.

## Interfaces
Declares initialization, capability, machine lifecycle, VCPU lifecycle/configuration/state/run/inject, GPA/HVA mapping, GVA-to-GPA and GPA-to-HVA translation, I/O and memory assist, control ioctl wrapper, VCPU dump, and VCPU stop functions.

## Dependencies
Includes `<dev/nvmm/nvmm.h>` and `<dev/nvmm/nvmm_ioctl.h>`, so low-level IDs, state layouts, exit records, and ioctl constants come from the kernel NVMM interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libnvmm/nvmm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/Makefile

## Purpose
Build definition for NetBSD `libossaudio`, the Open Sound System compatibility library.

## Main Contents
Builds library `ossaudio` with `WARNS=5`, installs `ossaudio.3`, compiles `oss_caps.c`, `oss_dsp.c`, `oss_ioctl.c`, `oss3_mixer.c`, `oss4_mixer.c`, and `oss4_global.c`, and installs `soundcard.h` into `/usr/include`.

## Integration Notes
The library supports the public header’s `ioctl` redirection to `_oss_ioctl`, which dispatches OSS commands to NetBSD audio/mixer translations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/internal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/internal.h

## Purpose
Private shared header for `libossaudio` implementation files.

## Main Contents
Includes real ioctl declarations and `soundcard.h`, then undefines `ioctl` so implementation files can call the system ioctl. Defines OSS/NetBSD volume conversion macros, `INTARG`, mixer command device extraction, hidden symbol visibility, and declarations for `_oss_ioctl()` plus DSP, caps, OSSv3 mixer, OSSv4 mixer, and OSSv4 global dispatchers.

## Integration Notes
This is the internal boundary between the public OSS compatibility ABI and NetBSD `<sys/audioio.h>` operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss3_mixer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss3_mixer.c

## Purpose
Implements OSSv3 mixer ioctl compatibility on top of NetBSD `AUDIO_MIXER_*` and `AUDIO_GETDEV`.

## Main Interfaces
`_oss3_mixer_ioctl()` handles OSS version, mixer info, recording source reads/writes, device masks, recording masks, stereo masks, caps, and per-device volume reads/writes. Helper functions discover NetBSD mixer controls and map enum/set opaque values to local indexes.

## Control Flow
`getdevinfo()` caches one mixer device identity using `fstat()`, scans up to 64 NetBSD mixer controls, maps known NetBSD labels to OSS mixer device codes, records stereo support, and locates `AudioNsource` for recording-source masks. The ioctl handler then translates OSS bitmasks and packed volume fields to NetBSD mixer values.

## Risks and Notes
The cache is a single static cache, not per descriptor or thread-local. Mixer controls beyond `NETBSD_MAXDEVS` are unavailable. Set-style recording sources are collapsed into OSS bitmask semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss3_mixer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_global.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_global.c

## Purpose
Handles OSSv4 global song/name/label metadata ioctls.

## Main Interface
`_oss4_global_ioctl()` recognizes `SNDCTL_SETSONG`, `SNDCTL_GETSONG`, `SNDCTL_SETNAME`, `SNDCTL_SETLABEL`, and `SNDCTL_GETLABEL`, but returns `EINVAL` for each.

## Integration Notes
The file intentionally follows FreeBSD/Solaris-style no-op failure semantics because these metadata ioctls are not meaningfully supported or commonly used.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_global.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_mixer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_mixer.c

## Purpose
Implements OSSv4 audio-info, card-info, system-info, mixer-info, mixer-control, enum-info, read, and write ioctls using NetBSD audio and mixer device nodes.

## Main Interfaces
`_oss4_mixer_ioctl()` handles `SNDCTL_AUDIOINFO`, `SNDCTL_AUDIOINFO_EX`, `SNDCTL_ENGINEINFO`, `SNDCTL_CARDINFO`, `SNDCTL_SYSINFO`, `SNDCTL_MIXERINFO`, `SNDCTL_MIX_NRMIX`, `SNDCTL_MIX_NREXT`, `SNDCTL_MIX_EXTINFO`, `SNDCTL_MIX_ENUMINFO`, `SNDCTL_MIX_READ`, and `SNDCTL_MIX_WRITE`.

## Control Flow
Audio info opens `/dev/audioN`, fetches device identity, capabilities, formats, and maximum channels, then fills OSSv4 metadata. Mixer ext info creates a synthetic root control at control 0 because NetBSD lacks an OSS-style root mixer node; real NetBSD controls are exposed at `ctrl - 1`. Reads and writes translate NetBSD enum, set, and value controls to OSS integer values.

## Risks and Notes
Device discovery depends on sequential `/dev/audioN` and `/dev/mixerN` opens. NetBSD set controls are treated like single-choice enums because OSSv4 multi-enum support is not broadly usable. Many OSS fields are synthetic or best-effort.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_mixer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_caps.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_caps.c

## Purpose
Computes OSS DSP capability bits from NetBSD audio properties and current format.

## Main Interface
`_oss_get_caps(int fd, int *out)` calls `AUDIO_GETPROPS` and optionally `AUDIO_GETFORMAT`, then sets OSS `PCM_CAP_*` and channel-layout flags.

## Behavior
Always advertises trigger, multi-open, and free-rate support. Adds duplex, mmap, input, and output capability bits from NetBSD device properties. Adds mono, stereo, or multi-channel hints from the current playback or record format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_caps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_dsp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_dsp.c

## Purpose
Implements OSS DSP ioctl compatibility for audio playback and recording controls on top of NetBSD audio ioctls.

## Main Interfaces
`_oss_dsp_ioctl()` handles reset/sync, rate, stereo/channel count, sample format, block and fragment sizing, supported formats, buffer-space queries, nonblocking mode, caps, trigger state, input/output pointers, playback/record volume, duplex, delay, target/source names, and selected OSSv4 DSP queries.

## Translation Logic
Sample rates are clamped to 1000-192000. `encoding_to_format()` and `format_to_encoding()` translate between NetBSD encodings and OSS `AFMT_*` flags. Unsupported requested formats can fall back to current hardware format. Channel setting falls back to current hardware counts when the requested count fails. OSS packed volume pairs are converted to NetBSD gain/balance values.

## State and Risks
Maintains process-global cumulative playback/record error counters for `SNDCTL_DSP_GETERROR`. Several OSS calls are intentionally unimplemented and return `EINVAL`. Pointer/sample counters have comments noting possible wraparound.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_dsp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_ioctl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_ioctl.c

## Purpose
Public variadic ioctl replacement used by the OSS compatibility header.

## Main Interface
`_oss_ioctl(int fd, unsigned long com, ...)` extracts the single pointer argument and dispatches by `IOCGROUP(com)`: `'P'` to DSP translation, `'M'` to OSSv3 mixer, `'X'` to OSSv4 mixer, `'Y'` to OSSv4 global metadata, and all other groups to the real `ioctl`.

## Integration Notes
`soundcard.h` defines `ioctl` as `_oss_ioctl`, so OSS-compatible applications enter this dispatcher transparently after including the header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/oss_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/soundcard.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/soundcard.h

## Purpose
Public Open Sound System compatibility header for NetBSD.

## Main Contents
Defines OSS DSP ioctl numbers, audio format constants, native-endian aliases, mixer device IDs, mixer masks, OSSv3 structs, OSSv4 system/audio/card/mixer/enum/control structs, mixer types and flags, global song/name/label ioctls, and the `#define ioctl _oss_ioctl` compatibility hook.

## Integration Notes
The header is an ABI/source-compatibility surface for ported OSS applications and the constants source for `libossaudio` internals. It warns new NetBSD code to use `<sys/audioio.h>` instead.

## Risks and Notes
Many constants are documented as unsupported or unused on NetBSD but remain defined to compile existing OSS code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libossaudio/soundcard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libp2k/Makefile

## Purpose
Build definition for `libp2k`, the PUFFS-to-rump-kernel VFS bridge library.

## Main Contents
Builds library `p2k` from `p2k.c`, installs `p2k.h` under `/usr/include/rump`, installs `p2k.3`, links against `libpuffs`, `librump`, `librumpvfs`, and `libukfs`, and defines `_KERNTYPES`.

## Integration Notes
The dependencies match the library’s role translating PUFFS requests into rump-kernel VFS and vnode operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/p2k.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libp2k/p2k.c

## Purpose
Implements “puffs 2 kernel”: a bridge that converts PUFFS protocol operations into rump-kernel VFS and vnode operations, allowing kernel filesystem code to be mounted through a userland PUFFS server.

## Public Entry Points
`p2k_init()` initializes PUFFS operation tables, environment-driven debug/cache/wizard options, daemonization, rump, and lightweight process state. `p2k_setup_fs()` and `p2k_setup_diskfs()` mount regular or disk-backed filesystems. `p2k_run_fs()` and `p2k_run_diskfs()` combine init, setup, and mainloop. `p2k_mainloop()` runs PUFFS and releases the ukfs mount. `p2k_cancel()` cancels and frees setup state.

## Core State
`struct p2k_mount` stores the root vnode, PUFFS usermount, optional ukfs mount, vnode hash table, rump mount pointer, tmpfs/debug flags, and vnode count. `struct p2k_node` embeds a PUFFS node and stores the backing rump vnode. A 65536-bucket hash maps vnode pointers to p2k nodes.

## Credential and Mount Handling
PUFFS credentials are converted to rump `kauth_cred`. `P2K_WIZARDUID` can force all requests to a configured uid. `makelwp()` imports the PUFFS caller pid/lid into rump state. `setupfs()` builds PUFFS mount metadata, initializes ukfs, handles special `rumpfs` root redirection, obtains the root vnode, installs root p2k state, configures filehandle passthrough, stack size, callbacks, debug signal handling, and mounts PUFFS.

## VFS and Node Operations
Implements PUFFS fs operations for statvfs, unmount, sync, filehandle conversion, and extattr control. Implements node operations for lookup, create, mknod, open, close, access, getattr, setattr, fsync, mmap, seek, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, read, write, pathconf, extended attributes, inactive, and reclaim. Most handlers convert credentials/names, lock vnodes, call the matching `RUMP_VOP_*`, unlock, and release temporary state.

## Risks and Notes
Reference counting is central and delicate; the file explicitly compensates for operations that may consume vnode references. `p2k_node_inactive()` flushes cached vnode pages except for tmpfs, then calls `RUMP_VOP_INACTIVE` and may clear vnode knowledge if recycle is requested. Hashing by vnode pointer assumes stable vnode identity while mapped.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/p2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/p2k.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libp2k/p2k.h

## Purpose
Public header for `libp2k`.

## Main Contents
Declares opaque `struct p2k_mount` and APIs to run, initialize, cancel, set up, and enter the mainloop for p2k filesystems. Includes `rump/ukfs.h` for disk partition support.

## Integration Notes
Supports both one-shot `p2k_run_*` usage and staged `p2k_init()` plus setup plus `p2k_mainloop()` usage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libp2k/p2k.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/Makefile

## Purpose
Top-level build ordering for NetBSD OpenPAM library and modules.

## Main Contents
Defines subdirectories as `staticmodules .WAIT libpam .WAIT modules`.

## Integration Notes
Static modules are built before `libpam` because they are linked into static `libpam.a`; dynamic modules are built after `libpam` because they depend on the shared library.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/Makefile.inc

## Purpose
Shared build settings for libpam and PAM modules.

## Main Contents
Enables fortification by default, computes the PAM module install directory with `MLIBDIR` support, defines `OPENPAM_MODULES_DIRECTORY`, builds with `OPENPAM_STATIC_MODULES` for static support, removes that define for shared-library flags, sets shared-library major version 4, and forces installed OpenPAM files to be owned by root.

## Integration Notes
Centralizes module path, ownership, and static/dynamic build-mode behavior for the library and modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/Makefile

## Purpose
Build definition for NetBSD’s `libpam`, based on external OpenPAM sources plus NetBSD-local additions.

## Main Contents
Builds library `pam` with `SHLIB_MINOR=1`, `WARNS=6`, `HAVE_CONFIG_H`, OpenPAM core sources, public PAM API sources, and local `pam_debug_log.c`. Installs OpenPAM/PAM public headers and `security/pam_mod_misc.h`.

## Static Module Logic
Defines standard static modules and conditionally adds Kerberos and S/Key modules. Builds `openpam_static_modules.o` by whole-archiving configured static module libraries into a relocatable object used only by static libpam support.

## Integration Notes
This is the central bridge between NetBSD build infrastructure, vendored OpenPAM sources, and NetBSD-local PAM module additions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/config.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/config.h

## Purpose
Autoconf-style configuration header for OpenPAM as built in NetBSD.

## Main Contents
Defines available functions and headers such as `asprintf`, `vasprintf`, `fpurge`, `setlogmask`, `strlcat`, `strlcpy`, standard C headers, `libcrypt`, and `libcrypto`. Defines OpenPAM package metadata for version `20130907` and feature-test macros including `_ALL_SOURCE`, `_GNU_SOURCE`, `_POSIX_PTHREAD_SEMANTICS`, and `__EXTENSIONS__`.

## Integration Notes
For non-NetBSD builds it provides fallback `LIB_MAJ` and `LT_OBJDIR`; NetBSD normally supplies `LIB_MAJ` through build flags. It maps `restrict` to `__restrict`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_debug_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_debug_log.c

## Purpose
Provides verbose PAM error reporting for modules.

## Main Interface
`_pam_verbose_error()` checks `PAM_SILENT` and the OpenPAM `no_warn` option, formats a caller-supplied message with `vasprintf`, derives a module name from `__FILE__`, and emits the result through `pam_error()` with function context.

## Notes
If formatting allocation fails, the function silently returns. It is wired into modules through `PAM_VERBOSE_ERROR` in `pam_mod_misc.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_debug_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_std_option.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_std_option.c

## Purpose
Common parser and accessor helpers for standard PAM module options.

## Main Interfaces
`pam_std_option()` initializes an options table with standard and optional module-specific names, parses argv entries, records boolean presence and `name=value` arguments, and syslogs invalid options. `pam_test_option()` reads option state and argument. `pam_set_option()` and `pam_clear_option()` mutate standard option booleans.

## Standard Options
Includes `debug`, `no_warn`, `echo_pass`, `use_first_pass`, `try_first_pass`, mapped password options, and `expose_account`.

## Risks and Notes
Option argument strings are duplicated into the options structure; caller-side lifecycle management must account for those allocations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_std_option.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/security/pam_mod_misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/security/pam_mod_misc.h

## Purpose
Common helper header for PAM modules.

## Main Contents
Defines common option-name macros, declares `_pam_verbose_error()`, and provides macros for OpenPAM debug logging, direct return, and verbose error emission with `pamh`, `flags`, `__FILE__`, and `__func__`.

## Integration Notes
Installed with libpam headers and used by NetBSD PAM modules for logging and user-visible error reporting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/libpam/security/pam_mod_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/Makefile

## Purpose
Builds PAM module subdirectories.

## Main Contents
Lists standard module subdirectories, conditionally adds `pam_skey` when `MKSKEY` is enabled and Kerberos modules when `MKKERBEROS` is enabled, then adds `pam_ssh`.

## Integration Notes
Uses `<bsd.subdir.mk>` and is sequenced after `libpam` by the top-level Makefile for dynamic module builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/mod.mk -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/mod.mk

## Purpose
Shared Makefile fragment for PAM modules.

## Main Contents
Sets warning level 6, marks targets as loadable modules, also builds static and link libraries, disables link installation, includes shared PAM build settings, computes the security library install directory, and includes `<bsd.lib.mk>`.

## Integration Notes
Individual module Makefiles set `LIB`, `SRCS`, `MAN`, and optional libraries, then include this fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/mod.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/Makefile

## Purpose
Build definition for the `pam_afslog` module.

## Main Contents
Builds `pam_afslog` from `pam_afslog.c`, installs `pam_afslog.8`, and links Heimdal Kerberos/AFS libraries plus crypt and OpenSSL crypto.

## Integration Notes
Includes the shared PAM module build fragment after adding required Kerberos, AFS, and crypto dependencies.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/pam_afslog.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/pam_afslog.c

## Purpose
PAM credential module that can obtain or destroy AFS tokens based on Kerberos credentials and appdefaults.

## Main Interfaces
`pam_sm_authenticate()` returns `PAM_IGNORE`. `pam_sm_setcred()` initializes Kerberos, opens the PAM-provided or default credential cache, reads the principal, checks the Kerberos appdefault boolean `afslog`, and performs AFS token operations.

## Behavior
For establish/reinitialize/refresh credentials, it may create a PAG and call `krb5_afslog()` if enabled and AFS is available. For delete credentials, it calls `k_unlog()`. Kerberos setup, cache, or principal errors return `PAM_SERVICE_ERR`.

## Dependencies
Depends on Heimdal `krb5` and `kafs`, PAM environment `KRB5CCNAME`, and OpenPAM logging macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/pam_afslog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/Makefile

## Purpose
Build definition for the `pam_chroot` session module.

## Main Contents
Builds `pam_chroot` from `pam_chroot.c`, installs `pam_chroot.8`, and includes shared PAM module rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/pam_chroot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/pam_chroot.c

## Purpose
PAM session module that chroots a user session.

## Main Interfaces
`pam_sm_open_session()` resolves the PAM user, determines chroot directory and working directory, calls `chroot()` and `chdir()`, and updates `HOME`. `pam_sm_close_session()` returns success.

## Configuration Behavior
Root is skipped unless `also_root` is set. A home directory containing `/./` splits into chroot prefix and post-chroot cwd. Otherwise `dir` and optional `cwd` options specify chroot behavior. If `always` is set and no chroot directory is available, the module fails.

## Risks and Notes
The module changes process root and cwd, so order in PAM session stacks is significant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/pam_chroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/Makefile

## Purpose
Build definition for the `pam_deny` module.

## Main Contents
Builds `pam_deny` from `pam_deny.c`, installs `pam_deny.8`, and includes shared PAM module rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/pam_deny.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/pam_deny.c

## Purpose
PAM module that deliberately denies authentication, account, session, credential, and password operations.

## Main Interfaces
`pam_sm_authenticate()` obtains the user then returns `PAM_AUTH_ERR`. `pam_sm_setcred()` returns `PAM_CRED_ERR`. `pam_sm_acct_mgmt()` returns `PAM_AUTH_ERR`. `pam_sm_chauthtok()` returns `PAM_AUTHTOK_ERR`, except `prelim_ignore` can make preliminary checks return `PAM_IGNORE`. Session open and close return `PAM_SESSION_ERR`.

## Integration Notes
Useful as an explicit default-fail module in PAM policy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/pam_deny.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/Makefile

## Purpose
Build definition for the `pam_echo` module.

## Main Contents
Builds `pam_echo` from `pam_echo.c`, installs `pam_echo.8`, and includes shared PAM module rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/pam_echo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/pam_echo.c

## Purpose
PAM module that displays configured messages through the PAM conversation.

## Main Logic
`_pam_echo()` concatenates module arguments into a bounded message, expands selected percent escapes from PAM items, and calls `pam_info()`. Supported expansions include remote host, service, tty, remote user, and user. It obeys `PAM_SILENT`.

## PAM Hooks
Authentication, account management, open session, and close session all echo. `pam_sm_setcred()` succeeds without output. Password change echoes only outside preliminary check.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/pam_echo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/Makefile

## Purpose
Build definition for the `pam_exec` module.

## Main Contents
Builds `pam_exec` from `pam_exec.c`, installs `pam_exec.8`, and includes shared PAM module rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/pam_exec.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/pam_exec.c

## Purpose
PAM module that executes an external command for PAM service hooks.

## Main Logic
`_pam_exec()` requires a command argument, builds an environment from `pam_getenvlist()` plus selected PAM items (`PAM_SERVICE`, `PAM_USER`, `PAM_TTY`, `PAM_RHOST`, `PAM_RUSER`), then `vfork()`/`execve()`s the command. It waits for the child and maps fork, exec, signal, wait, and nonzero exit failures to PAM errors.

## PAM Hooks
Authentication, setcred, account, open session, close session, and password change all call `_pam_exec()`.

## Risks and Notes
The executed command and arguments come from PAM policy configuration. The child inherits standard descriptors; conversation redirection is noted but not implemented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/pam_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/Makefile

## Purpose
Build definition for the `pam_ftpusers` account module.

## Main Contents
Builds `pam_ftpusers` from `pam_ftpusers.c`, installs `pam_ftpusers.8`, and includes shared PAM module rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/pam_ftpusers.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/pam_ftpusers.c

## Purpose
PAM account module that checks `/etc/ftpusers` style policy for the target user.

## Main Logic
`pam_sm_acct_mgmt()` resolves the PAM user, opens `_PATH_FTPUSERS`, and scans noncomment entries. Plain entries match usernames. Entries beginning with `@` are treated as group names and checked against group members. The `disallow` OpenPAM option reverses allow/deny interpretation.

## Behavior
By default, a found entry allows access and a missing entry denies access. With `disallow`, a found entry denies and a missing entry allows.

## Dependencies and Notes
Uses passwd/group lookups, `fgetln()`, `_PATH_FTPUSERS`, OpenPAM options, and PAM logging macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/pam_ftpusers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/Makefile

## Purpose
Build definition for the `pam_group` module.

## Main Contents
Builds `pam_group` from `pam_group.c`, installs `pam_group.8`, disables lint/profile/PIC install variants, and links `libutil` and `libcrypt`.

## Integration Notes
Includes shared module rules after adding libraries required for password authentication and login class handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/pam_group.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/pam_group.c

## Purpose
PAM authentication module that gates access based on applicant membership in a configured group, optionally authenticating that applicant’s password.

## Main Logic
`pam_sm_authenticate()` gets the target account (`PAM_USER`) and applicant (`PAM_RUSER`), optionally ignores non-root targets when `root_only` is set, resolves the configured `group` option or defaults to `wheel`, and checks applicant primary gid or group membership.

## Options
`authenticate` prompts for the applicant’s password and verifies it with `crypt()`. `deny` inverts success/failure semantics. `fail_safe` treats missing or invalid group data as allowed. `root_only` applies only to root target accounts.

## Other Hook and Risks
`pam_sm_setcred()` returns success. Password verification compares `crypt(pass, pwd->pw_passwd)` against the stored hash, and failures can emit PAM conversation/log messages.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/pam_group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/Makefile

## Purpose
Build definition for the `pam_guest` module.

## Main Contents
Builds module library `pam_guest` from `pam_guest.c`, installs `pam_guest.8`, and includes shared PAM module rules via `../mod.mk`.

## Integration Notes
Only the Makefile is in this work item; the corresponding source file is outside this grouped file list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/Makefile -->