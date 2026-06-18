# Group Research: group_1409_openbsd_src_sources_os_bsd_openbsd_src_sys_sys_cdefs_h_sources_os_b_0a81da33d4d2

Scope verified against `Docs/research_subset_a.md`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/cdefs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/cdefs.h

This header provides foundational compiler, linkage, attribute, prediction, and standards-visibility macros used throughout OpenBSD headers.

Key definitions:
- Compiler/version helpers: `__GNUC_PREREQ__`, `__P`, `__CONCAT`, `__STRING`.
- Attribute wrappers: `__dead`, `__pure`, `__unused`, `__used`, `__warn_unused_result`, `__bounded`, `__returns_twice`, `__packed`, `__aligned`, `__malloc`.
- Inline/linkage helpers: `__only_inline`, `__BEGIN_EXTERN_C`, `__END_EXTERN_C`, visibility push/pop macros, and public/hidden declaration wrappers.
- Branch prediction: `__predict_true()` and `__predict_false()`.
- Feature exposure macros: `__POSIX_VISIBLE`, `__XPG_VISIBLE`, `__ISO_C_VISIBLE`, and `__BSD_VISIBLE`.

Behavior and integration:
- Includes `<machine/cdefs.h>` for machine-level additions.
- Normalizes `_XOPEN_SOURCE`, `_POSIX_C_SOURCE`, `_ANSI_SOURCE`, `_ISOC99_SOURCE`, `_ISOC11_SOURCE`, `__STDC_VERSION__`, and C++ levels into internal visibility values.
- Defaults to POSIX.1-2024, XPG 800, ISO C 2017, and BSD-visible interfaces when no restrictive feature-test macros are supplied.

Risk notes:
- This is a high-impact compatibility header; small changes can alter API exposure across the whole tree.
- Feature-test macro ordering is deliberate: X/Open settings can redefine `_POSIX_C_SOURCE`, and ISO/C++ settings can override ISO C visibility.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/cdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/cdio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/cdio.h

This header defines CD-ROM and DVD ioctl ABI structures and command constants shared between kernel and userland.

Key definitions:
- CD addressing/layout types: `union msf_lba`, `struct cd_toc_entry`, subchannel header/data structures, and `struct cd_sub_channel_info`.
- CD ioctls: play by track/block/MSF, read subchannel, read TOC header/entries, read multisession address, volume/patch control, pause/resume/reset/start/stop/eject/lock/unlock/close, and load/unload.
- DVD structures: `struct dvd_layer`, `dvd_physical`, `dvd_copyright`, `dvd_disckey`, `dvd_bca`, `dvd_manufact`, and `union dvd_struct`.
- DVD authentication ABI: authentication state constants and `union dvd_authinfo`.

Behavior and integration:
- Includes `<sys/types.h>` and `<sys/ioccom.h>`.
- Uses `_BYTE_ORDER` to define CD bitfields consistently for little- and big-endian machines.
- Ioctl numbers use command groups `'c'` for CD and `'d'` for DVD.

Risk notes:
- Several structs contain user pointers passed through ioctls, so kernel handlers must validate lengths and copy boundaries.
- `CDIOCPLAYMSF` and `CDIOCALLOW` share command number 25 under different historical layouts; compatibility handling depends on ioctl encoding including direction/size.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/cdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/chio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/chio.h

This header defines the changer/tape-library ioctl interface.

Key definitions:
- Element types: `CHET_MT`, `CHET_ST`, `CHET_IE`, `CHET_DT`.
- Operation structures: `changer_move`, `changer_exchange`, `changer_position`, `changer_params`, `changer_voltag`, `changer_element_status`, and `changer_element_status_request`.
- Status bits: `CESTATUS_FULL`, `CESTATUS_IMPEXP`, `CESTATUS_EXCEPT`, `CESTATUS_ACCESS`, `CESTATUS_EXENAB`, `CESTATUS_INENAB`, plus per-element masks.
- Ioctls: `CHIOMOVE`, `CHIOEXCHANGE`, `CHIOPOSITION`, `CHIOGPICKER`, `CHIOSPICKER`, `CHIOGPARAMS`, `CHIOGSTATUS`.

Behavior and integration:
- Element type numeric values are ABI-sensitive and used as offsets by `sys/scsi/ch.c`.
- `CHIOGSTATUS` passes a caller-allocated array pointer through `changer_element_status_request`.

Risk notes:
- Reordering element type constants would break the SCSI changer driver.
- Status-return ioctls require careful count/type validation by consumers because the request contains a raw pointer.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/chio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/clockintr.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/clockintr.h

This header defines the OpenBSD clock interrupt scheduling interface and statistics.

Key definitions:
- Public stats: `struct clockintr_stat`.
- Kernel platform API: `struct intrclock` with `ic_rearm` and `ic_trigger`.
- Schedulable callback: `struct clockintr`, with pending/all queue links and callback function.
- Rescheduling request: `struct clockrequest`.
- Per-CPU queue: `struct clockqueue`, including mutex, pending lists, hardclock handle, interrupt clock, stats, generation counters, and dispatch flags.

Kernel APIs:
- CPU/platform: `clockintr_cpu_init`, `clockintr_dispatch`, `clockintr_trigger`.
- Callback lifecycle: `clockintr_bind`, `clockintr_schedule`, `clockintr_cancel`, `clockintr_unbind`, `clockintr_stagger`.
- Request helpers: `clockintr_advance`, `clockrequest_advance`, `clockrequest_advance_random`.
- Queue/sysctl: `clockqueue_init`, `sysctl_clockintr`.

Risk notes:
- Lock annotations in comments are central to correctness: queue fields are split between immutable, mutex-protected, atomic, and CPU-owned state.
- `clockrequest` lets callbacks ask for rescheduling on return, so dispatch paths must honor ownership and `CQ_IGNORE_REQUEST`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/clockintr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/conf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/conf.h

This header defines OpenBSD block/character device switch tables, line discipline tables, and device-switch initializer macros.

Key definitions:
- Device classes/flags: `D_DISK`, `D_TTY`, `D_CLONE`.
- Block device switch: `struct bdevsw` with open/close/strategy/ioctl/dump/size/type.
- Character device switch: `struct cdevsw` with open/close/read/write/ioctl/stop/tty/mmap/type/flags/kqfilter.
- Line discipline switch: `struct linesw`.
- Driver declaration/initializer macros: `dev_type_*`, `dev_decl`, `bdev_decl`, `cdev_decl`, `bdev_disk_init`, `cdev_disk_init`, `cdev_tty_init`, and many device-class-specific initializers.

Kernel APIs:
- Device switch globals: `bdevsw[]`, `cdevsw[]`, `linesw[]`, `swdevt[]`, `chrtoblktbl[]`.
- Mapping/helpers: `bdevsw_lookup`, `chrtoblk`, `blktochr`, `iskmemdev`, `iszerodev`, `getnulldev`.
- Declares many built-in cdev/bdev entry points such as `sd`, `cd`, `vnd`, `rd`, `fuse`, `kstat`, `kcov`, and `dt`.

Risk notes:
- Initializer macros encode default unsupported operations as `enodev`, `enxio`, or `nullop`; choosing the wrong macro changes visible device behavior.
- Some macros intentionally map specialized devices through other implementations, such as `fido`/`ujoy` using `uhid` operations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/core.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/core.h

This header preserves the obsolete NetBSD-style core file format used by binutils support.

Key definitions:
- Magic values: `COREMAGIC`, `CORESEGMAGIC`.
- `CORE_GETMAGIC`, `CORE_GETMID`, `CORE_GETFLAG`, `CORE_SETMAGIC` for network-byte-order mid/magic/flag encoding.
- Core flags: `CORE_CPU`, `CORE_DATA`, `CORE_STACK`.
- Userland structs: `struct core` and `struct coreseg`.

Kernel declarations:
- `coredump_write`
- `coredump_unmap`

Behavior and integration:
- The userland structures are explicitly marked obsolete and retained for binutils `netbsd-core` format support, especially a.out m88k/luna88k boot block workflows.

Risk notes:
- The header depends on network byte-order helpers and `_MAXCOMLEN` being available from includers.
- The old format is compatibility-only; modern OpenBSD ELF core notes are defined elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/core.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ctf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ctf.h

This header defines the Compact C Type Format ABI structures and encoding macros.

Key definitions:
- File/layout structs: `ctf_header`, `ctf_lblent`, `ctf_stype`, `ctf_type`, `ctf_array`, `ctf_member`, `ctf_lmember`, `ctf_enum`.
- Format constants: `CTF_MAGIC`, `CTF_VERSION`, `CTF_F_COMPRESS`, `CTF_MAX_NAME`, `CTF_MAX_VLEN`, `CTF_MAX_SIZE`, `CTF_LSIZE_SENT`.
- Type-kind macros: `CTF_INFO_VLEN`, `CTF_INFO_ISROOT`, `CTF_INFO_KIND`, and `CTF_K_*`.
- Integer/float encoding macros and flags.
- String-table/name and large-size/member-offset helpers.

Behavior and integration:
- Describes the on-disk/in-object CTF ABI; no functions are declared.
- Large structs use `CTF_LSTRUCT_THRESH` and `ctf_lmember` high/low offset fields.

Risk notes:
- All offsets and sizes are ABI layout fields; changes require matching consumers such as debuggers, linkers, or CTF readers.
- Macro aliases like `ctt_name` and `ctlm_name` intentionally overlay embedded structs for compact layout.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ctf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/device.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/device.h

This header defines OpenBSD autoconfiguration and device core structures.

Key definitions:
- Device classes: `DV_DULL`, `DV_CPU`, `DV_DISK`, `DV_IFNET`, `DV_TAPE`, `DV_TTY`.
- Power/lifecycle actions: `DVACT_DEACTIVATE`, `QUIESCE`, `SUSPEND`, `RESUME`, `WAKEUP`, `POWERDOWN`.
- Core structs: `struct device`, `struct cfdata`, `struct cfattach`, `struct cfdriver`, `struct pdevinit`.
- Config states: `FSTATE_NOTFOUND`, `FOUND`, `STAR`, disabled variants.
- Driver modes: `CD_INDIRECT`, `CD_SKIPHIBERNATE`, `CD_COCOVM`.

Kernel APIs:
- Autoconf: `config_init`, `config_search`, `config_found_sm`, `config_rootfound`, `config_scan`, `config_attach`, `config_detach`, suspend/resume/deactivate helpers, deferred mountroot helpers.
- Sleep/resume: `request_sleep`, `sleep_state`, `gosleep`, `suspend_finish`, `resuming`.
- Device lookup/ref/root: `device_mainbus`, `device_lookup`, `device_ref`, `device_unref`, `findblkmajor`, `getdisk`, `parsedisk`, `setroot`.
- Firmware: `loadfirmware`, with `FIRMWARE_MAX`.

Risk notes:
- `struct device` and config structs are central kernel ABI-internal contracts for every driver.
- `CD_COCOVM` allows devices in confidential-computing VMs, so mode flags have security/platform policy meaning.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dir.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/dir.h

This compatibility header maps old BSD `struct direct` usage to modern `struct dirent`.

Key definitions:
- Includes `<dirent.h>`.
- Defines `direct` as `dirent`.
- Defines legacy `DIRSIZ(dp)` record-size calculation using `d_namlen`.

Behavior and integration:
- Explicitly rejects kernel use with `#error "Please use <sys/dirent.h> instead"`.
- Exists only for old user-level compatibility.

Risk notes:
- `DIRSIZ` uses legacy 4-byte rounding, while kernel `DIRENT_RECSIZE` in `dirent.h` uses 8-byte alignment.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dirent.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/dirent.h

This header defines the directory entry ABI returned by `getdents(2)`.

Key definitions:
- `struct dirent` with file number, post-entry offset, record length, file type, name length, padding, and NUL-terminated name.
- `MAXNAMLEN` under `__BSD_VISIBLE`.
- File type constants: `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`.
- Conversion macros: `IFTODT`, `DTTOIF`.
- Kernel record-size macros: `DIRENT_RECSIZE(namelen)` and `DIRENT_SIZE(dp)`.

Behavior and integration:
- Includes `<sys/cdefs.h>` for feature visibility.
- Directory entries are padded for alignment and names are guaranteed NUL-terminated.

Risk notes:
- The structure is syscall ABI; field size or alignment changes would break userland.
- `DIRENT_RECSIZE` includes the terminating NUL and rounds to 8-byte alignment.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/disk.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/disk.h

This header defines kernel disk objects, disk statistics, and disk-list interfaces.

Key definitions:
- `DS_DISKNAMELEN`
- `struct diskstats`
- `struct disk` with global-list linkage, locks, device identity, flags, statistics, open masks, label state, block/byte shifts, and dynamically allocated `disklabel`.
- Disk flags: `DKF_CONSTRUCTED`, `DKF_OPENED`, `DKF_NOLABELREAD`.
- Disk label states: `DK_CLOSED`, `DK_WANTOPEN`, `DK_WANTOPENRAW`, `DK_RDLABEL`, `DK_OPEN`, `DK_OPENRAW`.
- Disk map flags: `DM_OPENPART`, `DM_OPENBLCK`.
- Public `TAILQ_HEAD(disklist_head, disk)`.

Kernel APIs:
- Lifecycle/statistics: `disk_init`, `disk_construct`, `disk_attach`, `disk_detach`, `disk_busy`, `disk_unbusy`, `disk_gone`.
- Partition/open handling: `disk_openpart`, `disk_closepart`.
- Lock/lookup: `disk_lock`, `disk_lock_nointr`, `disk_unlock`, `disk_lookup`.
- Labels/map/DUID: `disk_readlabel`, `disk_map`, `duid_iszero`, `duid_format`.

Risk notes:
- Open masks are 64-bit to match `MAXPARTITIONSUNIT`.
- `dk_label` is dynamically allocated to avoid machine-dependent `struct disk` sizing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/disklabel.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/disklabel.h

This header defines OpenBSD disklabel, partition, GPT, and DOS MBR layout constants and helpers.

Key definitions:
- Paths and constants: `_PATH_DISKTAB`, `DISKTAB`, `MAXPARTITIONSUNIT`, `MAXPARTITIONS16`, `RAW_PART`, `DISKMAGIC`, `MAXDISKSIZE`.
- Device translation macros: `DISKUNIT`, `DISKPART`, `DISKMINOR`, `MAKEDISKDEV`, `DISKLABELDEV`.
- `struct disklabel` with geometry, UID, 48-bit size/start/end high parts, checksum, partition count, and `d_partitions[MAXPARTITIONSUNIT]`.
- Partition helpers: `DL_GETPSIZE`, `DL_SETPSIZE`, `DL_GETPOFFSET`, `DL_SETPOFFSET`, `DL_GETDSIZE`, `DL_SETDSIZE`, `DL_GETBSTART`, `DL_SETBSTART`, `DL_GETBEND`, `DL_SETBEND`.
- Block/sector conversion helpers and partition name/number inline functions.
- Disk and filesystem type constants, plus optional name tables under `DKTYPENAMES`.
- GPT structures/constants and OpenBSD/EFI GUID constants.
- DOS MBR structures/constants and known DOS partition types.

Kernel APIs:
- Disklabel operations: `diskerr`, `dkcksum`, `initdisklabel`, `checkdisklabel`, `setdisklabel`, `readdisklabel`, `writedisklabel`, `bounds_check_with_label`, `readdisksector`, `readdoslabel`.
- Optional spoofers for `CD9660` and `UDF`.
- Userland: `getdiskbyname`.

Risk notes:
- 48-bit disk-size fields are split high/low; direct field access can truncate sizes.
- GPT fields are specified little-endian by UEFI even on big-endian systems.
- `DOS_LABELSECTOR` and machine-dependent `<machine/disklabel.h>` make label placement platform-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/disklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dkio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/dkio.h

This header defines disk-specific ioctl commands.

Key definitions:
- Disklabel ioctls: `DIOCGDINFO`, `DIOCSDINFO`, `DIOCWDINFO`, `DIOCGPART`, `DIOCGPDINFO`, `DIOCRLDINFO`.
- Removable/cache ioctls: `DIOCEJECT`, `DIOCLOCK`, `DIOCINQ`, `DIOCGCACHE`, `DIOCSCACHE`, `DIOCCACHESYNC`.
- Disk mapping ioctl: `DIOCMAP`.
- Compatibility transition sizing: `O_disklabel`, `O_DIOCGDINFO`.
- Structures: `dk_inquiry`, `dk_cache`, `dk_diskmap`.

Behavior and integration:
- Includes `<sys/ioccom.h>`.
- References `struct disklabel` and `struct partinfo` from disklabel definitions.

Risk notes:
- `dk_diskmap` includes a user pointer and fd; ioctl handlers must validate both.
- `O_DIOCGDINFO` exists for transition from 16 to more partitions and is ABI-compatibility sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/dkio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/domain.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/domain.h

This header defines the protocol domain descriptor for kernel networking.

Key definitions:
- `socklen_t` typedef guard.
- Forward declaration for `struct mbuf`.
- `struct domain` with address family, name, init hook, rights externalize/dispose hooks, protocol switch range, sockaddr size, route key offset, and maximum prefix length.

Kernel APIs:
- `domaininit`
- Domain globals: `domains[]`, `inet6domain`, `inetdomain`, `mplsdomain`, `pfkeydomain`, `routedomain`, `unixdomain`.

Risk notes:
- `dom_externalize` and `dom_dispose` handle file-descriptor/access-right transfer over mbufs, so domain implementations must preserve ownership rules.
- Routing fields are used by generic route-table code and must match each domain’s sockaddr layout.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/domain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/endian.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/endian.h

This header exposes public endian and byte-swap conversion macros.

Key definitions:
- Public aliases: `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, `BYTE_ORDER`.
- Host/endian conversion macros: `htobe16/32/64`, `htole16/32/64`, `be16/32/64toh`, `le16/32/64toh`.
- BSD-visible helpers: `swap16/32/64`, `swap16_multi`, `betoh*`, `letoh*`, `htons`, `htonl`, `ntohs`, `ntohl`, `NTOH*`, `HTON*`.
- Kernel memory conversion aliases: `bemtoh*`, `htobem*`, `lemtoh*`, `htolem*`.

Behavior and integration:
- Includes `<sys/cdefs.h>` and `<sys/_endian.h>`.
- Public userspace should include `<endian.h>`; kernel code should include `<sys/endian.h>`.

Risk notes:
- `be*toh` and `betoh*` intentionally map to the same low-level `__htobe*` transformations because swaps are symmetric.
- BSD-visible socket byte-order macros are only defined if not already provided.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/errno.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/errno.h

This header defines OpenBSD errno constants and kernel pseudo-errors.

Key definitions:
- Standard errno values from `EPERM` through `EPROTO`, with `ELAST` equal to 95 under `__BSD_VISIBLE`.
- Aliases: `EWOULDBLOCK` equals `EAGAIN`.
- BSD-visible errors include `ENOTBLK`, `ESOCKTNOSUPPORT`, `EPFNOSUPPORT`, `ESHUTDOWN`, `ETOOMANYREFS`, `EHOSTDOWN`, RPC/auth/IPsec/media-specific errors.
- Kernel pseudo-errors: `ERESTART` and `EJUSTRETURN`.

Behavior and integration:
- Includes `<sys/cdefs.h>` for feature visibility.
- Values are ABI-stable and used by libc, kernel syscall return handling, and applications.

Risk notes:
- `ELAST` must track the largest errno.
- Kernel pseudo-errors are internal negative values and must not escape as user-visible `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/evcount.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/evcount.h

This kernel-only header defines lightweight event counters.

Key definitions:
- `struct evcount` with main counter, id, name, user data, optional per-CPU counter storage, and global queue linkage.

Kernel APIs:
- `evcount_attach`
- `evcount_detach`
- `evcount_inc`
- `evcount_init_percpu`
- `evcount_percpu`
- `evcount_sysctl`

Behavior and integration:
- Only active under `_KERNEL`.
- Uses `<sys/queue.h>` and forward-declares `struct cpumem`.

Risk notes:
- Counters can be per-CPU or global; sysctl aggregation must understand `ec_percpu`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/evcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/event.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/event.h

This header defines the kqueue/kevent userspace ABI and kernel knote/filter interface.

Key definitions:
- Filters: `EVFILT_READ`, `WRITE`, `AIO`, `VNODE`, `PROC`, `SIGNAL`, `TIMER`, `DEVICE`, `EXCEPT`, `USER`.
- `struct kevent` and `EV_SET`.
- Event action/flag constants: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Filter notes for read/write/except, vnode, proc, device, timer, and user events.
- Public `struct klist` and `SLIST_HEAD(knlist, knote)` compatibility exposure.

Kernel definitions:
- Internal flags such as `__EV_SELECT`, `__EV_POLL`, `__EV_HUP`, `NOTE_SUBMIT`, `NOTE_SIGNAL`.
- `struct filterops`, `struct knote`, `struct klistops`, `struct kqueue_scan_state`.
- APIs for knote/kqueue registration, scan, poll, list operations, and inline helpers `knote_modify`, `knote_process`, `klist_empty`.

Userland declarations:
- `kqueue`
- `kqueue1`
- `kevent`

Risk notes:
- `struct kevent` is syscall ABI and must remain stable.
- Kernel filterops concurrency rules are documented in the header; filter implementations depend on serialized attach/detach/modify/process callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/eventvar.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/eventvar.h

This kernel header defines the internal `struct kqueue`.

Key definitions:
- Constants: `KQ_NEVENTS`, `KQEXTENT`.
- `struct kqueue` with queue mutex, pending event list/count, refcount, knotes for kqueue-on-kqueue, owning filedesc, registered knote arrays/hash, deferred task, and state flags.
- State flags: `KQ_SLEEP`, `KQ_DYING`, `KQ_TASK`.

Behavior and integration:
- Includes mutex, refcount, and task headers.
- Complements public and kernel-facing declarations in `event.h`.

Risk notes:
- Lock annotations distinguish immutable, global klist-lock, atomic, and kqueue-lock fields.
- `kq_fdp` ties kqueues to descriptor tables, so fd-table teardown must coordinate with kqueue lifecycle.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/eventvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/exec.h

This header defines generic exec package state, vmspace construction commands, and legacy machine IDs.

Key definitions:
- User stack process string block: `struct ps_strings`.
- Exec switch: `struct execsw`.
- VM build command: `struct exec_vmcmd`, flags `VMCMD_RELATIVE`, `BASE`, `STACK`, `IMMUTABLE`, `TEXTREL`.
- Command set: `struct exec_vmcmd_set`, `EXEC_DEFAULT_VMCMD_SETSIZE`, `VMCMDSET_INIT`.
- Main exec state: `struct exec_package`, including header, namei/vnode/attrs, vmcmds, text/data/stack layout, flags, interpreter, ELF args, syscall pins, and executable pin region.
- Exec flags: `EXEC_INDIR`, `EXEC_HASFD`, `EXEC_HASARGL`, `EXEC_SKIPARG`, `EXEC_DESTR`, `EXEC_WXNEEDED`, `EXEC_NOBTCFI`, `EXEC_PROFILE`.
- Legacy `MID_*` machine IDs.

Kernel APIs:
- VM command helpers: `vmcmdset_extend`, `kill_vmcmds`, `vmcmd_map_pagedvn`, `vmcmd_map_readvn`, `vmcmd_map_zero`, `vmcmd_mutable`, `vmcmd_randomize`, `new_vmcmd`.
- Exec helpers: `copyargs`, `setregs`, `check_exec`, `exec_setup_stack`, `exec_process_vmcmds`.
- Globals: `execsw[]`, `nexecs`, `exec_maxhdrsz`, `stackgap_random`.

Risk notes:
- `exec_package` coordinates file references, fake script args, interpreter loading, W^X, branch-target CFI, and pinsyscall metadata.
- VM command flags control memory attributes and ASLR-sensitive mapping behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec_elf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/exec_elf.h

This header defines OpenBSD’s ELF ABI structures, constants, relocation helpers, dynamic tags, core notes, and kernel ELF exec hooks.

Key definitions:
- ELF integer typedefs for 32-bit and 64-bit classes.
- Identification constants: `EI_*`, `ELFMAG*`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`, `IS_ELF`.
- ELF headers: `Elf32_Ehdr`, `Elf64_Ehdr`.
- Section headers, special section indexes, section types, section names, and section flags.
- Symbol table entries and symbol binding/type/visibility helpers.
- Relocation entries: `Elf32_Rel/Rela`, `Elf64_Rel/Rela`, `Elf32_Relr`, `Elf64_Relr`, and `ELF*_R_*` macros, including little-endian MIPS64 overrides.
- Program headers and segment constants including OpenBSD-specific `PT_OPENBSD_MUTABLE`, `RANDOMIZE`, `WXNEEDED`, `NOBTCFI`, `SYSCALLS`, and `BOOTDATA`.
- Dynamic section structures and `DT_*`, `DF_*`, `DF_1_*`.
- ELF note structures and OpenBSD core-note identifiers.
- `struct elfcore_procinfo`.
- Aux vector structures, `enum AuxID`, and `struct elf_args` under `_KERNEL` or `_DYN_LOADER`.
- ELFSIZE alias machinery mapping `Elf_*` names to 32- or 64-bit types.

Kernel APIs:
- `exec_elf_makecmds`
- `exec_elf_fixup`
- `coredump_elf`
- `coredump_note_elf_md`
- `coredump_writenote_elf`

Risk notes:
- This is a large ABI header used by kernel, dynamic loader, tools, and userland.
- OpenBSD program headers encode security policy: W^X exceptions, no branch-target CFI, syscall pin tables, randomization, and mutable segments.
- `ELF_AUX_ENTRIES` must match the actual aux vector construction path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec_script.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/exec_script.h

This header defines script-exec recognition constants and the kernel script exec hook.

Key definitions:
- `EXEC_SCRIPT_MAGIC` as `#!`
- `EXEC_SCRIPT_MAGICLEN`
- `EXEC_SCRIPT_HDRSZ`, based on magic, separator, `MAXINTERP`, and terminator.

Kernel API:
- `exec_script_makecmds`

Risk notes:
- Header-size calculation depends on `MAXINTERP` from included exec context.
- Script handling interacts with `EXEC_INDIR`, fake argv, and held script file descriptors in `exec_package`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/exec_script.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/extent.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/extent.h

This header defines the extent allocator interface used for address/resource range management.

Key definitions:
- `struct extent_region` with start/end/flags and list linkage.
- Region flags: `ER_ALLOC`, `ER_DISCARD`.
- `struct extent` with name, allocated regions, range, memory type, flags, and global linkage.
- `struct extent_fixed` for preallocated descriptor storage.
- Internal extent flags: `EXF_FIXED`, `EXF_NOCOALESCE`, `EXF_WANTED`, `EXF_FLWANTED`.
- Allocation flags: `EX_NOWAIT`, `EX_WAITOK`, `EX_FAST`, `EX_CATCH`, `EX_NOCOALESCE`, `EX_MALLOCOK`, `EX_WAITSPACE`, `EX_BOUNDZERO`, `EX_CONFLICTOK`, `EX_FILLED`.
- Placeholders: `EX_NOALIGN`, `EX_NOBOUNDARY`.

Kernel/testing APIs:
- `EXTENT_FIXED_STORAGE_SIZE`
- `extent_create`, `extent_destroy`
- `extent_alloc_subregion`, `extent_alloc_subregion_with_descr`
- `extent_alloc_region`, `extent_alloc_region_with_descr`
- `extent_free`, `extent_print`, `extent_print_all`
- Convenience macros `extent_alloc` and `extent_alloc_with_descr`.

Risk notes:
- Extents can sleep, allocate memory, or use fixed storage depending on flags; callers must choose flags appropriate to context.
- Boundary/alignment semantics are encoded in allocation API parameters, not the extent object alone.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/fcntl.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/fcntl.h

This header defines open/fcntl flags, file descriptor flags, file locking ABI, and related libc prototypes.

Key definitions:
- Open modes/status flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_ACCMODE`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_DSYNC`, `O_RSYNC`, `O_NOFOLLOW`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_CLOEXEC`, `O_DIRECTORY`, `O_CLOFORK`.
- BSD-visible kernel/compat aliases: `FREAD`, `FWRITE`, `FAPPEND`, `FASYNC`, `FFSYNC`, `FNONBLOCK`, `FNDELAY`, `O_NDELAY`.
- Kernel conversions: `FFLAGS`, `OFLAGS`, `FMASK`, `FCNTLFLAGS`.
- `fcntl` commands including POSIX.1-2024 `F_DUPFD_CLOFORK`.
- Descriptor flags: `FD_CLOEXEC`, `FD_CLOFORK`.
- Locking: `struct flock`, `F_RDLCK`, `F_UNLCK`, `F_WRLCK`, kernel lock flags, BSD `LOCK_*`.
- `*at` constants: `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_NOFOLLOW`, `AT_SYMLINK_FOLLOW`, `AT_REMOVEDIR`.

Userland declarations:
- `open`, `creat`, `fcntl`, `flock`, `openat`.

Risk notes:
- `FFLAGS`/`OFLAGS` rely on OpenBSD’s read/write bit encoding being one greater than open access mode.
- POSIX visibility controls whether newer close-on-fork interfaces are exposed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/file.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/file.h

This header defines kernel file object types, file operations, and file reference helpers.

Key definitions:
- Descriptor object types: `DTYPE_VNODE`, `SOCKET`, `PIPE`, `KQUEUE`, `DMABUF`, `SYNC`.
- `struct fileops` with read/write/ioctl/kqfilter/stat/close/seek callbacks.
- `FO_POSITION`.
- `struct file` with global linkage, mutex, flags, internal flags, type, refcount, credentials, ops, offset, private data, and IO metrics.
- Internal flags: `FIF_HASLOCK`, `FIF_INSERTED`.
- Reference helpers: `FREF`, `FRELE`, `FDUP_MAX_COUNT`.

Kernel APIs/globals:
- `fdrop`
- `foffset`
- `LIST_HEAD(filelist, file)`
- `maxfiles`, `numfiles`, `socketops`, `vnops`

Risk notes:
- Some `fileops` may run without the kernel lock; implementers must honor per-file locking.
- `FREF` calls `vfs_stall_barrier()` before incrementing the refcount, coupling file reference acquisition with VFS stall coordination.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/filedesc.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/filedesc.h

This header defines per-process/shared file descriptor table structures and descriptor-management APIs.

Key definitions:
- Sizing constants: `NDFILE`, `NDEXTENT`, `NDENTRIES`, `NDENTRYMASK`, `NDENTRYSHIFT`, `NDREDUCE`, `NDHISLOTS`, `NDLOSLOTS`.
- `struct filedesc` with open file pointer array, per-fd flags, cwd/root vnodes, allocation/open counters, free-fd bitmaps, umask, refcount, rwlock, file-pointer mutex, attached kqueues, flags, and kqueue user-event count.
- `struct filedesc0` embeds initial storage for the first descriptors and bitmap arrays.
- Per-fd flags: `UF_EXCLOSE`, `UF_PLEDGED`, `UF_FORKCLOSE`, `UF_PLEDGEOPEN`.
- Descriptor-table flag: `FD_ADVLOCK`.
- `OFILESIZE`.

Kernel APIs:
- Lifecycle/copy/share/free: `filedesc_init`, `fdinit`, `fdshare`, `fdcopy`, `fdfree`.
- Allocation/insert/remove/release: `fdalloc`, `fdexpand`, `falloc`, `fnew`, `fdinsert`, `fdremove`, `fdrelease`, `dupfdopen`.
- Exec/fork helpers: `fdprepforexec`.
- Lookup/iteration: `fd_iterfile`, `fd_getfile`, `fd_getfile_mode`, `fd_checkclosed`.
- Close/socket helpers: `closef`, `getsock`.
- Lock macros: `fdplock`, `fdpunlock`, `fdpassertlocked`.

Risk notes:
- Descriptor flags include both close-on-exec and close-on-fork behavior.
- `fd_ofiles` access is protected by two different locks depending on operation mode; misuse can race descriptor table expansion or closure.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/filedesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/filio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/filio.h

This header defines generic file-descriptor ioctl commands.

Key definitions:
- `FIOCLEX` and `FIONCLEX` for close-on-exec.
- `FIONREAD` for readable byte count.
- `FIONBIO` for nonblocking mode.
- `FIOASYNC` for async IO.
- `FIOSETOWN` and `FIOGETOWN` for signal owner.

Behavior and integration:
- Includes `<sys/ioccom.h>`.
- Included by `<sys/ioctl.h>` alongside tty and socket ioctl sets.

Risk notes:
- These ioctls are generic and may be implemented by multiple file types, so behavior depends on fileops/device support.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/fusebuf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/fusebuf.h

This header defines OpenBSD kernel-to-userland FUSE request/response buffer structures.

Key definitions:
- `FUSEBUFMAXSIZE`.
- `struct fb_hdr` with queue linkage, data length, errno, operation type, inode, UUID, caller tid/uid/gid, and umask.
- `struct fb_io` for file operations with fd, inode, offset, length, mode, flags, and rdev.
- `struct fusebuf` with header, operation union (`statvfs`, `stat`, `fb_io`), and data pointer.
- Convenience field macros for header and union fields.
- `fbtod(fb,t)` data conversion macro.
- Setattr flags: `FUSE_FATTR_*`.
- Operation types: `FBT_LOOKUP`, `GETATTR`, `SETATTR`, `READLINK`, `SYMLINK`, `MKNOD`, `MKDIR`, `UNLINK`, `RMDIR`, `RENAME`, `LINK`, `OPEN`, `READ`, `WRITE`, `STATFS`, `RELEASE`, `FSYNC`, `FLUSH`, `INIT`, `OPENDIR`, `READDIR`, `RELEASEDIR`, `FSYNCDIR`, `ACCESS`, `DESTROY`, `RECLAIM`.

Kernel APIs:
- `fb_setup`
- `fb_queue`
- `fb_delete`

Risk notes:
- Requests are correlated by `fh_uuid`; userland replies must preserve it.
- Large read/write/readdir operations can be split across multiple fusebufs with changing offsets.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/fusebuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/futex.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/futex.h

This header defines the OpenBSD futex syscall ABI.

Key definitions:
- Userland prototype: `futex(volatile uint32_t *, int, int, const struct timespec *, volatile uint32_t *)`.
- Operation masks/constants: `FUTEX_OP_MASK`, `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_REQUEUE`.
- Flag mask and private flag: `FUTEX_FLAG_MASK`, `FUTEX_PRIVATE_FLAG`.
- Convenience private operations: `FUTEX_WAIT_PRIVATE`, `FUTEX_WAKE_PRIVATE`, `FUTEX_REQUEUE_PRIVATE`.

Risk notes:
- The syscall accepts volatile user addresses; kernel implementation must validate and safely fault/copy user memory.
- Private futex operations alter sharing/lookup semantics and must not be confused with process-shared futexes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/futex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/gmon.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/gmon.h

This header defines gprof/gmon profiling data structures and userspace profiling hooks.

Key definitions:
- `struct gmonhdr` file header and `GMONVERSION`.
- Histogram settings: `HISTCOUNTER`, `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- Arc structures: `struct tostruct`, `struct rawarc`.
- Rounding macros: `ROUNDDOWN`, `ROUNDUP`.
- `struct gmonparam` profiling state with sample buffer, froms, tos, pc bounds, output buffer, raw arcs, dirfd, and list linkage.
- Profiling states: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`.
- Sysctl selectors: `GPROF_STATE`, `COUNT`, `FROMS`, `TOS`, `GMONPARAM`.

Kernel/userland APIs:
- Kernel global: `gmoninit`.
- Userland globals/functions: `_gmonparam`, `_mcleanup`, `_monstartup`, `moncontrol`, `_gmon_alloc`.

Risk notes:
- Profiling buffer sizing depends on text address ranges and architecture profile definitions.
- `MAXARCS` is bounded by the histogram counter width.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/gmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/gpio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/gpio.h

This header defines the GPIO ioctl ABI.

Key definitions:
- Pin values: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- Name length: `GPIOPINMAXNAME`.
- Pin capability/config flags: input/output/inout, open-drain, push-pull, tristate, pullup/pulldown, input/output inversion, user access, securelevel set marker.
- Structures: `gpio_info`, `gpio_pin_op`, `gpio_pin_set`, `gpio_attach`.
- Ioctls: `GPIOINFO`, `GPIOPINREAD`, `GPIOPINWRITE`, `GPIOPINTOGGLE`, `GPIOPINSET`, `GPIOPINUNSET`, `GPIOATTACH`, `GPIODETACH`.

Risk notes:
- GPIO configuration affects hardware pins and can expose user access through `GPIO_PIN_USER`.
- Attach/detach passes device names and masks through ioctl ABI, so driver name length and pin offsets are fixed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/gpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/hibernate.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/hibernate.h

This header defines hibernation image metadata, allocator state, compression state, and suspend/resume functions.

Key definitions:
- Limits/flags: `HIB_PHYSSEG_MAX`, `HIBERNATE_CHUNK_USED`, `CONFLICT`, `PLACED`, `HIBERNATE_MAGIC`, `HIB_MOVE`, `HIB_SKIP`.
- Allocator: `struct hiballoc_arena`.
- Compression: `struct hibernate_zlib_state`.
- Memory/disk image pieces: `hibernate_memory_range`, `hibernate_disk_chunk`.
- IO operation constants and callback type: `HIB_INIT`, `HIB_DONE`, `HIB_R`, `HIB_W`, `hibio_fn`.
- `union hibernate_info`, padded to 4096 bytes, with magic, device, physical memory ranges, image/chunk offsets, piglet addresses, IO function/page, kernel hash, stack guard fields, return guard offset, and sector size.

APIs:
- Hibernate allocator: `hib_alloc`, `hib_free`, `hiballoc_init`.
- Physical memory helpers: `uvm_pmr_dirty_everything`, `uvm_pmr_alloc_pig`, `uvm_pmr_alloc_piglet`, `uvm_page_rle`, `uvmpd_hibernate`.
- IO/info: `get_hibernate_io_function`, `get_hibernate_info`, `hibernate_block_io`, `hibernate_write`.
- Compression/image: `hibernate_zlib_reset`, allocation hooks, inflate/deflate/process/read/unpack functions.
- Signature/chunk operations, suspend/resume, memory preallocation, entropy, bufcache suspend/resume.

Risk notes:
- `union hibernate_info` is constrained to a disk sector-sized signature block.
- Resume correctness depends on physical address ranges, chunk placement, compression state, and kernel hash/guard metadata matching the saved image.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/hibernate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/hotplug.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/hotplug.h

This header defines the public hotplug event structure and kernel notification hooks.

Key definitions:
- Event types: `HOTPLUG_DEVAT`, `HOTPLUG_DEVDT`.
- `struct hotplug_event` with event type, device class, and 16-byte device name.

Kernel APIs:
- `hotplug_device_attach`
- `hotplug_device_detach`

Risk notes:
- Device names are fixed-width and align with `struct device::dv_xname`.
- Depends on `enum devclass` from `device.h` being available to includers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/hotplug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/intrmap.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/intrmap.h

This header declares the interrupt-to-CPU mapping abstraction.

Key definitions:
- Opaque `struct intrmap`.
- Flag: `INTRMAP_POWEROF2`.

APIs:
- `intrmap_create`
- `intrmap_destroy`
- `intrmap_count`
- `intrmap_cpu`

Behavior and integration:
- Maps device interrupts over a CPU set/count.
- Takes `const struct device *` at creation and returns `struct cpu_info *` for an interrupt index.

Risk notes:
- `INTRMAP_POWEROF2` likely constrains mapping count/selection to power-of-two behavior; callers must pass flags consistent with device interrupt layout.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/intrmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ioccom.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ioccom.h

This header defines ioctl command encoding macros.

Key definitions:
- Length/group extraction: `IOCPARM_MASK`, `IOCPARM_LEN`, `IOCBASECMD`, `IOCGROUP`.
- Maximum argument size: `IOCPARM_MAX` as `PAGE_SIZE`.
- Direction bits: `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`, `IOC_DIRMASK`.
- Encoding macros: `_IOC`, `_IO`, `_IOR`, `_IOW`, `_IOWR`.

Behavior and integration:
- Encodes direction, argument length, group, and number into an unsigned long command value.
- Used by nearly every ioctl ABI header.

Risk notes:
- Argument length is limited to 13 bits, but OpenBSD additionally caps ioctl args at `PAGE_SIZE`.
- `_IOWR` is named that way because `_IORW` conflicted historically with stdio.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ioccom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ioctl.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ioctl.h

This umbrella header exposes tty, file, and socket ioctl definitions plus the userland `ioctl` prototype.

Key includes:
- `<sys/ttycom.h>`
- `<sys/filio.h>`
- `<sys/sockio.h>`

Userland declaration:
- `int ioctl(int, unsigned long, ...);`

Risk notes:
- This file does not define ioctl encoding itself; command construction comes from `ioccom.h` through included headers.
- Inclusion order exposes broad ioctl namespaces to userland.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ipc.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ipc.h

This header defines System V IPC permission structures and common constants.

Key definitions:
- `struct ipc_perm` with creator/current uid/gid, mode, sequence, and key.
- Permission bits: `IPC_R`, `IPC_W`, `IPC_M`.
- Creation/control flags: `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, `IPC_PRIVATE`.
- Control commands: `IPC_RMID`, `IPC_SET`, `IPC_STAT`.

Kernel APIs/macros:
- ID encoding helpers: `IPCID_TO_IX`, `IPCID_TO_SEQ`, `IXSEQ_TO_IPCID`.
- `ipcperm`

Userland declaration:
- `ftok`

Risk notes:
- IPC identifiers combine index and sequence into a single id; sequence rollover behavior matters for stale-id detection.
- `ipcperm` is the shared permission gate for msg/sem/shm style objects.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kcore.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/kcore.h

This header defines the kernel crash-dump core file format.

Key definitions:
- Magic values: `KCORE_MAGIC`, `KCORESEG_MAGIC`.
- Physical RAM segment descriptor: `phys_ram_seg_t`.
- Crash dump header: `kcore_hdr_t`.
- Segment header: `kcore_seg_t`.

Behavior and integration:
- The format borrows structure from old regular core files in `<sys/core.h>`.
- Uses `u_quad_t` for physical address/size portability across architectures.

Risk notes:
- The header is format ABI for crash dump readers; field widths are chosen for cross-architecture dumps.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kcore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kcov.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/kcov.h

This header defines the kernel coverage device ioctl ABI and kernel hooks.

Key definitions:
- Ioctls: `KIOSETBUFSIZE`, `KIOENABLE`, `KIODISABLE`, `KIOREMOTEATTACH`.
- Coverage modes: `KCOV_MODE_NONE`, `KCOV_MODE_TRACE_PC`, `KCOV_MODE_TRACE_CMP`.
- Remote subsystem id: `KCOV_REMOTE_COMMON`.
- `struct kio_remote_attach`.

Kernel APIs/globals:
- `kcov_cold`
- `kcov_exit`
- `kcov_vnode`
- `kcov_remote_register`
- `kcov_remote_unregister`
- `kcov_remote_enter`
- `kcov_remote_leave`

Risk notes:
- Coverage buffers are user-controlled through ioctl, so buffer sizing and mmap/device access must be carefully bounded in implementation.
- Remote coverage requires subsystem/id registration discipline to avoid attributing events to the wrong context.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kcov.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kernel.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/kernel.h

This header declares core kernel global variables.

Key definitions/declarations:
- Host identity globals: `hostid`, `hostname`, `hostnamelen`, `domainname`, `domainnamelen`.
- Time globals: `utc_offset`, `tick`, `tick_nsec`, `ticks`, `hz`, `stathz`, `profhz`.
- Default `HZ` value of 100 if not otherwise defined.

Behavior and integration:
- Intended for kernel global state consumers.
- Relies on `MAXHOSTNAMELEN` being available from prior includes.

Risk notes:
- These globals are widely shared kernel state; changes affect timekeeping, profiling, and host identity reporting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kstat.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/kstat.h

This header defines the OpenBSD kstat ioctl ABI, named value format, and kernel registration interface.

Key definitions:
- String lengths and kstat types: `KSTAT_STRLEN`, `KSTAT_T_RAW`, `KSTAT_T_KV`, `KSTAT_T_COUNTERS`.
- `struct kstat_req` for ioctl discovery/read metadata and data pointer/length.
- Ioctls: version and find/next-find by id/provider/name.
- Named value constants: `KSTAT_KV_NAMELEN`, `KSTAT_KV_ALIGN`.
- `enum kstat_kv_type` for null, bool, counters, integers, inline/trailing strings/bytes, temperature, frequency, voltage, current, and power.
- `enum kstat_kv_unit`.
- `struct kstat_kv` and access macros.

Kernel definitions:
- `struct kstat` with id, provider/name/unit identity, type/flags/state, timestamps, RB-tree entries, data version, callbacks, lock ops, data pointer/length/update interval.
- APIs: `kstat_create`, lock setters, `kstat_read_nop`, `kstat_install`, `kstat_remove`, `kstat_destroy`, `kstat_kv_init`, `kstat_kv_unit_init`.
- Initializer macros: `KSTAT_KV_INITIALIZER`, `KSTAT_KV_UNIT_INITIALIZER`.

Risk notes:
- `struct kstat_req` contains a user data pointer and datalen; ioctl handlers must validate copy sizes and versioning.
- `KSTAT_F_REALLOC` and data version fields imply readers must handle data replacement/races.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kthread.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/kthread.h

This kernel-only header declares kernel thread creation and exit helpers.

Kernel APIs:
- `kthread_create`
- `kthread_create_deferred`
- `kthread_run_deferred_queue`
- `kthread_exit`

Behavior and integration:
- `kthread_create` accepts a function, argument, optional created proc pointer, and thread name.
- `kthread_exit` is marked `__noreturn__`.

Risk notes:
- Deferred creation queues allow threads to be created after initial conditions are ready; callers must not assume immediate execution.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ktrace.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ktrace.h

This header defines ktrace record formats, trace flags, userland syscall prototypes, and kernel trace emitters.

Key definitions:
- Operations: `KTROP_SET`, `KTROP_CLEAR`, `KTROP_CLEARFILE`, `KTROP(o)`.
- Flag: `KTRFLAG_DESCEND`.
- Common record header: `struct ktr_header`.
- Record types: `KTR_START`, `KTR_SYSCALL`, `KTR_SYSRET`, `KTR_NAMEI`, `KTR_GENIO`, `KTR_PSIG`, `KTR_STRUCT`, `KTR_USER`, `KTR_EXECARGS`, `KTR_EXECENV`, `KTR_PLEDGE`, `KTR_PINSYSCALL`.
- Per-record structs: `ktr_syscall`, `ktr_sysret`, `ktr_genio`, `ktr_psig`, `ktr_user`, `ktr_pledge`, `ktr_pinsyscall`.
- Trace facility bits: `KTRFAC_*`, `KTRFAC_MASK`, `KTRFAC_ROOT`, `KTRFAC_INHERIT`.

Userland declarations:
- `ktrace`
- `utrace`

Kernel APIs/macros:
- `KTRPOINT`
- Emitters: `ktrgenio`, `ktrnamei`, `ktrpsig`, `ktrsyscall`, `ktrsysret`, `ktruser`, `ktrexec`, `ktrpledge`, `ktrpinsyscall`, `ktrstruct`.
- Trace state: `ktrcleartrace`, `ktrsettrace`.
- Convenience `ktrstruct` wrappers for timespec/timeval/cmsghdr/fds/fdset/flock/iovec/itimerval/kevent/msghdr/pollfd/quota/rlimit/rusage/sigaction/siginfo/sockaddr/stat.

Risk notes:
- Trace records may include syscall arguments, IO data, exec args/env, pledge failures, and pinsyscall addresses, so output can contain sensitive process data.
- `KTRPOINT` avoids recursive tracing when `P_INKTR` is set.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ktrace.h -->