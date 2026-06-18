# Research Group: subset-b-005993

This grouped report covers UAPI headers under `sources/distributed-fs/ceph-client/include/uapi/linux`. Each section is source-tree aligned and can be split into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sockios.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sockios.h

## Purpose
Defines Linux socket ioctl command numbers shared by userspace network tools and kernel socket/netdevice handlers. It is a stable UAPI registry for routing, interface, ARP/RARP, ethtool, MII, bonding, bridge, VLAN, timestamp, hardware timestamp, device-private, and protocol-private ioctl ranges.

## Important APIs, Types, and Constants
There are no functions or structs in this header. Important exported constants include `SIOCINQ`, `SIOCOUTQ`, `SIOCGSTAMP`, `SIOCGSTAMPNS`, `SIOCADDRT`, `SIOCDELRT`, `SIOCGIF*`, `SIOCSIF*`, `SIOCETHTOOL`, `SIOCGMIIPHY`, `SIOCGMIIREG`, `SIOCSMIIREG`, `SIOCSHWTSTAMP`, `SIOCGHWTSTAMP`, `SIOCDEVPRIVATE`, and `SIOCPROTOPRIVATE`. Timestamp ioctl selection depends on word size and libc `timeval`/`timespec` layout.

## Control Flow, State, and Persistence
The header has compile-time selection only. Runtime state is in socket and netdevice subsystems, not in this file. Ioctl numbers are persistent ABI; reusing obsolete holes or renumbering existing commands would break old tools.

## Dependencies and Integration Points
Depends on `<asm/bitsperlong.h>` and `<asm/sockios.h>`. Integrates with `ioctl(fd, request, arg)`, netdevice `ndo_do_ioctl`, bridge/bonding/VLAN handlers, hardware timestamp configuration in `linux/net_tstamp.h`, and TIPC's protocol-private additions.

## Risks and Test Signals
Risks are ABI collisions, wrong timestamp command on 32-bit/time64 builds, and userspace issuing private ioctls to the wrong device. Test by compiling representative 32-bit and 64-bit userspace, checking numeric ioctl stability, and exercising interface query/set operations through tools such as `ip`, `ethtool`, and timestamp socket tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sonet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sonet.h

## Purpose
Exports SONET/SDH physical-layer control ABI for ATM devices. It lets userspace retrieve or clear physical counters, inject diagnostic errors, configure framing, and read framing sense data.

## Important APIs, Types, and Constants
`struct sonet_stats` is a packed counter block generated from `__SONET_ITEMS`, covering section, line, and path BIP/FEBE counters, correctable and uncorrectable HCS errors, and transmitted/received cell counts. Ioctls include `SONET_GETSTAT`, `SONET_GETSTATZ`, `SONET_SETDIAG`, `SONET_CLRDIAG`, `SONET_GETDIAG`, `SONET_SETFRAMING`, `SONET_GETFRAMING`, and `SONET_GETFRSENSE`. Diagnostic bits include `SONET_INS_SBIP`, `SONET_INS_LBIP`, `SONET_INS_PBIP`, `SONET_INS_FRAME`, `SONET_INS_LOS`, `SONET_INS_LAIS`, `SONET_INS_PAIS`, and `SONET_INS_HCS`.

## Control Flow, State, and Persistence
The header defines ioctl payload shape only. Device drivers maintain counters, diagnostic injection state, and framing state. `SONET_GETSTATZ` is state-mutating because it zeros counters after returning them.

## Dependencies and Integration Points
Uses ATM ioctl numbering through `ATMIOC_PHYTYP`, expected from ATM headers included by consumers. Integrates with SONET-capable ATM PHY drivers and diagnostic tools.

## Risks and Test Signals
Packed layout must remain stable. Risks include counter truncation because fields are `int`, incorrect ATM ioctl base inclusion, and diagnostic bits left enabled. Test with header compilation beside ATM headers, ioctl number checks, and driver tests that verify get, get-and-zero, framing round trips, and each diagnostic bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sonypi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sonypi.h

## Purpose
Defines the legacy Sony Programmable I/O control userspace ABI for VAIO hotkey, jog dial, battery, brightness, Bluetooth, fan, and temperature events exposed by `/dev/sonypi`.

## Important APIs, Types, and Constants
The header exports event numbers from `SONYPI_EVENT_IGNORE` through `SONYPI_EVENT_VENDOR_PRESSED`, including jog dial, Fn key, capture, wireless, lid, memory stick, battery, volume, and media-button events. Ioctls include `SONYPI_IOCGBRT`, `SONYPI_IOCSBRT`, `SONYPI_IOCGBAT1CAP`, `SONYPI_IOCGBAT1REM`, `SONYPI_IOCGBAT2CAP`, `SONYPI_IOCGBAT2REM`, `SONYPI_IOCGBATFLAGS`, `SONYPI_IOCGBLUE`, `SONYPI_IOCSBLUE`, `SONYPI_IOCGFAN`, `SONYPI_IOCSFAN`, and `SONYPI_IOCGTEMP`. Battery flag bits are `SONYPI_BFLAGS_B1`, `SONYPI_BFLAGS_B2`, and `SONYPI_BFLAGS_AC`.

## Control Flow, State, and Persistence
Event delivery occurs through device reads. Ioctls query or mutate firmware-backed device state such as brightness and radio/fan state. Numeric event assignments are persistent ABI for user daemons.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl encoding provided by consumers. Integrates with the sonypi driver, laptop hotkey daemons, and older VAIO platform control tools.

## Risks and Test Signals
Risks include stale hardware-specific semantics, obsolete event values that must stay reserved, and privilege/safety concerns around fan or wireless control. Test by compiling old sonypi userspace, checking ioctl sizes for `__u8` and `__u16`, and using driver or mock tests for event decoding and state query/set round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sonypi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sound.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sound.h

## Purpose
Defines legacy OSS sound device minor numbers used to identify mixer, sequencer, MIDI, DSP, audio, synth, and obsolete sound nodes.

## Important APIs, Types, and Constants
The header has no structs or functions. Constants include `SND_DEV_CTL`, `SND_DEV_SEQ`, `SND_DEV_MIDIN`, `SND_DEV_DSP`, `SND_DEV_AUDIO`, `SND_DEV_DSP16`, `SND_DEV_UNUSED`, `SND_DEV_AWFM`, `SND_DEV_SEQ2`, `SND_DEV_SYNTH`, `SND_DEV_DMFM`, `SND_DEV_UNKNOWN11`, `SND_DEV_ADSP`, `SND_DEV_AMIDI`, and `SND_DEV_ADMMIDI`.

## Control Flow, State, and Persistence
There is no runtime logic. The minor-number assignments are persistent ABI and must stay compatible with old `/dev/sound` and OSS node naming.

## Dependencies and Integration Points
Includes `<linux/fs.h>` for device-number context. Integrates with OSS compatibility device registration and old userspace device-node creation scripts.

## Risks and Test Signals
Risks are accidental reuse of obsolete numbers and mismatch with `soundcard.h` ioctl expectations. Test by compiling OSS compatibility code and checking that generated device minors match historical nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/soundcard.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/soundcard.h

## Purpose
Exports the legacy Open Sound System 3.8 userspace ABI: sequencer, MIDI, DSP/audio PCM, mixer, synth patch loading, coprocessor, and convenience sequencer macro interfaces. This is a broad compatibility header for old OSS applications.

## Important APIs, Types, and Constants
Important versioning and ioctl helpers include `SOUND_VERSION`, `OPEN_SOUND_SYSTEM`, `_SIO`, `_SIOR`, `_SIOW`, and `_SIOWR`. Sequencer and timer ioctls include `SNDCTL_SEQ_*`, `SNDCTL_SYNTH_*`, and `SNDCTL_TMR_*`. PCM ioctls include `SNDCTL_DSP_RESET`, `SNDCTL_DSP_SYNC`, `SNDCTL_DSP_SPEED`, `SNDCTL_DSP_CHANNELS`, `SNDCTL_DSP_GETFMTS`, `SNDCTL_DSP_SETFMT`, `SNDCTL_DSP_GETOSPACE`, `SNDCTL_DSP_GETISPACE`, `SNDCTL_DSP_SETTRIGGER`, and capability/format constants such as `AFMT_*` and `PCM_ENABLE_*`. Mixer APIs include `SOUND_MIXER_*`, `MIXER_READ`, `MIXER_WRITE`, `mixer_info`, `mixer_record`, and `mixer_vol_table`. Key structs include `patch_info`, `sysex_info`, `sbi_instrument`, `synth_info`, `midi_info`, `audio_buf_info`, `count_info`, and `copr_msg`. The bottom of the file defines user convenience macros such as `SEQ_DEFINEBUF`, `SEQ_START_NOTE`, `SEQ_SYSEX`, `SEQ_SET_TEMPO`, and `SEQ_WRPATCH`.

## Control Flow, State, and Persistence
Most control flow is in applications using ioctls and sequencer macros. The macros write binary 4-byte and 8-byte events into `_seqbuf`, flushing with application-provided `seqbuf_dump()`. Kernel-side state includes device format, fragmenting, trigger state, mixer levels, patch memory, sequencer timers, and event queues. The header's structs and ioctl numbers are persistent ABI; many obsolete values remain reserved for compatibility.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>`, libc `<endian.h>` outside the kernel, and `<linux/patchkey.h>`. Integrates with OSS compatibility drivers, `/dev/dsp`, `/dev/audio`, `/dev/mixer`, `/dev/sequencer`, and old MIDI/synth applications.

## Risks and Test Signals
Risks are high because the header mixes ABI, C macros that perform unaligned casts, flexible trailing arrays, legacy endian decisions, and obsolete but still visible controls. Test by compiling representative OSS programs, checking ioctl numbers against historical values, validating 32/64-bit struct sizes, exercising PCM format/channel/rate negotiation, mixer read/write, sequencer event encoding, and ensuring deprecated values remain accepted or fail compatibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/soundcard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/spi/spi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/spi/spi.h

## Purpose
Defines userspace-visible SPI mode bit flags and mode combinations shared by spidev and userspace SPI tools.

## Important APIs, Types, and Constants
There are no structs or functions. Constants include `SPI_CPHA`, `SPI_CPOL`, `SPI_MODE_0` through `SPI_MODE_3`, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, `SPI_3WIRE`, `SPI_LOOP`, `SPI_NO_CS`, `SPI_READY`, dual/quad/octal transfer flags, `SPI_CS_WORD`, `SPI_3WIRE_HIZ`, `SPI_RX_CPHA_FLIP`, `SPI_MOSI_IDLE_LOW`, `SPI_MOSI_IDLE_HIGH`, and `SPI_MODE_USER_MASK`.

## Control Flow, State, and Persistence
The header is declarative. SPI device state is set by ioctl users such as `spidev.h`. `SPI_MODE_USER_MASK` bounds userspace-accepted bits and must not overlap kernel-private mode bits.

## Dependencies and Integration Points
Depends on `<linux/const.h>` for `_BITUL`. Used by `spidev.h`, SPI test tools, and libraries that construct mode words for `SPI_IOC_WR_MODE` and `SPI_IOC_WR_MODE32`.

## Risks and Test Signals
Risks include adding a bit without extending `SPI_MODE_USER_MASK`, overlap with kernel-only mode bits, and old 8-bit mode ioctls truncating newer flags. Test via compile-time mask assertions, spidev mode32 round trips, and hardware or loopback transfers for each line-width flag supported by a controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/spi/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/spi/spidev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/spi/spidev.h

## Purpose
Defines the `/dev/spidev*` ioctl ABI used by userspace to configure an SPI device and submit synchronous transfer batches.

## Important APIs, Types, and Constants
`struct spi_ioc_transfer` describes one transfer with userspace `tx_buf` and `rx_buf` pointers, `len`, `speed_hz`, `delay_usecs`, `bits_per_word`, `cs_change`, `tx_nbits`, `rx_nbits`, `word_delay_usecs`, and padding. `SPI_IOC_MESSAGE(N)` submits an array of transfers. Configuration ioctls include `SPI_IOC_RD_MODE`, `SPI_IOC_WR_MODE`, `SPI_IOC_RD_LSB_FIRST`, `SPI_IOC_WR_LSB_FIRST`, `SPI_IOC_RD_BITS_PER_WORD`, `SPI_IOC_WR_BITS_PER_WORD`, `SPI_IOC_RD_MAX_SPEED_HZ`, `SPI_IOC_WR_MAX_SPEED_HZ`, `SPI_IOC_RD_MODE32`, and `SPI_IOC_WR_MODE32`.

## Control Flow, State, and Persistence
Userspace configures defaults, then submits transfer arrays that execute together like `spi_sync()`. Transfer fields can temporarily override device speed and word size. Device defaults persist for the file/device until changed by ioctl.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/ioctl.h>`, and `<linux/spi/spi.h>`. Integrates with the spidev character driver and SPI controller drivers.

## Risks and Test Signals
The struct layout is explicitly 32/64-bit stable and must be zero-initialized for future compatibility. Risks include `_IOC_SIZEBITS` overflow via large `N`, invalid user pointers, unsupported `word_delay_usecs` silently ignored, and use of 8-bit mode ioctls for mode bits above bit 7. Test with ABI size checks, loopback transfers, invalid pointer handling, `SPI_IOC_MESSAGE(0/large)`, and mode32 round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/spi/spidev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/stat.h

## Purpose
Provides file type, permission, and `statx()` UAPI definitions. It lets userspace request and interpret extended file metadata such as birth time, mount IDs, direct-I/O alignment, subvolume ID, and atomic write properties.

## Important APIs, Types, and Constants
Classic mode constants include `S_IFMT`, `S_IFSOCK`, `S_IFLNK`, `S_IFREG`, `S_IFBLK`, `S_IFDIR`, `S_IFCHR`, `S_IFIFO`, `S_ISUID`, `S_ISGID`, `S_ISVTX`, `S_IS*()` predicates, and permission bits. `struct statx_timestamp` and `struct statx` define the `statx()` result layout. Request/result masks include `STATX_TYPE`, `STATX_MODE`, `STATX_BASIC_STATS`, `STATX_BTIME`, `STATX_MNT_ID`, `STATX_DIOALIGN`, `STATX_MNT_ID_UNIQUE`, `STATX_SUBVOL`, `STATX_WRITE_ATOMIC`, and `STATX_DIO_READ_ALIGN`. Attribute flags include compressed, immutable, append-only, encrypted, automount, mount-root, verity, DAX, and atomic-write support.

## Control Flow, State, and Persistence
The file is ABI structure only. Kernel filesystems fill `struct statx` based on requested masks and available metadata. Unsupported fields are cleared or fabricated for compatibility.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `statx(2)`, VFS, distributed filesystems such as Ceph, libc wrappers, backup tools, and file managers.

## Risks and Test Signals
Risks include struct layout drift, mask/attribute confusion, reserved bit misuse, and filesystem-specific partial support. Test with compile-time size/offset checks, `statx()` mask combinations, filesystem matrix tests, direct-I/O alignment validation, and 32-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stddef.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/stddef.h

## Purpose
Exports small compiler/layout helper macros usable by UAPI headers, especially for anonymous struct groups and flexible arrays embedded in unions.

## Important APIs, Types, and Constants
Defines `__always_inline` fallback, `__struct_group_tag`, `__struct_group(TAG, NAME, ATTRS, MEMBERS...)`, `__DECLARE_FLEX_ARRAY(TYPE, NAME)`, no-op counted-by annotations (`__counted_by`, `__counted_by_le`, `__counted_by_be`, `__counted_by_ptr`), and `__kernel_nonstring`.

## Control Flow, State, and Persistence
No runtime state. These macros influence C/C++ compilation and ABI layout. The C++ path for `__DECLARE_FLEX_ARRAY` uses a zero-length array because C++ does not treat empty structs like C.

## Dependencies and Integration Points
May include `<linux/compiler_types.h>` in kernel builds. Used by many UAPI structs, including headers with flexible arrays such as TCMU and packet editing.

## Risks and Test Signals
Risks are compiler incompatibility, C/C++ layout differences, and annotations not being available to userspace compilers. Test by compiling UAPI headers as C and C++, checking offsets for structs using `__struct_group`, and building with sparse/clang/gcc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/stm.h

## Purpose
Defines userspace ioctls for the System Trace Module class, used to allocate STP master/channel ranges and set STM options.

## Important APIs, Types, and Constants
`STP_MASTER_MAX` and `STP_CHANNEL_MAX` cap values. `struct stp_policy_id` carries variable-length policy identity data with total `size`, assigned `master`, assigned `channel`, requested/returned `width`, reserved fields, and flexible `id[]`. Ioctls are `STP_POLICY_ID_SET`, `STP_POLICY_ID_GET`, and `STP_SET_OPTIONS`.

## Control Flow, State, and Persistence
Userspace passes an ID and desired channel width; the kernel fills assignment fields. Policy assignment and options live in STM class/device state, not in the header.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl definitions. Integrates with STM character devices and tracing infrastructure based on MIPI STPv2.

## Risks and Test Signals
Risks include incorrect `size` calculation for `id[]`, uninitialized reserved fields, and invalid channel width. Test variable-length ioctl handling, get-after-set behavior, maximum master/channel boundary values, and 32/64-bit struct layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/stm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/string.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/string.h

## Purpose
Provides a UAPI-safe wrapper for string definitions. Outside the kernel it includes libc `<string.h>` and intentionally avoids exposing kernel `strings.h`-style helpers to userspace.

## Important APIs, Types, and Constants
No custom APIs are defined. The only exported behavior is conditional inclusion of standard C string declarations for non-kernel builds.

## Control Flow, State, and Persistence
No runtime behavior or state. This header affects include resolution and prevents accidental use of kernel-only string helpers.

## Dependencies and Integration Points
Depends on libc `<string.h>` outside `__KERNEL__`. Used by UAPI headers that need `memcpy`, `memset`, or string declarations in inline helpers, for example TIPC configuration helpers.

## Risks and Test Signals
Risks are include-order surprises and exposing nonportable kernel helpers to userspace. Test by compiling userspace consumers that include `<linux/string.h>` before and after libc headers and by building kernel-side consumers with `__KERNEL__`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sunrpc/debug.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sunrpc/debug.h

## Purpose
Defines SUNRPC debug flag bits and binary sysctl IDs for RPC, NFS, NFSD, and lockd debug control.

## Important APIs, Types, and Constants
Debug masks include `RPCDBG_XPRT`, `RPCDBG_CALL`, `RPCDBG_DEBUG`, `RPCDBG_NFS`, `RPCDBG_AUTH`, `RPCDBG_BIND`, `RPCDBG_SCHED`, `RPCDBG_TRANS`, `RPCDBG_SVCXPRT`, `RPCDBG_SVCDSP`, `RPCDBG_MISC`, `RPCDBG_CACHE`, and `RPCDBG_ALL`. Sysctl IDs include `CTL_RPCDEBUG`, `CTL_NFSDEBUG`, `CTL_NFSDDEBUG`, `CTL_NLMDEBUG`, `CTL_SLOTTABLE_UDP`, `CTL_SLOTTABLE_TCP`, `CTL_MIN_RESVPORT`, and `CTL_MAX_RESVPORT`.

## Control Flow, State, and Persistence
The header defines values only. Runtime debug state is stored in dynamically registered SUNRPC sysctl tables and read or changed by sysctl/procfs interfaces.

## Dependencies and Integration Points
Integrates with `CTL_SUNRPC` from `sysctl.h`, SUNRPC module sysctl registration, NFS tooling, and kernel debug logging.

## Risks and Test Signals
Risks include binary sysctl deprecation, flags being interpreted differently across modules, and noisy debug output. Test by toggling each debug mask through supported proc/sysctl paths, checking no ABI renumbering, and validating NFS/SUNRPC logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sunrpc/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/cdev.h

## Purpose
Defines the `/dev/surface/aggregator` userspace ABI for direct Surface System Aggregator Module EC requests, notifier registration, event enable/disable, and event reads. It is mainly for debugging and development.

## Important APIs, Types, and Constants
`enum ssam_cdev_request_flags` defines `SSAM_CDEV_REQUEST_HAS_RESPONSE` and `SSAM_CDEV_REQUEST_UNSEQUENCED`. `struct ssam_cdev_request` carries target category/id, command id, instance id, flags, output status, user payload pointer/length, and response pointer/length. `struct ssam_cdev_notifier_desc` registers event categories with priority. `struct ssam_cdev_event_desc` describes registry commands and event IDs. `struct ssam_cdev_event` is the variable-length event read format. Ioctls are `SSAM_CDEV_REQUEST`, `SSAM_CDEV_NOTIF_REGISTER`, `SSAM_CDEV_NOTIF_UNREGISTER`, `SSAM_CDEV_EVENT_ENABLE`, and `SSAM_CDEV_EVENT_DISABLE`.

## Control Flow, State, and Persistence
Userspace submits request ioctls and may register notifiers, enable events, then read event records. Kernel state includes notifier registrations, event enablement, EC transaction queues, and response buffers.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with Surface aggregator core, EC transport, and misc-device userspace tooling.

## Risks and Test Signals
Risks include mutually exclusive response/unsequenced flags, packed pointer fields, invalid user buffers, and privileged EC access. Test invalid flag combinations, short buffers, event lifecycle register-enable-read-disable, and 32-bit compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/dtx.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/dtx.h

## Purpose
Defines the `/dev/surface/dtx` userspace ABI for Surface Book clipboard/base detachment control and event reporting.

## Important APIs, Types, and Constants
Status category macros include `SDTX_STATUS`, `SDTX_ERR_RT`, `SDTX_ERR_HW`, `SDTX_UNKNOWN`, `SDTX_CATEGORY`, and `SDTX_SUCCESS`. Values cover latch open/closed, base detached/attached, runtime errors such as infeasible or timed-out detach, and hardware errors. Base type macros distinguish HID and SSH bases. `enum sdtx_device_mode` describes tablet, laptop, and studio modes. `struct sdtx_event` is a variable-length read event, `enum sdtx_event_code` names request/cancel/base/latch/mode events, and `struct sdtx_base_info` returns connection state and base id. Ioctls enable events, lock/unlock/request/confirm/heartbeat/cancel latch operations, and query base info, device mode, and latch status.

## Control Flow, State, and Persistence
Userspace enables events, reads event stream records, and drives detach through request, confirm, heartbeat, and cancel ioctls. Kernel/device state includes latch state, base connection, detach feasibility, and current mode.

## Dependencies and Integration Points
Depends on ioctl and fixed-width types. Integrates with Surface DTX driver, SSAM/EC communication, and desktop detach policy agents.

## Risks and Test Signals
Risks include wrong sequencing of latch operations, unknown future event codes, critical hardware error handling, and packed variable-length event parsing. Test successful and failed detach state machines, event enable/disable, unknown event skipping, base info queries, and privilege checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/surface_aggregator/dtx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/suspend_ioctls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/suspend_ioctls.h

## Purpose
Defines ioctl ABI for the snapshot/suspend device used by hibernation and suspend-to-RAM userspace helpers.

## Important APIs, Types, and Constants
`struct resume_swap_area` is a packed structure carrying resume swap `offset` and device id `dev` for `SNAPSHOT_SET_SWAP_AREA`. Ioctls include `SNAPSHOT_FREEZE`, `SNAPSHOT_UNFREEZE`, `SNAPSHOT_ATOMIC_RESTORE`, `SNAPSHOT_FREE`, `SNAPSHOT_FREE_SWAP_PAGES`, `SNAPSHOT_S2RAM`, `SNAPSHOT_SET_SWAP_AREA`, `SNAPSHOT_GET_IMAGE_SIZE`, `SNAPSHOT_PLATFORM_SUPPORT`, `SNAPSHOT_POWER_OFF`, `SNAPSHOT_CREATE_IMAGE`, `SNAPSHOT_PREF_IMAGE_SIZE`, `SNAPSHOT_AVAIL_SWAP_SIZE`, and `SNAPSHOT_ALLOC_SWAP_PAGE`.

## Control Flow, State, and Persistence
Userspace coordinates freezing, image creation, swap allocation, restore, and platform power transitions via ioctl sequence. Kernel state includes frozen task state, hibernation image pages, swap allocations, and platform support flags.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl macros. Integrates with `/dev/snapshot`, swsusp, power management, and initramfs resume tooling.

## Risks and Test Signals
Risks are unsafe ioctl order, packed `resume_swap_area` layout, device-number mismatch, and data loss if swap/image accounting is wrong. Test hibernation create/resume paths, invalid order failures, 32/64-bit structure layout, low-swap behavior, and platform support detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/suspend_ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/swab.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/swab.h

## Purpose
Provides byte-swap and halfword-swap helpers for UAPI and userspace code, with constant-folding, compiler builtins, and architecture-specific overrides.

## Important APIs, Types, and Constants
Constant macros include `___constant_swab16`, `___constant_swab32`, `___constant_swab64`, `___constant_swahw32`, and `___constant_swahb32`. Inline helpers include `__fswab16`, `__fswab32`, `__fswab64`, `__fswahw32`, and `__fswahb32`. Public macros/functions include `__swab16`, `__swab32`, `__swab64`, `__swab`, `__swahw32`, `__swahb32`, pointer forms `__swab16p`, `__swab32p`, `__swab64p`, `__swahw32p`, `__swahb32p`, and in-place forms `__swab16s`, `__swab32s`, `__swab64s`, `__swahw32s`, `__swahb32s`.

## Control Flow, State, and Persistence
The helpers are pure value transforms with no persistent state. Compile-time paths prefer compiler builtins or `__builtin_constant_p`; runtime paths use arch helpers or portable shifts.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/stddef.h>`, `<asm/bitsperlong.h>`, and `<asm/swab.h>`. Used by endian conversion headers and wire-format parsers.

## Risks and Test Signals
Risks include signedness mistakes, unaligned pointer use by callers, wrong `__BITS_PER_LONG` path, and architecture override mismatch. Test constant and runtime values for 16/32/64-bit cases, pointer and in-place forms, 32-bit/64-bit builds, and compiler-builtin and no-builtin configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/switchtec_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/switchtec_ioctl.h

## Purpose
Defines the Microsemi/Microchip Switchtec PCIe switch ioctl ABI for flash partition information, event summaries/control, and PFF-to-port mapping.

## Important APIs, Types, and Constants
Partition IDs cover config, image, NVLOG, vendor, BL2, map, and key partitions. `struct switchtec_ioctl_flash_info`, `switchtec_ioctl_flash_part_info`, `switchtec_ioctl_event_summary_legacy`, `switchtec_ioctl_event_summary`, `switchtec_ioctl_event_ctl`, and `switchtec_ioctl_pff_port` are ioctl payloads. Event IDs range through stack, PPU, ISP, firmware, MRPC, GPIO, DPC, hotplug, threshold, power, link, GFMS, intercomm, and UEC events. Event flags support clear, enable/disable polling/log/CLI/fatal. Ioctls include `SWITCHTEC_IOCTL_FLASH_INFO`, `SWITCHTEC_IOCTL_FLASH_PART_INFO`, `SWITCHTEC_IOCTL_EVENT_SUMMARY`, `SWITCHTEC_IOCTL_EVENT_SUMMARY_LEGACY`, `SWITCHTEC_IOCTL_EVENT_CTL`, `SWITCHTEC_IOCTL_PFF_TO_PORT`, and `SWITCHTEC_IOCTL_PORT_TO_PFF`.

## Control Flow, State, and Persistence
Userspace queries flash layout, maps ports, reads event bitmaps, and controls per-event behavior. Device firmware and driver maintain event counts, occurrence data, flash partitions, and PFF mappings.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl encoding. Integrates with the Switchtec PCI driver and vendor management tools.

## Risks and Test Signals
Risks include legacy and current event-summary sharing the same ioctl number with different struct sizes, invalid partition indices, and accidental clearing of diagnostics. Test size-dispatch compatibility, Gen3/Gen4 partition counts, event flag validation, all-event/local-part sentinel indices, and PFF mapping round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/switchtec_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sync_file.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sync_file.h

## Purpose
Defines the sync_file fence ioctl ABI used by graphics, DMA, and display stacks to merge fences, query fence details, and set scheduling deadline hints.

## Important APIs, Types, and Constants
`struct sync_merge_data` names and merges the calling fence fd with `fd2`, returning a new `fence` fd. `struct sync_fence_info` reports timeline name, driver name, status, flags, and timestamp. `struct sync_file_info` queries a sync file and optionally points to an array of fence info records. `struct sync_set_deadline` carries an absolute `CLOCK_MONOTONIC` deadline. Ioctls are `SYNC_IOC_MERGE`, `SYNC_IOC_FILE_INFO`, and `SYNC_IOC_SET_DEADLINE`; opcode numbers 0-2 are intentionally burned.

## Control Flow, State, and Persistence
Userspace performs a two-pass file-info query when needed: first with `num_fences = 0`, then with a populated user buffer. Fence status evolves in kernel DMA fence state. Deadline hints influence scheduling but are not durable.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with DRM, Android sync framework compatibility, dma-fence, and compositor/display userspace.

## Risks and Test Signals
Risks include invalid user pointers in `sync_fence_info`, stale status races, unsupported deadline semantics, and old API ioctl number confusion. Test merge semantics, two-pass info query, active/signaled/error status transitions, deadline validation, and fd lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sync_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/synclink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/synclink.h

## Purpose
Exports the SyncLink multiprotocol serial adapter private ABI for configuring asynchronous, HDLC, monosync, bisync, raw, base-clock, and extended sync modes.

## Important APIs, Types, and Constants
Defines generic bit constants, frame and buffer limits, async parity modes, HDLC flags, CRC modes, idle modes, encodings, preamble settings, device IDs, diagnostics, serial signal bits, and event flags. `MGSL_PARAMS` carries common, HDLC, and async configuration. `struct mgsl_icount` reports modem, TX/RX, and error counters. `struct gpio_desc` controls GPIO state, direction, and wait masks. Private ioctls include `MGSL_IOCSPARAMS`, `MGSL_IOCGPARAMS`, `MGSL_IOCSTXIDLE`, `MGSL_IOCGTXIDLE`, `MGSL_IOCTXENABLE`, `MGSL_IOCRXENABLE`, `MGSL_IOCTXABORT`, `MGSL_IOCGSTATS`, `MGSL_IOCWAITEVENT`, GPIO controls, and XSYNC/XCTRL controls.

## Control Flow, State, and Persistence
Userspace configures line mode and protocol parameters, enables TX/RX, waits for modem/GPIO events, and reads statistics. Driver state includes mode, clocks, line interface, GPIO direction/state, counters, and transmit/receive queues.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl macros. Integrates with Microgate SyncLink serial drivers and specialized WAN/industrial serial applications.

## Risks and Test Signals
Risks include `unsigned long` ABI differences across 32/64-bit builds, private ioctl compatibility, unsafe mode transitions while active, and event wait races. Test compat ioctls, every mode transition, HDLC CRC/encoding combinations, GPIO wait behavior, counter rollover, and invalid interface values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/synclink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sysctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sysctl.h

## Purpose
Defines the legacy binary `sysctl()` UAPI: `struct __sysctl_args` and numeric MIB names for kernel, VM, network, filesystem, device, ABI, and architecture-specific controls. The header warns that numbering is exported and must not be changed.

## Important APIs, Types, and Constants
`CTL_MAXNAME` limits path components. `struct __sysctl_args` contains user pointers for name vector, old value/length, new value/length, and unused padding. Top-level enums include `CTL_KERN`, `CTL_VM`, `CTL_NET`, `CTL_FS`, `CTL_DEBUG`, `CTL_DEV`, `CTL_ABI`, `CTL_CPU`, `CTL_SUNRPC`, and others. Large enum groups define kernel settings (`KERN_*`), VM settings (`VM_*`), network families and protocol controls (`NET_*`), filesystem controls (`FS_*`), device controls (`DEV_*`), and ABI controls.

## Control Flow, State, and Persistence
Userspace passes an integer path and optional old/new buffers to the binary syscall. Kernel sysctl tables resolve the path, copy data out/in, and may mutate runtime kernel state. The numeric path values are persistent ABI, even for obsolete or removed entries.

## Dependencies and Integration Points
Depends on `<linux/const.h>`, `<linux/types.h>`, and `<linux/compiler.h>`. Integrates with the deprecated `sysctl()` syscall, procfs `/proc/sys`, networking sysctls, SUNRPC debug, filesystem tunables, and legacy tools such as old `strace` builds.

## Risks and Test Signals
Risks are severe ABI breakage from renumbering, stale entries that no longer correspond to active procfs files, pointer-size compatibility through `__user` members, and security-sensitive write controls. Test by compiling old sysctl callers, checking numeric stability, verifying unsupported paths fail compatibly, and comparing binary/sysctl-proc behavior where still implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sysinfo.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sysinfo.h

## Purpose
Defines `struct sysinfo`, the userspace result shape for system uptime, load averages, memory, swap, process count, high memory, and memory unit scale.

## Important APIs, Types, and Constants
`SI_LOAD_SHIFT` gives the fixed-point load average shift. `struct sysinfo` fields include `uptime`, three `loads`, RAM and swap totals/free counts, shared and buffer memory, `procs`, m68k padding, high memory totals/free counts, `mem_unit`, and legacy libc5 padding.

## Control Flow, State, and Persistence
No code is present. Kernel fills this struct for `sysinfo(2)`. Values are a snapshot and not persistent; the layout and padding are ABI.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `sysinfo(2)`, libc, monitoring tools, and memory-reporting utilities.

## Risks and Test Signals
Risks include load fixed-point misinterpretation, overflow if callers ignore `mem_unit`, and layout differences from `__kernel_long_t`. Test 32/64-bit struct size, load conversion, large-memory systems, and libc wrapper compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sysinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/target_core_user.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/target_core_user.h

## Purpose
Defines the TCMU userspace target ABI for SCSI command processing through an mmaped UIO region, command ring, mailbox, and generic netlink events.

## Important APIs, Types, and Constants
`TCMU_VERSION`, `TCMU_MAILBOX_VERSION`, and mailbox capability flags describe supported features. `struct tcmu_mailbox` carries command ring offset/size, `cmd_head`, and user-updated `cmd_tail`. `enum tcmu_opcode` names `TCMU_OP_PAD`, `TCMU_OP_CMD`, and `TCMU_OP_TMR`. `struct tcmu_cmd_entry_hdr` packs length and opcode in `len_op` and carries command IDs and flags. Inline helpers get/set op and length. `struct tcmu_cmd_entry` contains request CDB/data offsets or response status/read length/sense. `struct tcmu_tmr_entry` carries task management requests. Generic netlink command and attribute enums report device add/remove/reconfig and features.

## Control Flow, State, and Persistence
Kernel writes ring entries and advances `cmd_head`, then notifies userspace through UIO. Userspace processes entries, writes response fields, and advances `cmd_tail`; optional capabilities allow out-of-order completion, read length, TMR, and buffer retention. Device configuration is delivered over generic netlink.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/uio.h>`, and `__DECLARE_FLEX_ARRAY`. Integrates with LIO target core, UIO mmap/interrupts, SCSI userspace backstores, and generic netlink management.

## Risks and Test Signals
Risks include ring wrap/pad handling, memory ordering, packed flexible layouts, length/op bit corruption, and userspace failing to advance `cmd_tail`. Test ring wrap, PAD entries, command and TMR processing, sense buffer propagation, feature negotiation, and concurrent reset/removal events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/target_core_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/taskstats.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/taskstats.h

## Purpose
Defines the generic netlink ABI for exporting per-task and per-thread-group accounting, delay accounting, I/O accounting, memory high-water marks, context switches, executable identity, and delay extrema/timestamps.

## Important APIs, Types, and Constants
`TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` contains versioned fields that must only grow at the end: exit code, accounting flags, CPU/block/swap/freepage/thrashing/compact/write-protect/IRQ delay counts and totals, basic accounting, memory and I/O usage, context switches, scaled CPU times, 64-bit begin time, thread group fields, executable device/inode, delay min/max values, and max timestamps as `struct __kernel_timespec`. Netlink enums define commands (`TASKSTATS_CMD_GET`, `TASKSTATS_CMD_NEW`), types (`TASKSTATS_TYPE_PID`, `TASKSTATS_TYPE_TGID`, `TASKSTATS_TYPE_STATS`, aggregate forms), command attributes, family name `TASKSTATS`, and version.

## Control Flow, State, and Persistence
Userspace requests stats for PID/TGID or registers CPU masks for exit events. Kernel snapshots task accounting state into this append-only struct. Values are per-task runtime state and may wrap as documented.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/time_types.h>`. Integrates with delay accounting, BSD process accounting concepts, generic netlink, and monitoring/accounting tools.

## Risks and Test Signals
Risks include struct version/offset drift, non-atomic delay counter reads, overflow, and differing availability when delay accounting is disabled. Test netlink request/response parsing, old-version userspace prefix compatibility, 64-bit alignment, disabled delay accounting, process exit events, and cputime/memory/I/O sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/taskstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_bpf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_bpf.h

## Purpose
Defines the traffic-control action ABI for attaching BPF programs as packet actions.

## Important APIs, Types, and Constants
`struct tc_act_bpf` embeds `tc_gen`. Netlink attributes include timing, parameters, classic BPF op length/ops, BPF fd, name, pad, tag, and id through `TCA_ACT_BPF_*`.

## Control Flow, State, and Persistence
Userspace sends netlink action attributes to create/update a TC action. Kernel stores generic action state and references a BPF program by fd/id/name/tag.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with `tc`, rtnetlink, classifier/action core, and eBPF program management.

## Risks and Test Signals
Risks include fd lifetime/reference mistakes, classic-vs-eBPF attribute confusion, and missing tag/id validation. Test `tc action bpf` add/show/delete, fd-based load, dump attributes, and program execution counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_connmark.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_connmark.h

## Purpose
Defines the TC connmark action ABI, which restores or uses conntrack marks in packet classification/action pipelines.

## Important APIs, Types, and Constants
`struct tc_connmark` embeds `tc_gen` and a `__u16 zone`. Attributes are `TCA_CONNMARK_PARMS`, `TCA_CONNMARK_TM`, and padding.

## Control Flow, State, and Persistence
Userspace configures the action via rtnetlink. Runtime state is in TC action instances and conntrack zone/mark state; the header itself is declarative.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with netfilter conntrack and `tc` action configuration.

## Risks and Test Signals
Risks include zone mismatch with conntrack rules and missing conntrack state. Test add/dump/delete, zone-specific packets, and mark restoration with conntrack enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_connmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_csum.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_csum.h

## Purpose
Defines the TC checksum update action ABI for recalculating protocol checksums after packet edits.

## Important APIs, Types, and Constants
`struct tc_csum` embeds `tc_gen` and `update_flags`. Flags include IPv4 header, ICMP, IGMP, TCP, UDP, UDPLite, and SCTP checksum updates. Attributes are `TCA_CSUM_PARMS`, `TCA_CSUM_TM`, and padding.

## Control Flow, State, and Persistence
Userspace configures which checksums to update. Kernel action execution examines packets and recalculates selected checksum fields. Persistent state is only the action's configured flags and generic counters.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Typically follows pedit, NAT, MPLS, VLAN, or other packet mutation actions in `tc` pipelines.

## Risks and Test Signals
Risks include stale checksums after edits, incompatible protocol flags, and fragmented/nonlinear skb handling. Test per-protocol checksum correction, bad flag combinations, action dump, and packet capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_csum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ct.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ct.h

## Purpose
Defines the TC conntrack action ABI for committing, clearing, forcing, and NATing connection-tracked packet state.

## Important APIs, Types, and Constants
`struct tc_ct` embeds `tc_gen`. Attributes include action flags, zone, mark/mask, labels/mask, NAT IPv4/IPv6 address ranges, NAT port ranges, helper name/family/proto, and padding. Action bits include `TCA_CT_ACT_COMMIT`, `TCA_CT_ACT_FORCE`, `TCA_CT_ACT_CLEAR`, `TCA_CT_ACT_NAT`, `TCA_CT_ACT_NAT_SRC`, and `TCA_CT_ACT_NAT_DST`.

## Control Flow, State, and Persistence
Userspace configures attributes through rtnetlink. Runtime action lookup or creates conntrack entries, applies metadata and NAT, or clears state. Conntrack table entries persist according to netfilter lifetimes.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with netfilter conntrack, NAT, helpers, OVS/TC offload paths, and `tc`.

## Risks and Test Signals
Risks include invalid NAT ranges, helper misuse, label width mismatch, offload incompatibility, and conntrack state leaks. Test commit/clear/NAT paths, zone isolation, mark/label masks, helper attributes, action dumps, and hardware-offload rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ctinfo.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ctinfo.h

## Purpose
Defines the TC ctinfo action ABI for copying conntrack metadata into packet DSCP or skb mark fields and reporting action statistics.

## Important APIs, Types, and Constants
`struct tc_ctinfo` embeds `tc_gen`. Attributes include action, zone, DSCP mask, DSCP state mask, cpmark mask, and statistics for DSCP set/error and cpmark set.

## Control Flow, State, and Persistence
Userspace configures masks and action mode. Kernel reads conntrack state during packet processing and conditionally updates packet DSCP or mark. Action counters persist with the action instance.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with conntrack, QoS classification, and `tc` filter/action chains.

## Risks and Test Signals
Risks include mask mistakes that corrupt DSCP bits, missing conntrack entries, and stats drift. Test DSCP/cpmark behavior with known conntrack marks, zone handling, and netlink dump of stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ctinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_defact.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_defact.h

## Purpose
Defines the generic/default TC action ABI used to carry opaque action data with standard `tc_gen` parameters.

## Important APIs, Types, and Constants
`struct tc_defact` embeds `tc_gen`. Attributes are `TCA_DEF_TM`, `TCA_DEF_PARMS`, `TCA_DEF_DATA`, and `TCA_DEF_PAD`.

## Control Flow, State, and Persistence
Userspace configures generic action parameters and optional data. Kernel action implementation interprets the data; generic counters and timing state persist per action instance.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC action core and `tc` netlink messages.

## Risks and Test Signals
Risks include opaque data versioning and mismatched userspace/kernel interpretation. Test action creation, dump round trip, unknown data rejection, and generic action counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_defact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gact.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gact.h

## Purpose
Defines the generic TC action ABI for pass/drop/reclassify-style actions, including probabilistic behavior.

## Important APIs, Types, and Constants
`struct tc_gact` embeds `tc_gen`. `struct tc_gact_p` configures probability type (`PGACT_NONE`, `PGACT_NETRAND`, `PGACT_DETERM`), value, and alternate action. Attributes include timing, parameters, probability, and padding.

## Control Flow, State, and Persistence
Userspace configures a generic action and optional probability policy. Runtime action selects the configured action, possibly using random or deterministic probability logic. Counters persist in action state.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC classifier/action chains.

## Risks and Test Signals
Risks include probabilistic behavior being difficult to validate and ptype/pval interpretation mismatch. Test deterministic and random probability modes statistically, action dumps, and counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gate.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gate.h

## Purpose
Defines the TC gate action ABI for time-aware gate schedules, commonly used with TSN-like traffic shaping.

## Important APIs, Types, and Constants
`struct tc_gate` embeds `tc_gen`. Nested entry attributes include index, gate state, interval, internal priority value, and max octets. Action attributes include priority, entry list, base time, cycle time, cycle time extension, flags, and clock id.

## Control Flow, State, and Persistence
Userspace installs a schedule. Runtime packet handling checks the selected clock and current schedule entry to allow or gate traffic. Schedule state persists in the action instance.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, qdisc scheduling, and time-aware networking features.

## Risks and Test Signals
Risks include wrong clock id, schedule wrap errors, invalid intervals, and hardware offload mismatch. Test schedule parsing, base-time alignment, cycle rollover, max-octets limits, and dump/offload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ife.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ife.h

## Purpose
Defines the TC IFE action ABI for encoding or decoding Inter-FE metadata around packets.

## Important APIs, Types, and Constants
`IFE_ENCODE` and `IFE_DECODE` select direction. `struct tc_ife` embeds `tc_gen` and `flags`. Attributes include parameters, timing, destination/source MAC, ethertype, metadata list, and padding.

## Control Flow, State, and Persistence
Userspace configures encode or decode and optional link-layer/metadata attributes. Runtime action adds or removes IFE metadata. Action configuration and counters persist per TC action.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/pkt_cls.h>`, and `<linux/ife.h>`. Integrates with TC metadata transport between network elements.

## Risks and Test Signals
Risks include encode/decode flag confusion, metadata length mismatch, and malformed Ethernet encapsulation. Test encode/decode round trips, MAC/type settings, metadata list parsing, and packet captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_ife.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mirred.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mirred.h

## Purpose
Defines the TC mirror/redirect action ABI for cloning or redirecting packets to ingress or egress of another interface or block.

## Important APIs, Types, and Constants
Action constants are `TCA_EGRESS_REDIR`, `TCA_EGRESS_MIRROR`, `TCA_INGRESS_REDIR`, and `TCA_INGRESS_MIRROR`. `struct tc_mirred` embeds `tc_gen`, `eaction`, and target `ifindex`. Attributes include timing, parameters, padding, and `TCA_MIRRED_BLOCKID`.

## Control Flow, State, and Persistence
Runtime action either redirects the packet or mirrors a clone. Target ifindex/block and generic counters are stored in action state.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ingress/egress hooks, netdevice ifindex lookup, and shared TC blocks.

## Risks and Test Signals
Risks include redirect loops, invalid ifindex, block target ambiguity, and clone allocation failures. Test mirror vs redirect semantics, ingress/egress direction, loop prevention, interface removal, and action stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mirred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mpls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mpls.h

## Purpose
Defines the TC MPLS action ABI for popping, pushing, modifying, decrementing TTL, or MAC-pushing MPLS headers.

## Important APIs, Types, and Constants
Actions include `TCA_MPLS_ACT_POP`, `TCA_MPLS_ACT_PUSH`, `TCA_MPLS_ACT_MODIFY`, `TCA_MPLS_ACT_DEC_TTL`, and `TCA_MPLS_ACT_MAC_PUSH`. `struct tc_mpls` embeds `tc_gen` and `m_action`. Attributes include protocol, label, traffic class, TTL, BOS, timing, parameters, and padding.

## Control Flow, State, and Persistence
Userspace configures MPLS operation and fields. Runtime packet handling mutates MPLS headers and updates action counters.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, MPLS forwarding, and tunnel/encapsulation pipelines.

## Risks and Test Signals
Risks include invalid TTL zero, label width overflow, BOS misuse, and protocol mismatch after pop/push. Test each action, boundary label/TC/BOS values, checksum interactions, and packet capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_nat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_nat.h

## Purpose
Defines the legacy TC NAT action ABI for address rewriting with a mask and direction flag.

## Important APIs, Types, and Constants
`struct tc_nat` embeds `tc_gen` plus `old_addr`, `new_addr`, `mask`, and `flags`. `TCA_NAT_FLAG_EGRESS` selects egress behavior. Attributes include parameters, timing, and padding.

## Control Flow, State, and Persistence
Runtime action rewrites matching IPv4 address bits according to old/new/mask and direction, then generic action state tracks counters.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>` and `<linux/types.h>`. Integrates with TC action chains; checksum correction may require `tc_csum`.

## Risks and Test Signals
Risks include IPv4-only scope, checksum staleness, mask confusion, and overlap with conntrack NAT. Test ingress/egress rewrites, mask boundary cases, checksum follow-up, and dump/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_nat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_pedit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_pedit.h

## Purpose
Defines the TC packet-edit action ABI for modifying packet bytes at offsets, with extended header-type and command metadata.

## Important APIs, Types, and Constants
Attributes include legacy parameters, extended parameters, extended keys, and per-key extended metadata. Header types include network, Ethernet, IPv4, IPv6, TCP, and UDP. Commands include set and add. `struct tc_pedit_key` carries mask, value, offset, `at`, `offmask`, and shift. `struct tc_pedit_sel` embeds `tc_gen`, key count, flags, and a flexible `keys[]` array annotated with `__counted_by(nkeys)`.

## Control Flow, State, and Persistence
Userspace provides one or more edit keys. Runtime action computes offsets, applies masks/values or additions, and records generic counters. Action config persists until removed.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC, checksum action, and packet header parsers.

## Risks and Test Signals
Risks include out-of-bounds edits, legacy network-relative semantics, flexible-array sizing, and missing checksum updates. Test multiple keys, extended header types, set/add commands, malformed offsets, action dump, and packet capture plus checksum verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_pedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_sample.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_sample.h

## Purpose
Defines the TC sample action ABI for probabilistically sending packet samples to psample groups.

## Important APIs, Types, and Constants
`struct tc_sample` embeds `tc_gen`. Attributes include timing, parameters, sample rate, truncation size, psample group, and padding.

## Control Flow, State, and Persistence
Userspace sets rate/group/truncation parameters. Runtime action samples matching packets and emits sample messages while maintaining action counters.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/pkt_cls.h>`, and `<linux/if_ether.h>`. Integrates with TC and the psample generic netlink family.

## Risks and Test Signals
Risks include unexpected sampling rates, truncation larger than packet size, and missing psample listener. Test statistical sample rate, truncation, group selection, dump attributes, and counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbedit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbedit.h

## Purpose
Defines the TC skbedit action ABI for editing skb metadata such as priority, queue mapping, mark, packet type, and flags.

## Important APIs, Types, and Constants
Feature flags include `SKBEDIT_F_PRIORITY`, `SKBEDIT_F_QUEUE_MAPPING`, `SKBEDIT_F_MARK`, `SKBEDIT_F_PTYPE`, `SKBEDIT_F_MASK`, `SKBEDIT_F_INHERITDSFIELD`, and `SKBEDIT_F_TXQ_SKBHASH`. `struct tc_skbedit` embeds `tc_gen`. Attributes carry priority, queue mapping, mark, packet type, mask, flags, and max queue mapping.

## Control Flow, State, and Persistence
Runtime action changes skb metadata, not packet bytes. Configured fields and counters persist in TC action state.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with qdisc selection, mark-based policy, and TC pipelines.

## Risks and Test Signals
Risks include invalid queue mapping, mask misuse, and confusion between packet bytes and skb metadata. Test queue steering, mark/mask behavior, priority inheritance, packet type changes, and dump/counter output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbmod.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbmod.h

## Purpose
Defines the TC skbmod action ABI for modifying Ethernet header fields and related packet metadata.

## Important APIs, Types, and Constants
Flags include `SKBMOD_F_DMAC`, `SKBMOD_F_SMAC`, `SKBMOD_F_ETYPE`, `SKBMOD_F_SWAPMAC`, and `SKBMOD_F_ECN`. `struct tc_skbmod` embeds `tc_gen` and `__u64 flags`. Attributes carry destination/source MAC, ethertype, timing, parameters, and padding.

## Control Flow, State, and Persistence
Userspace selects fields to modify. Runtime action edits packet headers and updates generic action stats.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC L2 rewrite pipelines and often with checksum or tunnel actions.

## Risks and Test Signals
Risks include malformed MAC/ethertype writes, ECN flag semantics, and offload mismatch. Test each flag, swapmac behavior, packet capture, and hardware-offload acceptance/rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_skbmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_tunnel_key.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_tunnel_key.h

## Purpose
Defines the TC tunnel key action ABI for setting or releasing tunnel metadata used by encapsulation offloads and tunnel devices.

## Important APIs, Types, and Constants
Actions are `TCA_TUNNEL_KEY_ACT_SET` and `TCA_TUNNEL_KEY_ACT_RELEASE`. `struct tc_tunnel_key` embeds `tc_gen` and `t_action`. Attributes carry IPv4/IPv6 source and destination, key id, destination port, checksum/no-frag flags, TOS, TTL, and nested tunnel options. Nested option families cover Geneve, VXLAN GBP, and ERSPAN fields.

## Control Flow, State, and Persistence
Userspace configures tunnel metadata. Runtime action writes or clears tunnel key state on the skb for later encapsulation or offload. Action state persists in TC.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, tunnel devices, switchdev/hardware offload, Geneve, VXLAN, and ERSPAN.

## Risks and Test Signals
Risks include invalid nested option lengths, IPv4/IPv6 attribute mismatch, key-id endian issues, and offload feature gaps. Test set/release, each tunnel family, option parsing boundaries, packet encapsulation, and dump/offload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_tunnel_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_vlan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_vlan.h

## Purpose
Defines the TC VLAN action ABI for popping, pushing, modifying, and Ethernet push/pop variants.

## Important APIs, Types, and Constants
Actions include `TCA_VLAN_ACT_POP`, `TCA_VLAN_ACT_PUSH`, `TCA_VLAN_ACT_MODIFY`, `TCA_VLAN_ACT_POP_ETH`, and `TCA_VLAN_ACT_PUSH_ETH`. `struct tc_vlan` embeds `tc_gen` and `v_action`. Attributes include VLAN ID, protocol, priority, Ethernet destination/source for push-eth, timing, parameters, and padding.

## Control Flow, State, and Persistence
Runtime action mutates VLAN/Ethernet headers according to configured action and records counters. Configuration persists as TC action state.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with VLAN-aware TC pipelines and hardware offload.

## Risks and Test Signals
Risks include invalid VLAN ID/priority, protocol mismatch, and push/pop on packets without expected headers. Test all actions, boundary IDs, QinQ-like protocols, packet capture, and offload dump behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_cmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_cmp.h

## Purpose
Defines the TC extended match compare ABI for matching packet bytes against masked values.

## Important APIs, Types, and Constants
`struct tcf_em_cmp` carries comparison `val`, `mask`, offset, alignment, flags, layer, and operand in bitfields. Alignment constants are `TCF_EM_ALIGN_U8`, `TCF_EM_ALIGN_U16`, and `TCF_EM_ALIGN_U32`; `TCF_EM_CMP_TRANS` flags transformed comparison.

## Control Flow, State, and Persistence
Userspace encodes match criteria in classifier netlink data. Runtime ematch reads packet data at the specified layer/offset, applies alignment/mask/operator logic, and returns match result.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch/classifier framework.

## Risks and Test Signals
Risks include bitfield layout assumptions, out-of-bounds offsets, and endian/alignment confusion. Test u8/u16/u32 matches, transformed flag, layer offsets, and malformed packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_cmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_ipt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_ipt.h

## Purpose
Defines the TC ematch ABI for using iptables/netfilter match modules inside traffic-control classifiers.

## Important APIs, Types, and Constants
Attributes include hook, match name, match revision, netfilter protocol, and match data under `TCA_EM_IPT_*`.

## Control Flow, State, and Persistence
Userspace passes module identity and opaque match data. Runtime classifier invokes the corresponding netfilter match logic for packets.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates TC ematch with netfilter/xtables match modules.

## Risks and Test Signals
Risks include opaque match-data ABI mismatches, module revision mismatch, and netfilter hook/protocol confusion. Test known xt matches, wrong revision rejection, dump round trips, and protocol-specific packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_ipt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_meta.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_meta.h

## Purpose
Defines the TC metadata ematch ABI for comparing packet, device, route, and socket metadata values.

## Important APIs, Types, and Constants
`struct tcf_meta_val` carries encoded `kind`, shift, and operator. `TCF_META_TYPE_MASK`, `TCF_META_ID_MASK`, `TCF_META_TYPE()`, and `TCF_META_ID()` decode kind. Types include variable and integer. Metadata IDs include constants for values, random, load averages, device, priority, protocol, packet type/length/data length/MAC length, netfilter mark, tcindex, route class/input interface, many socket fields, VLAN tag, and RX hash. `struct tcf_meta_hdr` stores left and right operands.

## Control Flow, State, and Persistence
Userspace describes a left/right metadata comparison. Runtime ematch fetches metadata from skb, netdevice, route, socket, or system source, applies shifts/operators, and returns match result.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC classifier ematch and socket/skb metadata.

## Risks and Test Signals
Risks include unimplemented IDs kept in ABI, changing socket metadata semantics, and type/operator mismatch. Test each supported metadata source, unsupported ID behavior, variable vs integer comparisons, and netlink dump compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_nbyte.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_nbyte.h

## Purpose
Defines the TC nbyte ematch ABI for matching a byte sequence at a packet offset.

## Important APIs, Types, and Constants
`struct tcf_em_nbyte` carries offset, 12-bit length, and 4-bit layer. The pattern data is supplied by surrounding ematch netlink payload conventions.

## Control Flow, State, and Persistence
Runtime classifier computes layer-relative offset and compares the configured byte pattern of the configured length.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch/classifier framework.

## Risks and Test Signals
Risks include length bitfield truncation, out-of-bounds offsets, and layer parsing failures on short packets. Test zero/maximum length, each supported layer, malformed packets, and dump round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_nbyte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_text.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_text.h

## Purpose
Defines the TC text ematch ABI for matching text/byte patterns with a named search algorithm over packet ranges.

## Important APIs, Types, and Constants
`TC_EM_TEXT_ALGOSIZ` is 16. `struct tcf_em_text` includes algorithm name, from/to offsets, pattern length, from/to layer bitfields, and padding.

## Control Flow, State, and Persistence
Userspace configures algorithm, layers, offsets, and pattern data. Runtime classifier searches the packet range with the selected textsearch algorithm.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/pkt_cls.h>`. Integrates with TC ematch and kernel textsearch implementations.

## Risks and Test Signals
Risks include unsupported algorithm names, range errors, bitfield layout, and high CPU cost on broad scans. Test known algorithms, offset boundaries, short packets, pattern length validation, and dump behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tc_ematch/tc_em_text.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tcp.h

## Purpose
Defines the TCP protocol UAPI: wire header layout, flag words, socket options, repair/diagnostic/authentication structs, `TCP_INFO`, timestamping stats attributes, MD5/TCP-AO key management, and zero-copy receive control.

## Important APIs, Types, and Constants
`struct tcphdr` maps the TCP wire header with endian-dependent bitfields; `union tcp_word_hdr`, `tcp_flag_word()`, and `TCP_FLAG_*` provide flag access. Socket options include classic controls (`TCP_NODELAY`, `TCP_MAXSEG`, keepalive, congestion, MD5), repair (`TCP_REPAIR*`), Fast Open, ULP, zero-copy receive, `TCP_INQ`, TCP-AO, MPTCP query, and RTO/delayed-ACK bounds. `struct tcp_info` exports extensive connection state, congestion, RTT, pacing, ECN, retransmission, and byte counters. Authentication structs include `tcp_md5sig`, `tcp_diag_md5sig`, `tcp_ao_add`, `tcp_ao_del`, `tcp_ao_info_opt`, `tcp_ao_getsockopt`, and `tcp_ao_repair`. `struct tcp_zerocopy_receive` drives zero-copy receive mapping.

## Control Flow, State, and Persistence
Applications use `setsockopt()`/`getsockopt()` to configure or query per-socket TCP state. Kernel TCP state machines own runtime state; options mutate congestion, repair, authentication keys, Fast Open, queues, and zero-copy behavior. Structs are append-only ABI where old userspace may request shorter sizes.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<asm/byteorder.h>`, and `<linux/socket.h>`. Integrates with TCP stack, inet_diag, timestamping cmsgs, MPTCP, crypto/authentication, and high-performance networking applications.

## Risks and Test Signals
Risks include endian bitfield mistakes, `tcp_info` extension compatibility, authentication reserved fields not zeroed, key leakage, and zero-copy pointer/length validation. Test header flag parsing on both endian models, `TCP_INFO` length negotiation, MD5/AO key add/delete/list, repair mode, Fast Open failure reporting, zero-copy receive error paths, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tcp_metrics.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tcp_metrics.h

## Purpose
Defines the generic netlink ABI for querying and deleting cached TCP metrics by destination/source address.

## Important APIs, Types, and Constants
Family name/version are `tcp_metrics` and `0x1`. Metric indices include RTT, RTTVAR, ssthresh, cwnd, reordering, RTT in usec, and RTTVAR in usec. Nested metric attributes mirror those values. Top-level attributes include IPv4/IPv6 destination, age, TIME_WAIT timestamp data, nested values, Fast Open MSS, SYN drop counts/timestamps, Fast Open cookie, IPv4/IPv6 source address, and padding. Commands are get and delete.

## Control Flow, State, and Persistence
Userspace sends generic netlink get/delete commands. Kernel returns or removes cached per-peer TCP metrics used to initialize future connections. Cache entries persist until aged, replaced, or deleted.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with TCP metrics cache and generic netlink tooling.

## Risks and Test Signals
Risks include misspelled legacy attribute `REODERING`, address-family mismatches, and stale Fast Open cookie data. Test netlink dumps for IPv4/IPv6, source-filtered queries, delete behavior, nested metrics parsing, and compatibility with existing `ip tcp_metrics`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tcp_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tdx-guest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tdx-guest.h

## Purpose
Defines the Intel TDX guest driver ioctl ABI for obtaining a TDREPORT0 attestation report from `TDG.MR.REPORT`.

## Important APIs, Types, and Constants
`TDX_REPORTDATA_LEN` is 64 and `TDX_REPORT_LEN` is 1024. `struct tdx_report_req` carries caller-supplied `reportdata` and output `tdreport`. `TDX_CMD_GET_REPORT0` is an `_IOWR('T', 1, struct tdx_report_req)` ioctl.

## Control Flow, State, and Persistence
Userspace supplies nonce/report data, kernel invokes the TDX TDCALL, and returns the report. No persistent state is defined by the header, though the report binds to current TD measurements.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with the TDX guest device and remote attestation workflows.

## Risks and Test Signals
Risks include exposing uninitialized report bytes, not preserving nonce, and error mapping from TDCALL failures. Test success path in a TDX guest, invalid ioctl buffers, reportdata echo/binding through attestation verifier, and non-TDX error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tdx-guest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tee.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tee.h

## Purpose
Defines the Trusted Execution Environment driver userspace ABI for version discovery, shared-memory allocation/registration, session management, invocation, cancellation, supplicant messages, and object invocation.

## Important APIs, Types, and Constants
Capabilities include generic GP, privileged, registered memory, null memref, and object-reference support. Implementation IDs include OP-TEE, AMDTEE, TSTEE, and QTEE. Key structs include `tee_ioctl_version_data`, `tee_ioctl_shm_alloc_data`, `tee_ioctl_buf_data`, `tee_ioctl_param`, `tee_ioctl_open_session_arg`, `tee_ioctl_invoke_arg`, `tee_ioctl_cancel_arg`, `tee_ioctl_close_session_arg`, supplicant recv/send args, `tee_ioctl_shm_register_data`, `tee_ioctl_shm_register_fd_data`, and `tee_ioctl_object_invoke_arg`. Ioctls cover version, shared memory allocate/register/register-fd, open session, invoke, cancel, close session, supplicant recv/send, and object invoke. Parameter attribute constants distinguish value, memref, userspace buffer, object reference, meta, null memref, and login methods.

## Control Flow, State, and Persistence
Userspace opens a TEE device, queries version, allocates/registers shared memory, opens a session, invokes TA commands, optionally cancels by cancel ID, and closes the session. Supplicant ioctls service secure-world requests. Kernel/secure OS maintain sessions, shared memory IDs/fds, object references, and pending requests.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with TEE core, OP-TEE/AMDTEE/TSTEE/QTEE drivers, tee-supplicant, dmabuf, mmap, and GlobalPlatform Client API concepts.

## Risks and Test Signals
Risks include variable-length buffer sizing up to `TEE_MAX_ARG_SIZE`, untrusted user pointers, reserved login ranges, null memref/object handling, fd lifetime, and supplicant deadlocks. Test version/capability probing, shared-memory map/unmap, open/invoke/close, cancel races, supplicant request/response, object invoke, invalid attrs, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/termios.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/termios.h

## Purpose
Provides the generic UAPI include wrapper for terminal I/O definitions, deferring architecture-specific layout and constants to `<asm/termios.h>`.

## Important APIs, Types, and Constants
This header defines no structs itself. It includes `<linux/types.h>` and `<asm/termios.h>`, which provide `termios`, `termios2`, `winsize`, modem control, and tty ioctl constants depending on architecture.

## Control Flow, State, and Persistence
No runtime logic. Terminal state is held by tty drivers and changed through termios ioctls; this file guarantees the include path for userspace.

## Dependencies and Integration Points
Depends directly on architecture UAPI. Integrates with libc, tty drivers, serial drivers, ptys, and command-line tools.

## Risks and Test Signals
Risks are architecture layout differences and include conflicts with libc termios. Test multi-arch header compilation, tty ioctl round trips, and libc/kernel header coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/thermal.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/thermal.h

## Purpose
Defines thermal subsystem UAPI names, modes, trip types, generic netlink family metadata, attributes, events, sampling groups, and commands.

## Important APIs, Types, and Constants
Constants include `THERMAL_NAME_LENGTH`, threshold direction bits, family name `thermal`, version `0x02`, and multicast group names. Enums define device mode disabled/enabled and trip types active/passive/hot/critical. Generic netlink attributes cover thermal zones, trip IDs/types/temps/hysteresis, modes, names, cooling devices, governors, CPU capability, thresholds, previous temperature, and weights. Events cover zone create/delete/enable/disable, trip crossing/change/add/delete, cooling device add/delete/state update, governor change, CPU capability change, and threshold add/delete/flush/up/down. Commands query zone IDs, trips, temperatures, governors, modes, cooling devices, thresholds, and mutate thresholds.

## Control Flow, State, and Persistence
Userspace sends generic netlink commands to query or modify thermal threshold state and subscribes to event/sampling groups. Kernel maintains thermal zone, trip, cooling device, governor, and threshold state.

## Dependencies and Integration Points
No explicit includes. Integrates with thermal core, generic netlink, platform thermal drivers, and power/monitoring daemons.

## Risks and Test Signals
Risks include threshold direction confusion, event versioning, policy daemons relying on names, and missing attributes in older kernels. Test netlink family discovery, every query command, threshold add/delete/flush, event multicast delivery, and unknown attribute tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/thp7312.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/thp7312.h

## Purpose
Defines V4L2 private control IDs for the THine THP7312 camera/ISP device.

## Important APIs, Types, and Constants
Exports four control IDs based on `V4L2_CID_USER_THP7312_BASE`: low light compensation, autofocus method, noise reduction auto, and noise reduction absolute.

## Control Flow, State, and Persistence
No runtime logic. Userspace uses V4L2 control ioctls to get/set device controls; the driver persists control state according to V4L2 semantics.

## Dependencies and Integration Points
Depends on `<linux/v4l2-controls.h>`. Integrates with THP7312 V4L2 subdevice/video drivers and camera control applications.

## Risks and Test Signals
Risks include control ID collision, missing menu/range definitions in the driver, and userspace using controls on unsupported devices. Test control enumeration, get/set round trips, default values, range validation, and media-controller pipeline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/thp7312.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/time.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/time.h

## Purpose
Defines legacy userspace time structs, timezone, interval timer IDs, POSIX clock IDs, auxiliary clock range, and timer flags.

## Important APIs, Types, and Constants
Outside the kernel it defines `struct timespec`, `struct timeval`, `struct itimerspec`, and `struct itimerval` when not already provided. It always defines `struct timezone`. Timer IDs include `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF`. Clock IDs include realtime, monotonic, process/thread CPU, monotonic raw, coarse clocks, boottime, alarm clocks, placeholder `CLOCK_SGI_CYCLE`, TAI, and auxiliary clocks from `CLOCK_AUX` through `CLOCK_AUX_LAST`. `TIMER_ABSTIME` is the timer set flag.

## Control Flow, State, and Persistence
No runtime logic. Kernel timekeeping, POSIX timers, and libc wrappers interpret these IDs and structures. Some legacy structures are Y2038-sensitive on 32-bit systems.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/time_types.h>`. Integrates with time syscalls, timer APIs, socket timestamping, libc, and VDSO clock access.

## Risks and Test Signals
Risks include libc struct conflicts, Y2038 issues with old time types, and accidental reuse of placeholder clock IDs. Test header coexistence with libc, 32-bit time64 builds, clock_gettime/setsockopt timestamp consumers, and timer absolute/relative behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/time_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/time_types.h

## Purpose
Defines kernel UAPI time structures with explicit old and time64 layouts for syscalls and embedded structures.

## Important APIs, Types, and Constants
`struct __kernel_timespec` and `struct __kernel_itimerspec` use 64-bit seconds. Legacy structures include `__kernel_old_timeval`, `__kernel_old_timespec`, and `__kernel_old_itimerval`. `struct __kernel_sock_timeval` uses signed 64-bit seconds and microseconds for socket timeout ABIs.

## Control Flow, State, and Persistence
The header has no runtime logic. It controls ABI layout for old and new time-related syscalls and embedded fields.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Used by taskstats, timer APIs, socket options, and many UAPI headers needing Y2038-safe timestamps.

## Risks and Test Signals
Risks include mixing old and time64 structs, libc conflicts, and padding/alignment differences. Test 32-bit and 64-bit layouts, syscall wrappers using time64, and socket timeout gets/sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/time_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/timerfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/timerfd.h

## Purpose
Defines timerfd userspace flags and an ioctl for setting expiration tick count.

## Important APIs, Types, and Constants
Timer set flags include `TFD_TIMER_ABSTIME` and `TFD_TIMER_CANCEL_ON_SET`. File flags map `TFD_CLOEXEC` to `O_CLOEXEC` and `TFD_NONBLOCK` to `O_NONBLOCK`. `TFD_IOC_SET_TICKS` writes a `__u64` tick count.

## Control Flow, State, and Persistence
Userspace creates and arms timerfds through syscalls and can adjust tick count through ioctl. Kernel timerfd state includes clock, expiration schedule, cancellation behavior, and accumulated expirations.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/fcntl.h>`, and `<linux/ioctl.h>`. Integrates with event loops using `poll`, `epoll`, or `read` on timerfd descriptors.

## Risks and Test Signals
Risks include O_* flag collisions, cancel-on-set semantics, and invalid tick count changes. Test absolute/relative timers, clock set cancellation, nonblocking reads, epoll readiness, and `TFD_IOC_SET_TICKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/timerfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/times.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/times.h

## Purpose
Defines `struct tms`, the userspace result for process and children CPU times returned by `times(2)`.

## Important APIs, Types, and Constants
`struct tms` contains `tms_utime`, `tms_stime`, `tms_cutime`, and `tms_cstime`, all `__kernel_clock_t`.

## Control Flow, State, and Persistence
No runtime logic. Kernel snapshots current process and waited-for child CPU accounting into the structure.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `times(2)`, libc, shell/accounting tools, and process monitoring.

## Risks and Test Signals
Risks include clock tick unit interpretation and `__kernel_clock_t` size differences. Test syscall results against `/proc` CPU accounting, child accumulation, and 32/64-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/times.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/timex.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/timex.h

## Purpose
Defines NTP/adjtimex clock discipline UAPI for controlling and observing kernel time offset, frequency, error estimates, PLL/FLL/PPS status, TAI offset, and leap state.

## Important APIs, Types, and Constants
`NTP_API` is 4. Userspace `struct timex` is defined outside the kernel with old timeval fields. `struct __kernel_timex` is the time64/padded kernel ABI form with 64-bit fields and `__kernel_timex_timeval`. Mode constants include `ADJ_OFFSET`, `ADJ_FREQUENCY`, `ADJ_MAXERROR`, `ADJ_ESTERROR`, `ADJ_STATUS`, `ADJ_TIMECONST`, `ADJ_TAI`, `ADJ_SETOFFSET`, `ADJ_MICRO`, `ADJ_NANO`, `ADJ_TICK`, and legacy single-shot modes. Status constants include `STA_PLL`, PPS flags, leap flags, `STA_UNSYNC`, `STA_NANO`, read-only masks, and time states `TIME_OK`, `TIME_INS`, `TIME_DEL`, `TIME_OOP`, `TIME_WAIT`, and `TIME_ERROR`.

## Control Flow, State, and Persistence
Userspace calls `adjtimex`/`clock_adjtime` with mode bits. Kernel timekeeping updates or returns clock discipline state. Settings such as frequency and TAI offset persist in kernel until changed or rebooted.

## Dependencies and Integration Points
Depends on `<linux/time.h>`. Integrates with NTP/PTP daemons, PPS discipline, timekeeping core, and libc time APIs.

## Risks and Test Signals
Risks include old vs time64 struct confusion, privileged write controls, leap-second state handling, and read-only status bits. Test read-only queries, each writable mode with privilege checks, nanosecond/microsecond mode, TAI updates, PPS fields, and 32-bit Y2038-safe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tiocl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tiocl.h

## Purpose
Defines console `TIOCLINUX` subcommands and selection structures for virtual terminal selection, paste, blanking, mouse reporting, foreground console, scroll, and kernel message redirection controls.

## Important APIs, Types, and Constants
Selection commands include `TIOCL_SETSEL`, selection modes, `TIOCL_PASTESEL`, `TIOCL_UNBLANKSCREEN`, `TIOCL_SELLOADLUT`, `TIOCL_GETSHIFTSTATE`, `TIOCL_GETMOUSEREPORTING`, `TIOCL_SETVESABLANK`, `TIOCL_SETKMSGREDIRECT`, `TIOCL_GETFGCONSOLE`, `TIOCL_SCROLLCONSOLE`, `TIOCL_BLANKSCREEN`, `TIOCL_BLANKEDSCREEN`, `TIOCL_GETKMSGREDIRECT`, and `TIOCL_GETBRACKETEDPASTE`. `struct tiocl_selection` carries start/end coordinates and selection mode.

## Control Flow, State, and Persistence
Userspace passes a subcommand through tty ioctl mechanisms. Kernel virtual terminal state tracks selection contents, screen blanking, mouse reporting, foreground console, and message redirection.

## Dependencies and Integration Points
No explicit includes. Integrates with virtual terminal console code, gpm-like tools, console selection/paste, and tty ioctl paths.

## Risks and Test Signals
Risks include coordinate validation, selection visibility leaks, bracketed paste state, and console-only behavior on ptys. Test each subcommand on VTs, invalid coordinates, paste behavior, blank/unblank, and foreground console query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tiocl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tipc.h

## Purpose
Defines the Transparent Inter-Process Communication socket ABI: addressing, priorities, subscriptions, events, socket options, group membership, bearer/link names, crypto key payloads, and deprecated address helper macros.

## Important APIs, Types, and Constants
Core service/socket structs include `tipc_socket_addr`, `tipc_service_addr`, `tipc_service_range`, `tipc_subscr`, `tipc_event`, `sockaddr_tipc`, `tipc_group_req`, `tipc_sioc_ln_req`, `tipc_sioc_nodeid_req`, and variable-length `tipc_aead_key`. Constants define importance levels, scopes, address types, ancillary data objects, socket options (`TIPC_IMPORTANCE` through `TIPC_NODELAY`), group flags, max name sizes, SIOC protocol-private queries, AEAD key sizes, and rekeying. Deprecated macros and inline helpers encode/decode zone/cluster/node addresses.

## Control Flow, State, and Persistence
Userspace creates AF_TIPC sockets, binds to service names/ranges, subscribes for topology events, joins groups, queries bearer/link identity, and installs crypto keys. Kernel TIPC maintains name tables, subscriptions, socket queues, groups, node/bearer/link state, and key material.

## Dependencies and Integration Points
Depends on fixed-width types and socket constants; integrates with `sockios.h` protocol-private range, TIPC core, generic socket APIs, and cluster applications.

## Risks and Test Signals
Risks include deprecated 32-bit address helpers, variable-length key sizing, subscription timeout/filter misuse, queue-depth read-only options, and unknown future socket options. Test bind/connect/sendmsg/recvmsg, subscriptions/events, group join/leave, node/link SIOC queries, AEAD key min/max validation, and old address macro compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_config.h

## Purpose
Defines the legacy TIPC configuration management ABI: command numbers, TLV encoding helpers, generic netlink message header, and TIPC socket configuration message header.

## Important APIs, Types, and Constants
Commands are grouped as public (`TIPC_CMD_GET_NODES`, media/bearer/link/name-table/stats queries), protected (`TIPC_CMD_ENABLE_BEARER`, `DISABLE_BEARER`, link parameter updates), private (`TIPC_CMD_SET_NODE_ADDR`, remote management, netid), and reserved. TLV types include unsigned, strings of several sizes, error string, network address, media/bearer/link names, node/link info, bearer/link config, name table query, and port reference. Config structs include `tipc_node_info`, `tipc_link_info`, `tipc_bearer_config`, `tipc_link_config`, `tipc_name_table_query`, `tlv_desc`, `tlv_list_desc`, `tipc_genlmsghdr`, and `tipc_cfg_msg_hdr`. Inline helpers validate, get/set, append, iterate, and align TLVs and TCM messages.

## Control Flow, State, and Persistence
Userspace builds requests with `TCM_SET` and `TLV_SET`, sends them over generic netlink or TIPC config service, and parses TLV replies. Kernel applies configuration to node, bearer, link, and management state; query replies may contain variable TLV lists.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/string.h>`, `<linux/tipc.h>`, and `<asm/byteorder.h>`. Integrates with TIPC generic netlink family `TIPC`, legacy socket config service, byte-order helpers, and management tools.

## Risks and Test Signals
Risks include TLV length/alignment bugs, network-byte-order mistakes, command privilege rules, deprecated commands, and inline helper use with undersized buffers. Test TLV boundary validation, multi-TLV iteration, public/protected/private privilege behavior, generic netlink header sizing, socket config message encoding, and malformed reply handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_config.h -->
