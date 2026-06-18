# Group Research: group_570_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__0acf9f70df74

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/illumos/illumos-gate`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_oss.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_oss.h

This header defines the illumos/Solaris OSS compatibility ABI for `/dev/dsp` and `/dev/mixer`. It is primarily a public ioctl and constant definition file, with many entries retained for source compatibility with OSS applications even where Solaris does not implement the behavior.

Key contents:
- OSS buffer, pointer, sync, error, digital control, system info, mixer extension, audio info, mixer info, and card info structs.
- OSS ioctl encoding macros: `OSSIOC_*`, `__OSSIO*`.
- Global OSS4-style ioctl commands such as `SNDCTL_SYSINFO`, `SNDCTL_AUDIOINFO`, `SNDCTL_MIX_*`, `SNDCTL_DSP_*`.
- Legacy OSS mixer constants and source compatibility macros such as `SOUND_MIXER_*`, `SOUND_MASK_*`, and `MIXER_READ/WRITE`.
- Audio format masks `AFMT_*`, native/opposite endian aliases, PCM capability masks, trigger masks, channel binding masks, and internal `SNDCTL_SUN_SEND_NUMBER`.

Dependencies:
- Includes `sys/types.h` and `sys/time.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The file is ABI-sensitive: struct sizes, ioctl numbers, and constant values are externally visible.
- Comments explicitly warn that many definitions are compatibility-only or obsolete.
- `SNDCTL_SUN_SEND_NUMBER` is duplicated with `sys/audioio.h` and marked internal.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_oss.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/g711.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/g711.h

This header contains precomputed G.711 conversion lookup tables for converting between linear PCM and A-law or u-law encodings. It is data-only: no functions or macros perform conversion logic beyond indexing the arrays.

Key contents:
- Defines conversion midpoint constants:
  - `G711_256_ARRAY_MIDPOINT`
  - `G711_ULAW_MIDPOINT`
  - `G711_ALAW_MIDPOINT`
- Decode tables:
  - `_8alaw2linear16[256]`
  - `_8alaw2linear8[256]`
  - `_8ulaw2linear16[256]`
  - `_8ulaw2linear8[256]`
- Encode tables:
  - `_13linear2alaw8[0x2000]`
  - `_14linear2ulaw8[0x4000]`

Dependencies:
- Uses fixed-width integer types such as `int16_t`, `int8_t`, and `uint8_t`, but does not include a type header itself.
- C++ guarded with `extern "C"`.

Research notes:
- The file explicitly says it has a very low commitment level and may change or be removed.
- The arrays are defined directly in the header, not declared `extern` or `static`; including this header from multiple translation units would create multiple definitions unless the build uses it in a controlled way.
- Most of the file is large generated/static table data rather than hand-written implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/g711.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audioio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audioio.h

This header defines the older Solaris audio device ioctl ABI and state structures. It covers stream configuration/state, device-wide state, encoding constants, port masks, feature masks, and classic `AUDIO_*` ioctls.

Key contents:
- `audio_prinfo_t`: per-playback or per-record stream state, including format, gain, port, buffer size, counters, pause/error/waiting/open/active flags.
- `audio_info_t`: combined playback/record state plus monitor gain, mute state, reference count, and hardware/software feature flags.
- Audio encoding constants including u-law, A-law, signed linear PCM, DVI ADPCM, and unsigned 8-bit linear.
- Gain, balance, channel count, precision, and input/output port constants.
- Feature masks `AUDIO_HWFEATURE_*` and `AUDIO_SWFEATURE_MIXER`.
- `AUDIO_INITINFO()` macro for initializing `audio_info_t` to ignored-field values.
- `audio_device_t` and ioctls `AUDIO_GETINFO`, `AUDIO_SETINFO`, `AUDIO_DRAIN`, `AUDIO_GETDEV`, `AUDIO_DIAG_LOOPBACK`.

Dependencies:
- Includes `sys/types.h`, `sys/types32.h`, `sys/time.h`, and `sys/ioccom.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is an externally visible device ABI; struct layout and ioctl encodings are compatibility-sensitive.
- `AUDIO_SETINFO` uses the `AUDIO_INITINFO` convention where initialized values are ignored.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audioio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/autoconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/autoconf.h

This is a kernel autoconfiguration/DDI support header. It defines driver-name bookkeeping state, driver flags, debug flags/macros, device tree audit/cache structures, and kernel-private autoconfiguration entry points.

Key contents:
- `struct devnames`: per-driver state parallel to the devops list, including name, flags, parent list, lock, instance list, global properties, minor permissions, and instance boundaries.
- `DN_*` flags for parsed config, busy/held/inactive/removed state, network/leaf/nexus-like classifications, no-autodetach, GLDv3, PHCI, SCSI sizing, etc.
- Kernel-only DDI debug flag masks and conditional debug macros.
- `devinfo_audit_t`, `devinfo_log_header_t`, and `struct di_cache`.
- Special devinfo path/cache constants such as `PSEUDO_PATH`, `CLONE_PATH`, `DI_CACHE_FILE`.
- Global kernel symbols and prototypes for driver/device tree setup, mbind handling, reconfiguration state, devinfo cache, forced attach, I/O retire, quiesce checks.

Dependencies:
- Includes DDI/devops/mutex/thread/OBP/hwconf/system headers.
- Most declarations are under `_KERNEL`.

Research notes:
- This is kernel-internal infrastructure, not a user ABI.
- Locking expectations are documented for `dn_lock` and devops reference count macros.
- Several interfaces are marked obsolete or compatibility-only.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/autoconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv.h

This header defines illumos auxiliary vector types and common auxiliary vector constants used around `exec`, runtime linker startup, brands, hardware capability reporting, and secure execution flags.

Key contents:
- `auxv_t` with `a_type` plus value/pointer/function union.
- `auxv32_t` under `_SYSCALL32`.
- Standard ELF auxiliary vector constants `AT_NULL` through `AT_ENTRY`.
- Commentary on PPC/Linux/LSB auxiliary vector values that illumos mostly does not emit.
- Sun extensions `AT_SUN_*` for uid/gid, runtime linker metadata, platform, hardware capabilities, icache flush, CPU/MMU names, exec path, aux flags, emulator/brand data, commpage, x86 FPU type/size.
- Kernel globals for `auxv_hwcap`, `auxv_hwcap_2`, `auxv_hwcap_3`, and 32-bit equivalents.
- User declaration for `getisax()`.
- `AF_SUN_*` flags for secure linker behavior, hardware-cap verification, and primary link-map behavior.
- Includes arch-specific `auxv_SPARC.h` and `auxv_386.h` depending on target macros or compiler architecture.

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is ABI-facing and shared by kernel, libc/runtime linker, and userland.
- The architecture-specific hardware capability namespaces are intentionally factored into separate headers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_386.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_386.h

This header defines x86-specific `AT_SUN_HWCAP`, `AT_SUN_HWCAP2`, `AT_SUN_HWCAP3`, and `AT_SUN_FPTYPE` bit values.

Key contents:
- `AV_386_*` HWCAP bits for baseline x87/i386 features through SSE, AVX, VMX, SVM, AES, PCLMULQDQ, POPCNT, etc.
- `FMT_AV_386` printf/bit-format string.
- `AV_386_2_*` HWCAP2 bits for F16C, RDRAND, BMI, FMA, AVX2, ADX, RDSEED, AVX-512 families, SHA, FSGSBASE, CLWB, VAES, GFNI, etc.
- `FMT_AV_386_2`.
- `AV_386_3_*` HWCAP3 bits for AVX512 VBMI2 and BF16.
- `FMT_AV_386_3`.
- `AT_386_FPINFO_*` values describing FPU save layout: none, FXSAVE, XSAVE, XSAVE_AMD.

Dependencies:
- Intended to be included by `sys/auxv.h`.
- C++ guarded with `extern "C"`.

Research notes:
- Bit assignments are externally meaningful to runtime linker/libc consumers.
- Comments note withdrawn bit positions and unsupported `xsavec`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_386.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_SPARC.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_SPARC.h

This header defines SPARC-specific hardware capability bit values for auxiliary vector reporting.

Key contents:
- `AV_SPARC_*` bits for legacy arithmetic capability, V8+/VIS/VIS2/VIS3, block init ASIs, FMA variants, HPC, random, transactions, crypto/hash instructions, Montgomery/multiple-precision multiply, CRC32C, pause, compare-and-branch, and cache sparing.
- `FMT_AV_SPARC` bit-format string.
- Obsolete compatibility aliases:
  - `AV_SPARC_HWMUL_32x32`
  - `AV_SPARC_HWDIV_32x32`
  - `AV_SPARC_HWFSMULD`

Dependencies:
- Intended to be included by `sys/auxv.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is an ABI support header for hardware capability consumers.
- Several values are explicitly legacy or obsolete aliases.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_SPARC.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/av/iec61883.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/av/iec61883.h

This header defines the IEC 61883 FireWire AV user/kernel ioctl interface. It covers asynchronous FCP requests, isochronous stream setup/transfer, plug control, node ROM text leaf access, ioctl numbers, and 32-bit compatibility structs.

Key contents:
- Interface version helpers and `IEC61883_V1_0`.
- `iec61883_arq_t` for asynchronous FCP command/response and bus reset events.
- `iec61883_isoch_init_t` for isochronous stream initialization, including packet/frame sizing, direction, bus speed, channel mask, DBS/FN/rate fields, timestamp mode, mmap offset, channel result, and error.
- Direction, bus speed, DV rate, timestamp, and error enums/constants.
- `iec61883_xfer_t`, `iec61883_recv_t`, and `iec61883_xmit_t` for frame transfer state.
- Plug init, plug register read, plug register CAS structs and enums.
- `iec61883_node_text_leaf_t` for ROM text leaf reads.
- Ioctl values `IEC61883_ISOCH_INIT` through `IEC61883_NODE_GET_TEXT_LEAF`.
- Kernel-only 32-bit compat structs for fields containing `off_t` or pointers.

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is a device ioctl ABI; struct layout and ioctl values are compatibility-sensitive.
- Contains spelling mistakes in comments only, not symbol names.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/av/iec61883.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avintr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avintr.h

This header defines kernel autovectored interrupt and soft interrupt data structures and registration/removal prototypes.

Key contents:
- Interrupt constants `MAXIPL`, `INT_IPL(x)`, and `AV_INT_SPURIOUS`.
- Interrupt function type `avfunc`.
- `struct autovec`: linked interrupt handler entry with vector, two args, tick counter pointer, priority, interrupt id, device info pointer, flags, and IPL chain link.
- `AV_PENTRY_*` pending/servicing/level-trigger flag masks.
- `struct av_head` for interrupt chain priority bounds.
- `struct softint` with pending software interrupt bitfield.
- Kernel-only globals and functions for adding/removing hardware, NMI, and software interrupt handlers, moving soft interrupt priority, updating args, waiting for visibility, and `softlevel1`.

Dependencies:
- Includes `sys/mutex.h`, `sys/dditypes.h`, and `sys/ddi_intr.h`.
- Kernel-only operational declarations are under `_KERNEL`.

Research notes:
- Internal kernel interrupt infrastructure; not a user ABI.
- Registration functions identify handlers by interrupt id, IPL, vector/function, and vector number depending on path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avintr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl.h

This header defines the public generic AVL tree API used in illumos. It describes the intrusive-node model, comparator contract, tree lifecycle, lookup/insertion/removal, traversal, update, swap, and teardown helpers.

Key contents:
- Comparator helpers `AVL_ISIGN`, `AVL_CMP`, and `AVL_PCMP`.
- Opaque/public typedefs `avl_tree_t`, `avl_node_t`, and `avl_index_t`.
- Direction constants `AVL_BEFORE` and `AVL_AFTER`.
- API prototypes:
  - `avl_create`, `avl_find`, `avl_insert`, `avl_insert_here`
  - `avl_first`, `avl_last`, `avl_nearest`
  - `avl_add`, `avl_remove`
  - `avl_update`, `avl_update_lt`, `avl_update_gt`
  - `avl_swap`, `avl_numnodes`, `avl_is_empty`
  - `avl_destroy_nodes`, `avl_destroy`
- Traversal macros `AVL_NEXT` and `AVL_PREV`.

Dependencies:
- Includes `sys/types.h` and private implementation header `sys/avl_impl.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The data structure is intrusive: caller-owned structs embed `avl_node_t`.
- Thread safety is explicitly caller-managed.
- Comparator must return exactly `-1`, `0`, or `+1`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl_impl.h

This private header defines the concrete AVL node/tree layout and low-level macros used by `avl.h` and the AVL implementation. It warns applications not to include it directly.

Key contents:
- `struct avl_node` layout differs by pointer width:
  - 32-bit: children, parent pointer, child index, and balance as separate fields.
  - 64-bit: two child pointers plus packed `avl_pcb` containing parent pointer, child index, and balance in low bits.
- Accessor macros for parent, child index, and balance:
  - `AVL_XPARENT`, `AVL_SETPARENT`
  - `AVL_XCHILD`, `AVL_SETCHILD`
  - `AVL_XBALANCE`, `AVL_SETBALANCE`
- Node/data conversion macros `AVL_NODE2DATA` and `AVL_DATA2NODE`.
- `avl_index_t` packing/extraction macros.
- `struct avl_tree` layout: root, comparator, node offset, node count, user struct size.
- Internal traversal function `avl_walk`.

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The 64-bit layout assumes pointer alignment leaves the low three bits available.
- Tree fields are ordered for `avl_find()` cache-line locality.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/beep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/beep.h

This kernel-only header defines the abstract system beeper API and state structures. It separates generic beeper scheduling/queuing from hardware-specific on/off/frequency callbacks.

Key contents:
- `beep_entry_t`: queued frequency/duration pair.
- Callback types:
  - `beep_on_func_t`
  - `beep_off_func_t`
  - `beep_freq_func_t`
- `beep_state_t`: callback private arg, mode enum, callback pointers, timeout id, mutex, circular queue indices/size, and queue pointer.
- `BEEP_QUEUE_SIZE`.
- Beep type enum: `BEEP_DEFAULT`, `BEEP_CONSOLE`, `BEEP_TYPE4`.
- `beep_params_t` with type, frequency, and duration.
- Kernel API prototypes for init/fini, on/off/frequency control, default beep, polled beep, tone creation, timeout handler, and busy check.

Dependencies:
- Includes `sys/mutex.h`.
- Almost all contents are under `_KERNEL`.
- C++ guarded with `extern "C"`.

Research notes:
- This is not a user-facing sound API; it is a kernel abstraction for console/system tones.
- Queue state is protected by `beep_state_t.mutex`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/beep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitext.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitext.h

This small header declares typed helper functions for extracting, setting, and deleting bit ranges from integer values. It is intended as a safer replacement for the `BITX` macro family with better error handling.

Key contents:
- Extraction functions:
  - `bitx8`, `bitx16`, `bitx32`, `bitx64`
- Bit range set functions:
  - `bitset8`, `bitset16`, `bitset32`, `bitset64`
- Delete helper:
  - `bitdel64`

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The header only declares functions; behavior and error handling live in implementation/manpage references such as `bitx64(9F)`, `bitdel64(9F)`, and `bitset64(9F)`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitext.h -->