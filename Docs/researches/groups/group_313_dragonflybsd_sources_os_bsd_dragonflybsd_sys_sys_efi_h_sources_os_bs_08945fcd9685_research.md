# Group Research: group_313_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_efi_h_sources_os_bs_08945fcd9685

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/dragonflybsd` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/efi.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/efi.h

`efi.h` defines DragonFly's shared EFI data structures and constants. It covers EFI page sizing, selected EFI configuration table UUIDs, reset types, `efi_char`, `efi_status`, configuration table entries, memory descriptors, time/time-capability structures, table headers, runtime services, and the EFI system table.

Important ABI details include `EFIABI` using `__attribute__((ms_abi))` for runtime-service function pointers, EFI memory descriptor type and attribute constants, and `efi_next_descriptor()` for descriptor-table walking. Under `_KERNEL`, it exposes `efi_systbl_phys`.

This is a low-level firmware ABI header used by kernel EFI runtime/configuration consumers and EFI ioctls.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/efi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/efiio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/efiio.h

`efiio.h` defines the ioctl interface for EFI services exposed through a device interface. It includes `ioccom.h`, `uuid.h`, and `efi.h`.

The ABI structures are `efi_get_table_ioc`, for looking up EFI configuration tables by UUID, and `efi_var_ioc`, for getting, iterating, and setting EFI variables by wide-character name, vendor UUID, attributes, and data buffer.

It declares ioctl command numbers for table lookup, time get/set, variable get/next/set. This header is shared by userland tools and the kernel EFI device implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/efiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf32.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf32.h

`elf32.h` defines the 32-bit class-dependent ELF ABI types and records. It includes `sys/types.h` and `sys/elf_common.h`.

It declares 32-bit `Elf32_*` scalar types, ELF header, section header, program header, dynamic entry, relocation records with and without addends, symbol entries, GNU/Sun versioning structures, version-symbol type, and symbol-info records.

The header also provides macros for packing/unpacking relocation `r_info`, symbol `st_info`, and symbol visibility. It is a pure format-definition header used by loaders, linkers, coredump code, and binary parsers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf64.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf64.h

`elf64.h` defines the 64-bit class-dependent ELF ABI. It includes `sys/types.h` and `sys/elf_common.h`.

It declares 64-bit `Elf64_*` scalar types, 64-bit ELF/section/program/dynamic/relocation/symbol/versioning structures, `Elf64_Nhdr`, move and hardware/software capability entries, and syminfo records. It also defines relocation, move, symbol, and visibility macros.

Compared with `elf32.h`, this header carries 64-bit-specific relocation type-data helpers and capability/move records. It is the 64-bit counterpart used by kernel ELF image activation, coredumps, and format-aware tooling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf_common.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf_common.h

`elf_common.h` contains ELF definitions independent of word size and architecture. It defines `Elf_Note`, identification indexes, magic constants, ELF class/data/OSABI values, `IS_ELF()`, object types, machine IDs, special section indexes, program header types, segment permission flags, section types, section flags, note types, symbol bindings/types/visibility values, dynamic tags, dynamic flags, versioning constants, syminfo constants, and section group flags.

This is the shared vocabulary for `elf32.h`, `elf64.h`, `imgact_elf.h`, loaders, debuggers, coredump handling, and binary utilities. Much of the file mirrors generic ELF, GNU, Solaris, and platform extension registries.

The file is table-like and ABI-sensitive: changing numeric constants or aliases would affect binary compatibility and ELF parsing.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf_generic.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf_generic.h

`elf_generic.h` maps generic `Elf_*`, `ELF_*`, and helper names to either 32-bit or 64-bit ELF definitions based on `__ELF_WORD_SIZE`.

It validates that `__ELF_WORD_SIZE` is 32 or 64, derives `ELF_CLASS` and `ELF_DATA` from machine byte order, defines concatenation helpers such as `__ElfN()`, and provides Linux-compatible `ElfW(x)`. It typedefs common generic names and maps generic relocation/symbol macros to the selected class.

The header must be included after the relevant machine/ELF setup. If `__ELF_WORD_SIZE` is absent, it emits a warning rather than providing generic names.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/elf_generic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/endian.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/endian.h

`endian.h` provides generic endian conversion and unaligned byte-stream encode/decode helpers. It includes `sys/types.h` and `machine/endian.h`.

It defines `_QUAD_HIGHWORD`/`_QUAD_LOWWORD`, `bswap16/32/64`, host-to-big/little and big/little-to-host conversion macros, and inline `be16/32/64dec`, `le16/32/64dec`, `be16/32/64enc`, and `le16/32/64enc`.

The encode/decode helpers operate byte-by-byte, so they are alignment-agnostic and suitable for disk/network formats.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/errno.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/errno.h

`errno.h` defines the DragonFly errno namespace and the userland `errno` access pattern. In non-kernel, non-standalone builds it declares thread-local `errno`, `__errno_location()`, and maps `errno` either through an inline `__error()` or directly to `__errno_location()` for parser compatibility.

The file defines standard POSIX/BSD error constants from `EPERM` through `EOWNERDEAD`, with BSD-visible extras such as `ENOTBLK`, `EFTYPE`, `ENOATTR`, `EDOOFUS`, and `EASYNC`. `ELAST` is 99 under BSD visibility.

Kernel-only pseudo-errors include `ERESTART`, `EJUSTRETURN`, `ENOIOCTL`, and `EMOUNTEXIT`. These are internal syscall/control-flow indicators, not user-visible errno values.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eui64.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/eui64.h

`eui64.h` defines IEEE EUI-64 support. It sets `EUI64_SIZ` for ASCII representation length, `EUI64_LEN` for the eight-byte binary length, and `struct eui64` as an array of eight octets.

For userland it declares conversion helpers: `eui64_aton()`, `eui64_ntoa()`, `eui64_ntohost()`, and `eui64_hostton()`.

This is a small shared ABI/header for link-layer or identifier formatting code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eui64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/event.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/event.h

`event.h` defines DragonFly's kqueue/kevent public ABI and kernel knote infrastructure. Public content includes `EVFILT_*` filter IDs, `EV_SET()`, `struct kevent`, event action flags, returned flags, and `NOTE_*` filter-specific hint bits for user, read/write, exception, vnode, and process events.

For kernel or structure-visible builds, it defines `struct kqinfo`; for `_KERNEL`, it defines `KNOTE`, internal note flags, `filterops`, `struct knote`, scan/timeout flags, copyin/copyout callback types, and prototypes for kqueue/knote operations.

For userland or virtual-kernel builds, it declares `kqueue()` and `kevent()`. This header is both a syscall ABI definition and the central kernel event-notification contract.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eventhandler.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/eventhandler.h

`eventhandler.h` is kernel-only and errors out for normal userland inclusion. It defines dynamic event-handler lists and entries, `eventhandler_tag`, and macro APIs for fast and slow eventhandler declaration, definition, invocation, registration, and deregistration.

Fast lists require a link-time owner via `EVENTHANDLER_FAST_DEFINE`; slow lists are created dynamically and found by name. Handler entries carry priority and an opaque argument.

Kernel prototypes cover `eventhandler_register()`, `eventhandler_deregister()`, and `eventhandler_find_list()`. The file also declares standard shutdown event queues and priority constants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eventhandler.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eventvar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/eventvar.h

`eventvar.h` is a kernel-structure header for internal kqueue state and rejects normal userland inclusion. It includes queue, event, thread, and filedesc definitions.

It defines `KQ_NEVENTS`, `KQEXTENT`, `TAILQ_HEAD(kqlist, knote)`, and `struct kqueue`, including pending/all knote lists, pending count, async signal owner, attached `kqinfo`, file descriptor table pointer, state, sleep count, registration thread, and knote hash table.

The state flags are `KQ_ASYNC` and `KQ_REGWAIT`. This header is consumed by kernel kqueue implementation and structures that embed or inspect kqueues.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/eventvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exec.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/exec.h

`exec.h` defines common exec-related structures. Publicly it defines `struct ps_strings`, the user-stack metadata used by tools such as `ps` to find argv and environment strings, plus `PS_STRINGS` and `SPARE_USRSPACE`.

It declares `struct execsw`, the executable image activator switch with an image-activation function and name. It includes `machine/exec.h` for machine-specific exec definitions.

Under `_KERNEL`, it declares page-mapping helpers for exec image inspection, exec switch registration/unregistration, and macros to define executable image modules through the module subsystem.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exislock.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/exislock.h

`exislock.h` documents and declares DragonFly's existential lock state. The long file comment explains the design: readers enter type-safe critical sections with `exis_hold()`/`exis_drop()` while object owners can unlink, cache, terminate, poll, and eventually reuse/free structures after pseudo-tick grace periods.

The header defines `struct exislock` containing a `pseudo_ticks` deadline/state value, `exislock_t`, and `exis_state_t` values `EXIS_TERMINATE`, `EXIS_NOTCACHED`, `EXIS_CACHED`, and `EXIS_LIVE`.

It declares the global `pseudo_ticks`. The actual inline operations live in `exislock2.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exislock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exislock2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/exislock2.h

`exislock2.h` implements the inline existential lock API declared by `exislock.h`. It includes `globaldata.h` and `machine/thread.h`.

It provides `exis_init()`, `exis_setlive()`, per-CPU and current-CPU hold/drop helpers, `exis_poll()`, `exis_state()`, `exis_usable()`, `exis_freeable()`, `exis_cache()`, and `exis_terminate()`. The functions use per-CPU `gd_exislockcnt`, `gd_exisarmed`, `pseudo_ticks`, and `cpu_ccfence()` to avoid cacheline contention in normal access paths.

The API is subtle: CACHED objects can remain usable during a type-safe critical section even if they concurrently age to NOTCACHED; termination is staged over pseudo-ticks before destruction is safe.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/exislock2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/extattr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/extattr.h

`extattr.h` defines extended filesystem attribute namespaces and the userland extended-attribute syscall API. It defines empty, user, and system namespaces with string names and an initializer macro for namespace-name tables.

Under `_KERNEL`, it defines `EXTATTR_MAXNAMELEN` and forward-declares kernel types. In userland, it declares `extattrctl()`, fd/file/link variants for delete/get/list/set operations, and related types.

This header is the public ABI for TrustedBSD-style extended attributes on DragonFly.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fbio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/fbio.h

`fbio.h` defines framebuffer and video-adapter ioctl structures and constants. It includes `sys/types.h`, `sys/ioccom.h`, and `machine/types.h`.

The older framebuffer interface includes framebuffer type IDs, `struct fbtype`, color-map structures, framebuffer attributes, video on/off control, hardware cursor structures, and corresponding `FBIO*` ioctls. The newer interface defines `video_info_t`, `video_adapter_t`, `video_adapter_info_t`, display-start and palette structures, VGA/EGA/Hercules mode numbers, adapter flags, memory model constants, and more `FBIO_*` control commands.

This is a device ABI header. Structures contain user pointers for colormap/cursor/palette buffers, so ioctl handlers must validate and copy data carefully.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fcntl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/fcntl.h

`fcntl.h` defines open flags, file-status flags, descriptor flags, record locking structures, `fcntl()` command numbers, `at`-family constants, permission bits, advisory locking constants, and userland function declarations.

It distinguishes user open flags from kernel `f_flag` encoding, with kernel conversion macros `FFLAGS()` and `OFLAGS()`. DragonFly-specific or BSD-visible flags include forced blocking/nonblocking/append/offset/sync/async write flags, `O_DIRECT`, close-on-fork support, `F_GETPATH`, `F_MAXFD`, and dup variants with close-on-exec or close-on-fork.

The header declares `struct flock`, kernel `union fcntl_dat`, `open()`, `openat()`, `creat()`, `fcntl()`, `flock()`, `posix_fadvise()`, and `posix_fallocate()` under the appropriate visibility gates.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/file.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/file.h

`file.h` defines the kernel file object and file operation vector. It includes common type/fcntl/unistd headers, and under kernel/structure builds includes event, queue, spinlock, namecache, and uio definitions.

`struct fileops` contains read, write, ioctl, kqfilter, stat, close, shutdown, and seek methods. `struct file` tracks active-list linkage, descriptor type, flags, credentials, ops vector, sequential access state, offset, backing data pointers, reference counts, namecache handle, knote list, and DRM-style private data.

The file declares descriptor type constants such as `DTYPE_VNODE`, `DTYPE_SOCKET`, `DTYPE_KQUEUE`, and `DTYPE_DMABUF`, plus kernel helpers for file reference management, open/read/write/stat/mmap/close/shutdown, bad fileops, and system file limits.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/file2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/file2.h

`file2.h` provides kernel-only inline wrappers around `struct fileops`. It includes `file.h`.

The wrappers call file operations through `fp->f_ops`. Read, write, ioctl, and stat acquire a temporary reference with `fhold()` and release it with `fdrop()` around the operation. Close, shutdown, kqfilter, and seek directly dispatch to the underlying method.

This header centralizes safe fileops dispatch and protects operations that need the file object held during execution.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/file2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/filedesc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/filedesc.h

`filedesc.h` defines kernel file descriptor table structures and descriptor-management APIs. It sets `NDFILE` to 15 built-in descriptors and `NTDCACHEFD` for per-thread fd cache slots.

`struct fdnode` records a file pointer, per-fd flags, occupancy/reservation/subtree metadata, and per-thread caches. `struct filedesc` tracks descriptor arrays, current/root/jail directories as both vnode and namecache handles, file table sizing and high-water state, umask, references, close counters, spinlock, and built-in fd nodes.

It also defines `filedesc_to_leader` for POSIX lock ownership tracking across shared descriptor tables, close-on-exec/fork flags, `struct sigio`, duplication flags, and many kernel routines for allocation, copying, sharing, closing, revoking, holding, and signal-owner management.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/filedesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/filio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/filio.h

`filio.h` defines generic file-descriptor ioctl commands. It includes `ioccom.h`.

It declares `struct fiodname_args` for device-name lookup by file descriptor and defines ioctls for close-on-exec manipulation, readable byte count, nonblocking mode, async mode, signal owner get/set, descriptor type, starting block number, descriptor name, and SEEK_DATA/SEEK_HOLE-style hole/data seeking.

This is a small public ioctl ABI shared by many descriptor-like kernel objects.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/firmware.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/firmware.h

`firmware.h` defines the loadable firmware registration API. `struct firmware` contains a system-wide name, data pointer, byte size, and version.

The API exposes `firmware_register()`, `firmware_unregister()`, `firmware_get()`, and `firmware_put()`, with `FIRMWARE_UNLOAD` allowing unload if unreferenced.

The comments explain the module embedding model: firmware images are registered by unique name, consumers hold references, and multi-image modules treat the first image as master so module unloading is gated by dependent references.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/firmware.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/flame_graph.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/flame_graph.h

`flame_graph.h` defines data structures for per-CPU flame graph sampling. It sets the base symbol name `_flame_graph_ary`, frame depth to 32, and default entry count to 256.

`struct flame_graph_entry` stores an array of instruction-pointer-sized return addresses. `struct flame_graph_pcpu` stores entry count, write index, a pointer to entry storage, and padding/dummy fields, cache-aligned.

This header is data-layout only; sampling and export logic live elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/flame_graph.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fnv_hash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/fnv_hash.h

`fnv_hash.h` implements a 32-bit Fowler/Noll/Vo hash helper. It defines `Fnv32_t`, `FNV1_32_INIT`, and `FNV_32_PRIME`.

The active inline function is `fnv_32_buf()`, which hashes a byte buffer by multiplying by the FNV prime and XORing each byte. A string variant is present but disabled under `#if 0`.

This is a lightweight public-domain utility header for non-cryptographic hashing.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/fnv_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/globaldata.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/globaldata.h

`globaldata.h` defines DragonFly's per-CPU `struct globaldata` for kernel and structure-visible builds. The comment notes that assembler offset generation and module/kernel compatibility depend on this layout.

The structure tracks current/free threads, run queues, CPU IDs/masks, interrupt nesting, VM counters and totals, IPI queues, scheduler/timer state, slab allocator state, vm_map_entry cache, pipe/namecache/sysid caches, tsleep hash, spinlock state, systimer state, vnode counters, debug fields, delayed wakeups, sampling PCs/SPs, per-CPU vmstats, callouts, indefinite-wait state, sysctl lock, and existential-lock counters.

The file defines request flag bit positions/masks such as `RQF_IPIQ`, `RQF_TIMER`, AST masks, scheduler/idle masks, HVM masks, globaldata flags, debug macros, and kernel prototypes `globaldata_find()` and `is_globaldata_space()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/globaldata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gmon.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/gmon.h

`gmon.h` defines profiling data structures used for `gmon.out`/`monstartup()` style profiling. It includes `machine/profile.h`.

It defines `struct gmonhdr`, `GMONVERSION`, histogram counter type, histogram/hash allocation fractions, arc density limits, `struct tostruct`, raw arc records, rounding macros, and `struct gmonparam`, which stores histogram, from/to arc tables, text range, profiling rate, overhead counters, and state.

It declares global `_gmonparam`, profiling state constants, and user-visible `moncontrol()` and `monstartup()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gpt.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/gpt.h

`gpt.h` defines GUID Partition Table on-disk structures and partition type UUID constants. It includes `sys/uuid.h`.

`struct gpt_hdr` models the GPT header, including signature, revision, size, CRCs, self/alternate LBAs, usable range, disk UUID, partition table location, entry count/size, and table CRC. It explicitly pads the structure and asserts the minimum header size when `CTASSERT` is available. `struct gpt_ent` models a 128-byte partition entry with type UUID, unique UUID, LBA range, attributes, and UTF-16 name.

The header defines standard EFI/MBR entries plus DragonFly, FreeBSD, Microsoft, Linux, VMware, Apple, NetBSD, ChromeOS, OpenBSD, BIOS boot, and PReP boot type GUIDs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gtaskqueue.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/gtaskqueue.h

`gtaskqueue.h` is kernel-only and rejects userland inclusion. It defines group taskqueue structures and APIs, derived from FreeBSD taskqueue group support.

It defines task flags, `gtask_fn_t`, `struct gtask`, `struct grouptask`, group task name length, and helpers/macros for initialization and enqueueing. `grouptask` associates a generic task with a taskqueue, unique key, name, device, IRQ resource, and CPU binding.

The API covers queue block/unblock, cancel/drain, grouped enqueue, taskqgroup attach/detach/create/destroy/bind/drain, and SYSINIT-based `TASKQGROUP_DEFINE()`. It declares the `softirq` taskqgroup.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/gtaskqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/hash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/hash.h

`hash.h` provides simple 32-bit non-cryptographic hash helpers using the classic `hash * 33 + c` step. It defines `HASHINIT` as 5381 and `HASHSTEP()` if not already defined.

Inline helpers hash arbitrary buffers, null-terminated strings, bounded strings, strings terminated by a specific character, and bounded strings terminated by a specific character. The terminating variants optionally return the end pointer.

The comments note pathname component hashing as a main use case.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ibaa.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ibaa.h

`ibaa.h` defines state structures and macros for two pseudo-random/state algorithms, without include guards.

It sets `ALPHA`, `SIZE`, `MASK`, `ind(x)`, and `barrel(a)` macros, then defines `struct ibaa_state` with memory/results arrays, accumulator fields, byte index, and memory index.

It also defines `L15_STATE_SIZE` and `struct l15_state` with byte state and indices. The file assumes required integer types are already visible to the includer.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ibaa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/iconv.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/iconv.h

`iconv.h` defines kernel iconv character-set conversion constants, sysctl ABI structures, userland management functions, and kernel converter/module interfaces.

Shared definitions include charset/converter name length limits, maximum charset-pair data length, xlat16 flags, case-conversion flags, Unicode/wctype names, `iconv_cspair_info`, `iconv_add_in`, and `iconv_add_out`. Userland declarations cover adding xlat tables/pairs, converter and charset lookup, and charset quirk handling.

Under `_KERNEL`, it defines converter classes, charset-pair records, module declaration macros for converters and CES modules, core conversion APIs, case conversion APIs, filesystem iconv bridge declarations via `VFS_DECLARE_ICONV`, lookup/helper functions, module handlers, and debug macros.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/iconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/idr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/idr.h

`idr.h` defines a kernel-only integer ID to pointer mapping API compatible with Linux conventions, including support for NULL pointers.

It declares `struct idr_node`, `struct idr`, and APIs to find, replace, remove, remove all, destroy, iterate, allocate new IDs, allocate above a starting ID, pre-grow, initialize, and allocate within a range. The structure tracks node array size, last/free indices, expansion count, maximum wanted ID, and a token for synchronization.

`idr_preload()` and `idr_preload_end()` are Linux-compatibility no-ops in this implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/idr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact.h

`imgact.h` defines exec image-activation state. It includes mount and lwbuf definitions and sets `MAXSHELLCMDLEN` to 128.

`struct image_args` tracks the argument/environment string buffer, argv/env starts, end pointer, executable filename, remaining space, and argument/environment counts. `struct image_params` tracks the executing process, args, executable vnode and attributes, mapped image header, entry address, flags for resident/vmspace/interpreted state, interpreter name, ELF auxargs, first-page mapping cache, BSD/OS `ps_strings`, and exec path storage.

Kernel prototypes cover resident image activation, permission checks, new vmspace setup, and shell-script image activation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact_aout.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact_aout.h

`imgact_aout.h` defines legacy a.out executable header handling. It includes `sys/types.h`.

The header provides macros to get/set magic, machine ID, and flags in host or network byte order; validate magic numbers; compute aligned text/data/relocation/symbol/string offsets; and compute text/data virtual addresses. It supports `OMAGIC`, `NMAGIC`, `ZMAGIC`, and `QMAGIC`.

`struct exec` models the a.out header, with `aout_register_t` optionally forced to 32-bit via `AOUT_H_FORCE32`. The file also defines historical machine IDs and dynamic/PIC flags. It is legacy executable-format ABI support.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact_elf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact_elf.h

`imgact_elf.h` defines kernel ELF image activation and coredump support structures. It includes `elf_common.h` and `machine/elf.h`.

Under `_KERNEL`, it defines `AUXARGS_ENTRY()`, ELF auxiliary argument and brand-info structures, brand note metadata, generic typedefs through `__ElfType()`, maximum brand count, brand flags, and brand-note flags.

It declares brand registration/removal/in-use functions, DragonFly stack fixup, ELF coredump routines, generic coredump support, and the DragonFly brand note. This header connects ELF format parsing with exec emulation/branding and core generation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/imgact_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/in_cksum.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/in_cksum.h

`in_cksum.h` defines Internet checksum helpers. It includes `sys/types.h` and `machine/stdint.h`.

Kernel-only declarations include `in_cksum_range()` for mbuf ranges and `asm_ones32()` for 32-bit-word summing, plus inline wrappers `in_cksum()`, `in_cksum_skip()`, and `in_cksum_hdr()` for IPv4 headers.

The header also provides inline assembly helpers `in_addword()` and `in_pseudo()` for one's-complement addition and pseudo-header checksum folding. The inline assembly makes this architecture-specific despite being under `sys`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/in_cksum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/indefinite.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/indefinite.h

`indefinite.h` defines state for tracking indefinite waits in contention loops. It includes `machine/clock.h`.

It declares `lock_test_mode` and `indefinite_uses_rdtsc`, defines `struct indefinite_info` with timing base, lock address, identifier, elapsed seconds, loop count, type, and reported flag, and typedefs it as `indefinite_info_t`.

`INDEF_INFO_START` controls how many loop iterations occur before timing begins. The inline operational logic is in `indefinite2.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/indefinite.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/indefinite2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/indefinite2.h

`indefinite2.h` implements inline indefinite-wait tracking. It includes `indefinite.h` and `globaldata.h`.

`indefinite_init()` initializes wait state and optionally reports the lock name/address in per-CPU counters. `indefinite_check()` pauses or yields in a loop, starts timing after `INDEF_INFO_START`, periodically computes elapsed time via TSC or ticks, updates collision counters, emits warnings by lock type, can print backtraces under `INVARIANTS`, and panics after prolonged spin-lock waits. `indefinite_done()` records final collision time and disables tracking.

This header is used by lock/spin/token loops to diagnose and account for long waits.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/indefinite2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/inflate.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/inflate.h

`inflate.h` declares a small reentrant gzip/deflate inflate interface for kernel or `KZIP` builds. It defines `GZ_EOF` and `GZ_WSIZE`.

`struct inflate` carries caller-private data, input and output callbacks, and private inflate state such as bit buffer, bit count, memory-use tracking, fixed Huffman table pointers, fixed table bit widths, sliding window, and write pointer.

It declares `inflate(struct inflate *)`. The callback-based state object makes the decompressor reusable without global mutable state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/inflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/interrupt.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/interrupt.h

`interrupt.h` defines system interrupt numbering limits and kernel interrupt registration APIs. It sets maximum hard interrupts to 192, soft interrupts to 64, and derives `FIRST_SOFTINT` and `MAX_INTS`.

It defines `inthand2_t`, soft interrupt numbers in priority order, and corresponding pending-bit masks. Shared aliases include `SWI_CRYPTO` over `SWI_CAMNET`.

Under `_KERNEL`, it declares registration/unregistration for software and hardware interrupts, random interrupt registration, counter access, scheduler entry points for hard/soft interrupt threads, virtual-kernel interrupt hooks, and interrupt-name string tables.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/interrupt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ioccom.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ioccom.h

`ioccom.h` defines the ioctl command encoding scheme. It reserves lower bits for group/number and upper bits for parameter size and direction.

It defines parameter-size masks, helpers `IOCPARM_LEN()`, `IOCBASECMD()`, `IOCGROUP()`, max parameter size, direction flags `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`, and construction macros `_IOC`, `_IO`, `_IOWINT`, `_IOR`, `_IOW`, and `_IOWR`.

For userland or virtual-kernel builds it declares `ioctl(int, unsigned long, ...)`. Many other headers in this group build their ioctl constants on this file.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ioccom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ioctl.h

`ioctl.h` is an umbrella public ioctl header. If included in the kernel, it emits a warning advising kernel code to include specific `xxxio.h` headers instead.

It includes `sys/filio.h`, `sys/sockio.h`, and `sys/ttycom.h`.

The file contains no command definitions of its own beyond aggregating common file, socket, and tty ioctl definitions for userland consumers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/iosched.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/iosched.h

`iosched.h` defines small I/O scheduler accounting structures and kernel hooks. Kernel/structure builds include type, queue, and systimer headers.

`struct iosched_data` records read bytes, write bytes, and the last tick value used for decay/accounting.

Under `_KERNEL`, it forward-declares `struct thread` and declares `bwillwrite()`, `bwillread()`, `bwillinode()`, and `biosched_done()`. This is a compact interface between buffer/cache I/O paths and scheduler accounting.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/iosched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ipc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ipc.h

`ipc.h` defines SVID/System V IPC common types, permission structure, constants, and helper macros. It includes `sys/cdefs.h` and `machine/stdint.h`, and conditionally typedefs `gid_t`, `key_t`, `mode_t`, and `uid_t`.

`struct ipc_perm` stores creator/current UID/GID, permission mode, sequence number, and user-specified key. Constants include BSD-visible read/write/control permission bits, `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, `IPC_PRIVATE`, and control operations `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.

Kernel builds get ID/index/sequence conversion macros and `ipcperm()`. Userland gets the historical `ftok()` declaration.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ipmi.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ipmi.h

`ipmi.h` defines the IPMI user/kernel ioctl ABI and message structures. It includes `ioccom.h`.

The header defines address/data-size limits, BMC defaults, IPMI address types, ioctl command constants for receiving, sending, command registration, event command configuration, address get/set, and LUN get/set, plus receive types and common application command constants such as get device ID, get/clear message flags, watchdog commands, and watchdog action bits.

It declares `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`, generic/system-interface/IPMB address structures, and amd64 32-bit compatibility ioctl structures with 32-bit pointer fields. This is a pointer-bearing ioctl ABI, so compatibility and copyin/copyout handling are central to its consumers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ipmi.h -->