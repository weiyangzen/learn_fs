# Group Research: group_617_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__94fed751cb11

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_ioctl.h

## Role

Defines private ioctl data shared between the SD card `cfgadm` plugin and the illumos SDA framework.

## Key Interfaces

- `sda_card_type_t` enumerates unknown, MMC, SD memory, SDHC, SD combo, and SDIO card classes.
- `sda_card_info_t` reports card type plus memory-card identity fields: manufacturer, OEM ID, product ID, serial, date, and revision.
- `struct sda_ap_control` carries AP-control command, payload size, and payload pointer.
- Kernel-only `struct sda_ap_control32` provides ILP32-compatible fields.

## Commands

Defines AP-control commands for card-info lookup, device-path lookup, and slot reset:
`SDA_CFGA_GET_CARD_INFO`, `SDA_CFGA_GET_DEVICE_PATH`, `SDA_CFGA_RESET_SLOT`.

## Risk Notes

This is a private plugin/kernel control ABI. Structure layout, command numbering, and 32-bit compatibility fields must stay synchronized with both cfgadm-side and framework-side consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt.h

## Role

Defines public static DTrace probe macros and the lightweight probe descriptor used by SDT instrumentation.

## Key Interfaces

- Userland `DTRACE_PROBE` through `DTRACE_PROBE5` declare and call provider-qualified `__dtrace_<provider>___<name>` functions with `unsigned long` arguments.
- Kernel `DTRACE_PROBE` through `DTRACE_PROBE8` declare and call `__dtrace_probe_<name>` functions with `uintptr_t` arguments.
- Provider convenience macros cover scheduler, process, I/O, iSCSI, NFSv3/v4, SMB/SMB2, IP, TCP, UDP, sysevent, XPV, Fibre Channel, and SRP probe namespaces.
- `SET_ERROR(err)` emits the `set-error` probe and evaluates back to `err`.
- `sdt_probedesc_t` records static probe name, patched instruction offset, and linked-list membership.
- Exports `sdt_prefix`.

## Semantics

Kernel probe macros include explicit type parameters for DTrace type metadata but cast runtime arguments to `uintptr_t`. `SET_ERROR()` evaluates its argument twice, so callers must not pass side-effecting expressions.

## Risk Notes

Probe names are encoded by macro token-pasting and become observable DTrace provider ABI. Renaming or changing arity breaks scripts and provider metadata.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt_impl.h

## Role

Defines private SDT provider/probe implementation structures used by the DTrace SDT module and kernel runtime linker patching.

## Key Interfaces

- x86 instruction constants: `SDT_CALL`, `SDT_NOP`, `SDT_RET`, and `SDT_OFF_RET_IDX`.
- `sdt_instr_t` is `uint8_t` on x86 and `uint32_t` elsewhere.
- `sdt_provider_t` describes a provider name, probe-name prefix, stability attributes, privilege, and provider ID.
- `sdt_probe_t` tracks provider, name allocation, DTrace ID, owning module, load count, primary-module status, patch point, saved/patch instruction values, tail-call status, and list/hash links.
- `sdt_argdesc_t` maps provider/probe/argument index to native and translated DTrace argument types.
- Exports `sdt_providers[]`, `sdt_getargdesc()`, and `sdt_mode()`.

## Risk Notes

This header is coupled to instruction patching and module load accounting. Architecture-specific instruction sizes and tail-call handling must match krtld and SDT activation logic exactly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/secflags.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/secflags.h

## Role

Defines process security-flag sets, deltas, names, and validation interfaces.

## Key Interfaces

- `secflagset_t` is a 64-bit bitset.
- `psecflags_t` stores effective, inherit, lower, and upper process security flag sets.
- `secflagdelta_t` represents add/remove/assign operations.
- `psecflagwhich_t` selects which process flag set is targeted.
- `secflag_t` currently defines `PROC_SEC_ASLR`, `PROC_SEC_FORBIDNULLMAP`, and `PROC_SEC_NOEXECSTACK`.
- Helper APIs manipulate sets, convert names, validate deltas, produce defaults, and stringify flags.
- Userland exposes `secflags_parse()` and `psecflags()`.
- Kernel exposes `secflag_enabled()`, `secflags_promote()`, and `secflags_apply_delta()`.

## Risk Notes

`PROC_SEC_MASK` defines the valid bit universe. Validation must preserve the lower/effective/inherit/upper constraints or process hardening policy can be bypassed or made impossible to change.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/secflags.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/select.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/select.h

## Role

Defines `fd_set`, descriptor-set manipulation macros, `select()`, and `pselect()` declarations with illumos standards-visibility handling.

## Key Interfaces

- Duplicates `sigset_t` where necessary to avoid inclusion-order problems with `signal.h`.
- Default `FD_SETSIZE` is `65536`.
- Defines `fd_mask`, `fds_mask`, `NFDBITS`, `FD_NFDBITS`, `howmany`, and `__howmany`.
- `fd_set` stores descriptor bits in `long fds_bits[]`.
- `FD_SET`, `FD_CLR`, `FD_ISSET`, and `FD_ZERO` manipulate descriptor sets.
- Userland declares `select()` and, under the appropriate namespace, `pselect()`.

## Compatibility Notes

The header carefully gates type names and prototypes for X/Open, POSIX, extensions, kernel, and fake-kernel builds. `FD_ZERO` maps to `bzero()` in kernel-like builds and `_memset()` in userland.

## Risk Notes

`fd_set` size and bit arithmetic are ABI-visible. Changes to `FD_SETSIZE`, word sizing, or standards gates affect application binary and source compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/select.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem.h

## Role

Defines the public System V IPC semaphore ABI.

## Key Interfaces

- Permission bits: `SEM_A` for alter and `SEM_R` for read.
- Operation flag: `SEM_UNDO`.
- `semctl()` command constants: `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, and `SETALL`.
- `struct semid_ds` contains IPC permissions, base semaphore pointer, count, operation/change times, binary semaphore marker, and reserved padding.
- `struct sembuf` describes one `semop()` operation.
- Userland prototypes: `semctl()`, `semget()`, `semids()`, `semop()`, and extension `semtimedop()`.

## Compatibility Notes

`struct semid_ds` includes explicit 32-bit padding for future `time_t` expansion while preserving LP64 layout.

## Risk Notes

This is public IPC ABI. Command numbers, structure layout, and time padding are externally visible and must remain compatible with existing binaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem_impl.h

## Role

Defines private System V semaphore implementation structures, semsys subcodes, and ILP32 compatibility layout.

## Key Interfaces

- `semsys()` subcodes: `SEMCTL`, `SEMGET`, `SEMOP`, `SEMIDS`, `SEMTIMEDOP`.
- `ksemid_t` is the kernel semaphore-set descriptor, with `kipc_perm_t`, semaphore array, counts, timestamps, binary flag, maximum operations, and undo-list membership.
- `struct sem` stores value, last operation PID, wait counts, and condition variables for nonzero/zero waiters.
- `struct sem_undo` links per-process undo state by AVL and active undo list, with adjust-on-exit values.
- `struct semid_ds32` is the LP64 kernel view of the ILP32 public structure.
- Kernel exports `semexit()`.

## Risk Notes

Undo tracking and wait counters are core semaphore semantics. The flexible `un_aoe[1]` tail allocation and 32-bit layout must match allocation and copyout logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sema_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sema_impl.h

## Role

Defines the private in-kernel semaphore representation used underneath the public `ksema_t` interface.

## Key Interfaces

- `sema_impl_t` contains:
  - `s_slpq`: sleep queue pointer to blocked threads.
  - `s_count`: current semaphore count.

## Dependencies

Includes basic types and machine lock definitions outside assembly builds.

## Risk Notes

The public `ksema_t` in `semaphore.h` is opaque but sized to fit this representation. Layout changes must preserve that relationship and any assembly/kernel synchronization assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sema_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/semaphore.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/semaphore.h

## Role

Provides the public illumos kernel semaphore interface documented by `semaphore(9F)`.

## Key Interfaces

- `ksema_type_t` distinguishes `SEMA_DEFAULT` and `SEMA_DRIVER`.
- `ksema_t` is an opaque two-word semaphore object.
- Kernel macro `SEMA_HELD(x)` maps to `sema_held(x)`.
- Kernel functions:
  - `sema_init()`
  - `sema_destroy()`
  - `sema_p()`
  - `sema_p_sig()`
  - `sema_v()`
  - `sema_tryp()`
  - `sema_held()`

## Risk Notes

This is a stable driver-facing synchronization ABI. The opaque object size and initialization contract must remain compatible with compiled drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/semaphore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sendfile.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sendfile.h

## Role

Defines the `sendfile()` and `sendfilev()` user ABI, vector layouts, large-file remapping, and syscall subcodes.

## Key Interfaces

- `sendfilevec_t` describes one source: file descriptor, flags, offset, and length.
- `SFV_NOWAIT` requests nonblocking behavior.
- Large-file `sendfilevec64_t` is exposed under `_LARGEFILE64_SOURCE`.
- Kernel syscall32 structures handle ILP32 and ILP32-largefile copyin; the 64-bit variant uses packing on amd64 where needed.
- `SFV_FD_SELF` permits self-process data as a source.
- Subcodes: `SENDFILEV` and `SENDFILEV64`.
- Userland declares `sendfilev()`, `sendfile()`, and transitional `sendfilev64()`/`sendfile64()`.

## Compatibility Notes

The header uses `redefine_extname` or macros to map 32-bit `_FILE_OFFSET_BITS=64` applications to the 64-bit interfaces, while LP64 maps largefile aliases back to native names.

## Risk Notes

Vector layout, packing, and large-file symbol mapping are ABI-critical for 32-bit and 64-bit applications.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sendfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sensors.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sensors.h

## Role

Defines evolving consolidated sensor ioctl structures and kernel sensor registration interfaces.

## Key Interfaces

- Sensor kinds: unknown, temperature, voltage, current, and synthetic.
- Sensor units: unknown, Celsius, Fahrenheit, Kelvin, volts, amps, and none.
- Ioctl namespace `SENSOR_IOCTL`, with `SENSOR_IOCTL_KIND` and `SENSOR_IOCTL_SCALAR`.
- `sensor_ioctl_kind_t` reports kind and derivation.
- `sensor_ioctl_scalar_t` reports unit, signed granularity, precision, padding, and signed value.
- Kernel callback types `ksensor_kind_f` and `ksensor_scalar_f`.
- `ksensor_ops_t` groups kind and scalar callbacks.
- Kernel helpers create typed sensors, PCI scalar sensors, and remove one or all sensor IDs.

## Semantics

Scalar values are expressed through `sis_value` plus signed `sis_gran`: positive granularity divides the value into subunits; negative granularity multiplies.

## Risk Notes

The file explicitly marks these interfaces unstable. Consumers should expect ioctl and kernel API evolution.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sensors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ser_sync.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ser_sync.h

## Role

Defines synchronous serial line ioctls, mode/status/statistics structures, and private STREAMS state for sync serial drivers.

## Key Interfaces

- Ioctls cover get/set SCC mode, statistics, speed, MRU/MTU, modem control, and DTR.
- `struct scc_mode` carries transmit/receive clock source, inversion flags, connection config, baud rate, and validation error mask.
- Clock constants describe external clocks, baud generators, PLL, system clock, and inversion modes.
- Connection flags cover half duplex, multipoint, IBM-SDLC, modem-signal reporting, NRZI, loopback, and echo.
- `struct sl_status` reports modem/link events with timestamp; `sl_status32` is syscall32-compatible.
- `struct sl_stats` counts packets, bytes, aborts, CRCs, CTS/DCD events, underrun/overrun, and buffer failures.
- `struct ser_str` and `struct syncline` describe per-stream and protocol private driver state.

## State Flags

Defines transmit-state bits (`TX_IDLE`, `TX_ACTIVE`, `TX_ABORTED`, etc.), link flags (`SF_FDXPTP`, `SF_LINKERR`, etc.), clone-open state, and watchdog timing macros.

## Risk Notes

This header mixes ioctl ABI with driver-private STREAMS layout. Ioctl values/status constants are externally visible, while private fields must match driver implementation assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ser_sync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/serializer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/serializer.h

## Role

Declares an unstable kernel-only STREAMS serializer interface.

## Key Interfaces

- Opaque `serializer_t`.
- Callback type `srproc_t(mblk_t *, void *)`.
- Kernel functions:
  - `serializer_init()`
  - `serializer_create()`
  - `serializer_enter()`
  - `serializer_wait()`
  - `serializer_destroy()`

## Dependencies

Kernel builds include STREAMS message block definitions and kernel memory allocation support.

## Risk Notes

The header explicitly says it is not public and is unstable. Callers depend on serialized callback execution and must honor message ownership/lifetime conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/serializer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/session.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/session.h

## Role

Defines kernel session state, controlling terminal references, locking rules, and session-management entry points.

## Key Interfaces

- `sess_t` stores immutable session ID pointer plus lock-protected reference count, controlling TTY state, exit state, active TTY users, device, vnode, and credentials.
- `s_sid` aliases `s_sidp->pid_id`.
- Exports kernel `session0`.
- Kernel functions include session reference handling, controlling TTY hold/release, session creation, STREAMS controlling-TTY setup, freeing controlling TTY, querying controlling TTY device, and clearing SIGHUP state.

## Locking Contract

The header documents lock order as `sd_lock -> pidlock -> p_splock -> s_lock`. `pidlock` or `p_splock` protects `proc_t::p_sessp`; `s_lock` protects session contents. `tty_hold()` prevents controlling TTY changes by incrementing `s_cnt`.

## Risk Notes

Session and controlling-terminal logic is lock-order sensitive. Direct mutation outside session management code risks races with process session changes and terminal hangup behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/session.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1.h

## Role

Declares SHA-1 context layout and incremental hashing functions.

## Key Interfaces

- `SHA1_CTX` contains:
  - `uint32_t state[5]`
  - `uint32_t count[2]`
  - 64-byte buffered input union as bytes or aligned words
- Constants:
  - `SHA1_BLOCK_LENGTH` = 64
  - `SHA1_DIGEST_LENGTH` = 20
- Functions:
  - `SHA1Init()`
  - `SHA1Update()`
  - `SHA1Final()`

## Compatibility Notes

The file warns that the Niagara2 RNG driver directly accesses `SHA1_CTX::state`; it must remain a `uint32_t state[5]`.

## Risk Notes

Despite being a hash context, the structure layout is consumed directly by another driver. Reordering or resizing fields can break kernel consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1_consts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1_consts.h

## Role

Defines SHA-1 round constants and architecture-dependent constant-loading policy.

## Key Interfaces

- Exports `sha1_consts[]`.
- On SPARC, `SHA1_CONST(x)` loads from `sha1_consts[x]`.
- On other architectures, `SHA1_CONST(x)` expands to immediate `SHA1_CONST_<x>`.
- Defines FIPS 180-1 constants `SHA1_CONST_0` through `SHA1_CONST_3`.

## Rationale

SPARC loads 32-bit constants more cheaply from memory than from synthesized immediates, while Intel and other processors generally benefit from direct constants.

## Risk Notes

The macro must match implementation expectations in `SHA1Transform()`. Constant values are algorithm-defined and must not change.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1_consts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2.h

## Role

Declares SHA-2 context layout, digest/HMAC sizing constants, algorithm IDs, and SHA-256/384/512 function interfaces.

## Key Interfaces

- Digest lengths for SHA-256, SHA-384, SHA-512, SHA-512/224, and SHA-512/256.
- HMAC key and block-size constants.
- Algorithm constants from `SHA256` through `SHA512_256`.
- `SHA2_CTX` stores algorithm type, 32-bit or 64-bit state, 64-bit or 128-bit bit count, and 128-byte input buffer.
- Typedefs alias `SHA256_CTX`, `SHA384_CTX`, and `SHA512_CTX` to `SHA2_CTX`.
- Generic `SHA2Init()`, `SHA2Update()`, `SHA2Final()`.
- Algorithm-specific init/update/final functions for SHA-256, SHA-384, and SHA-512.
- Under `_SHA2_IMPL`, defines internal `sha2_mech_type_t`.

## Risk Notes

The internal mechanism enum order is used by division/modulus calculations in the module; adding or reordering mechanisms requires care. Consumers are told not to inspect context fields directly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2_consts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2_consts.h

## Role

Defines SHA-256 and SHA-512 round constants and architecture-dependent constant-loading macros.

## Key Interfaces

- Exports `sha256_consts[]` and `sha512_consts[]`.
- On SPARC, `SHA256_CONST(x)` and `SHA512_CONST(x)` load from arrays.
- On other architectures, they expand to immediate `SHA256_CONST_<x>` and `SHA512_CONST_<x>`.
- Defines all 64 SHA-256 constants and all 80 SHA-512 constants from FIPS 180-2.
- SHA-512 constants are also used for SHA-384.

## Risk Notes

These are algorithm constants. Any typo or mismatch changes digest output. The SPARC array path must remain synchronized with the macro constant set.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2_consts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/share.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/share.h

## Role

Defines file share reservation structures and kernel helpers for vnode share locking.

## Key Interfaces

- `MAX_SHR_OWNER_LEN` is 1024 bytes.
- `struct shr_locowner` identifies local owners by PID and ID.
- `struct shrlock` stores access mode, deny mode, system ID, PID, opaque owner length, and opaque owner pointer.
- `struct shrlocklist` links share locks.
- Kernel/fake-kernel helpers:
  - `add_share()`
  - `del_share()`
  - `cleanshares()`
  - `cleanshares_by_sysid()`
  - `shr_has_remote_shares()`
  - `proc_has_nbmand_share_on_vp()`

## Risk Notes

Share-lock owner matching depends on `s_sysid`, `s_pid`, `s_own_len`, and opaque owner data. Incorrect cleanup can leave stale local or remote share reservations on vnodes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/share.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm.h

## Role

Defines the public System V shared memory ABI.

## Key Interfaces

- `SHMLBA` is page size in kernel/kmemuser builds and `_sysconf(_SC_PAGESIZE)` in userland.
- Permissions: `SHM_R`, `SHM_W`.
- Attach flags: `SHM_RDONLY`, `SHM_RND`, `SHM_SHARE_MMU`, `SHM_PAGEABLE`.
- `SHMAT_VALID_FLAGS_MASK` lists valid `shmat()` flags.
- `shmatt_t` represents attach counts.
- `struct shmid_ds` contains IPC permissions, segment size, anon-map pointer, lock count, creator/last-operation PIDs, attach counts, timestamps, and reserved padding.
- Control operations: `SHM_LOCK`, `SHM_UNLOCK`.
- Userland prototypes: `shmget()`, `shmids()`, `shmctl()`, `shmat()`, and `shmdt()`.

## Compatibility Notes

The public structure uses LP64 and ILP32 padding branches for pointer visibility and future `time_t` expansion.

## Risk Notes

Shared-memory segment layout and flag values are public ABI. `SHMLBA` must remain a power-of-two low-boundary multiple for address rounding semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm_impl.h

## Role

Defines private System V shared-memory implementation structures, syscall subcodes, and 32-bit compatibility layout.

## Key Interfaces

- `shmsys()` subcodes: `SHMAT`, `SHMCTL`, `SHMDT`, `SHMGET`, `SHMIDS`.
- `kshmid_t` is the kernel segment descriptor with permissions, segment size, anon map, lock counts, lock mutex, PIDs, ISM attach count, timestamps, shared page table info, and legacy reserved field.
- `SHMSA_ISM` marks shared page table usage in segment accounting.
- `sptinfo_t` references a dummy address space for ISM segment handling.
- `segacct_t`, protected by `p_lock`, records per-process attached segment accounting in an AVL tree.
- Error codes `SHMID_NONE` and `SHMID_FREE` are used by `shmgetid()`.
- Kernel functions: `shminit()`, `shmfork()`, `shmexit()`, `shmgetid()`.
- `struct shmid_ds32` is the ILP32 public layout for LP64 kernels.

## Risk Notes

ISM/shared-page-table fields and per-process `segacct_t` state are sensitive to fork/exit/detach behavior. 32-bit layout must match copyin/copyout translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sid.h

## Role

Defines kernel SID/domain credential structures and userland SID/idmap syscall wrappers.

## Key Interfaces

- `sidsys` subcodes cover ID allocation, idmap registration/unregistration, kernel cache flush, SID-to-ID, and ID-to-SID operations.
- Kernel `ksiddomain_t` stores refcounted domain names in AVL trees.
- `ksid_t` combines cached UID/GID, RID, attributes, and domain pointer.
- `ksid_index_t` selects user, group, or owner SID slots.
- `ksidlist_t` stores refcounted SID arrays plus sorted ID pointers and ephemeral-ID count.
- `credsid_t` stores refcounted credential SID data and SID list.
- Kernel helpers manage lookup, holds/releases, credential SID updates, SID-list membership, and group-to-SID conversion.
- Userland exposes `allocids()`, `__idmap_reg()`, `__idmap_unreg()`, and `__idmap_flush_kcache()`.

## Risk Notes

SID credential substructures are refcounted because credential memory cannot be allocated while holding `p_crlock`. Incorrect hold/release behavior can corrupt credential SID state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/siginfo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/siginfo.h

## Role

Defines signal information ABI structures, signal codes, queued-signal kernel structures, and 32-bit translation interfaces.

## Key Interfaces

- Defines `union sigval`, kernel ILP32 `sigval32`, `struct sigevent`, `sigevent32`, and `SIGEV_*` notification modes.
- Signal-origin macros: `SI_FROMUSER()` and `SI_FROMKERNEL()`.
- Signal codes include `SI_NOINFO`, `SI_DTRACE`, `SI_RCTL`, `SI_USER`, `SI_LWP`, `SI_QUEUE`, `SI_TIMER`, `SI_ASYNCIO`, and `SI_MESGQ`.
- Pulls machine-dependent codes from `machsig.h` and defines trap, child, poll, and profile codes.
- `siginfo_t` is the padded public ABI with process, fault, file, profiling, and rctl unions.
- `siginfo32_t` is the kernel view of ILP32 `siginfo_t`.
- `k_siginfo_t` is the smaller internal version without public padding.
- `sigqueue_t` stores queued signal info plus destructor/backpointer metadata.
- Field aliases expose `si_pid`, `si_addr`, `si_value`, `si_status`, `si_entity`, and related members.
- `_SYSCALL32_IMPL` declares `siginfo_kto32()` and `siginfo_32tok()`.

## Risk Notes

Public padding sizes differ between LP64 and ILP32 and are ABI-fixed. `k_siginfo_t` must remain semantically synchronized with `siginfo_t` while intentionally omitting bulk padding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/siginfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signal.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signal.h

## Role

Defines the main illumos signal ABI beyond ISO C: signal sets, `sigaction`, alt stacks, signotify, kernel masks, signal queueing, and signal-set helpers.

## Key Interfaces

- Includes ISO signal definitions and conditionally includes `siginfo.h`.
- Duplicates `sigset_t` for XPG compatibility and defines compact kernel `k_sigset_t`.
- `struct sigaction` stores flags, overlapped handler/sigaction function pointer, mask, and ILP32 reserved padding.
- `struct sigaction32` is the kernel view of ILP32 sigaction.
- Defines `SA_*` flags, `NSIG`, `MAXSIG`, stack sizes, `SS_*` flags, `stack_t`, and `stack32_t`.
- `signotify_id_t` and syscall command constants support libc notification for mqueue/aio.
- Kernel exports standard signal masks, bit macros, mask conversion helpers, `sigsend_t`, `signotifyq_t`, `sigqhdr_t`, queue-size limits, and signal-set manipulation functions.
- Kernel declares `kill()`.

## Compatibility Notes

Most definitions are guarded by standards namespace macros. `NSIG`/`MAXSIG` are exposed only where extensions or non-XPG constraints allow.

## Risk Notes

Signal masks assume `MAXSIG` fits three 32-bit kernel words. Changes to signal numbering or mask width require updates to fill/cannot-mask constants and user/kernel conversion macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signalfd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signalfd.h

## Role

Defines illumos support for Linux-compatible `signalfd`.

## Key Interfaces

- Linux-compatible flags:
  - `SFD_CLOEXEC`
  - `SFD_NONBLOCK`
- Native private ioctl namespace:
  - `SIGNALFDIOC`
  - `SIGNALFDIOC_MASK`
- `signalfd_siginfo_t` is a 128-byte Linux-compatible signal-info record with signal number, errno, code, sender PID/UID, fd, band, trap, status, CPU times, address, and reserved padding.
- Userland declares `signalfd()`.
- Kernel minor names distinguish signalfd and clone devices.
- Kernel `sigfd_proc_state_t`, protected by `p_lock`, stores poll wake callback and a list of signalfd state.
- Exports kernel hook `sigfd_exit_helper`.

## Risk Notes

The header explicitly targets Linux binary compatibility for flags and struct size. Extending fields independently of Linux would break that contract.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signalfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/skein.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/skein.h

## Role

Declares the Skein hash API, context structures, optional extended initialization, tree/MAC support, and KCF mechanism metadata.

## Key Interfaces

- Return codes: `SKEIN_SUCCESS`, `SKEIN_FAIL`, `SKEIN_BAD_HASHLEN`.
- Defines state/block sizes for Skein-256, Skein-512, and Skein-1024.
- `Skein_Ctxt_Hdr_t` stores hash output bit length, buffered byte count, and two tweak words.
- Context structs for 256/512/1024 variants store common header, chaining variables, and aligned partial-block buffers.
- Incremental hash APIs: `Init`, `Update`, `Final`.
- Extended APIs: `InitExt`, `Final_Pad`, and, when enabled, `Output`.
- `skein_param_t` carries digest bit length for KCF hashing.
- Under `SKEIN_MODULE_IMPL`, defines mechanism strings, mechanism enum, and digest/MAC validation macros.

## Risk Notes

The context layout is algorithm-specific and may be copied for precomputed IV/MAC state reuse. Mechanism enum ranges are used by validation macros and must remain coherent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/skein.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sleepq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sleepq.h

## Role

Defines common sleep queue structures for traditional sleep queues and turnstile constituents.

## Key Interfaces

- `sleepq_t` stores the first sleeping thread.
- `sleepq_head_t` combines a sleep queue with a dispatcher lock for a hash bucket.
- Kernel constants/macros:
  - `NSLEEPQ` = 2048
  - `SQHASHINDEX(X)` computes a mixed pointer hash.
  - `SQHASH(X)` locates the bucket head.
- Exports `sleepq_head[]`.
- Kernel functions insert, wake one/all by channel, unsleep, dequeue, and unlink threads.

## Risk Notes

Sleep queue hashing and locking are scheduler/synchronization infrastructure. Pointer hashing must preserve bucket distribution, and callers must observe dispatcher-lock expectations around queue mutation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sleepq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios.h

## Role

Defines the unstable illumos SMBIOS access API shared by `libsmbios` and the kernel SMBIOS module. It covers SMBIOS entry points, DMTF structure type IDs, decoded structure records, enumeration constants, access functions, formatting helpers, and kernel snapshot globals.

## Entry Points and Types

- `smbios_entry_point_t` distinguishes SMBIOS 2.1 and 3.0 entry point formats.
- Packed `smbios_21_entry_t` and `smbios_30_entry_t` mirror the DMTF table entry point layouts.
- `smbios_entry_t` unions the two entry point formats.
- Defines entry anchor strings, maximum entry length, standard structure types 0 through 46, inactive/end-of-table types, OEM range, and Sun/Oxide OEM extension type IDs.

## Decoded Records

The file defines decoded structures for BIOS, system, baseboard, chassis and chassis elements, processor, cache, port, slot and slot peers, onboard devices, language, event log, memory arrays/devices/maps, pointing devices, batteries, hardware security, voltage/cooling/temperature/current probes, boot status, management devices/components, IPMI, power supplies, additional information, extended onboard devices, TPM, processor additional information including RISC-V details, firmware inventory, string properties, and OEM processor/port/PCIe/memory extensions.

## Constants and Enumerations

Large groups of constants encode DMTF values for BIOS flags, wake events, board/chassis classes, processor families/upgrades/characteristics, cache types, connector/port/slot kinds, memory technologies and capabilities, probes, power supplies, TPM characteristics, RISC-V ISA/privilege/width, firmware state/formats, and string property IDs. `SMB_VERSION` currently maps to SMBIOS 3.9.

## Access API

- Open sources: `smbios_open()`, `smbios_fdopen()`, `smbios_bufopen()`.
- Buffer/checksum/write/close helpers.
- Error and truncation helpers.
- Lookup and iteration: `smbios_lookup_id()`, `smbios_lookup_type()`, `smbios_iter()`.
- Information functions decode each supported SMBIOS structure into the typed records above.
- Free helpers release allocated arrays for chassis elements, slot peers, extended memory chip-selects, additional info entries, and firmware components.
- `smbios_psn()` and `smbios_csn()` return product and chassis serial numbers.
- Userland-only `*_desc()` and `*_name()` helpers convert enumeration values to human-readable strings or macro names.
- Kernel exports `ksmbios` and `ksmbios_flags`.

## Risk Notes

This header is intentionally unstable, but it is still a broad ABI between the parser, utilities, and kernel consumers. Packed entry-point layouts, handle constants, version negotiation, decoded struct fields, and free-function ownership rules must stay synchronized with parser implementation and generated string tables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios.h -->