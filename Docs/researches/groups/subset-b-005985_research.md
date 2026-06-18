# subset-b-005985 research

Grouped research for the requested UAPI headers. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_be_config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_be_config.h

## Purpose
Defines the Raspberry Pi PiSP back-end userspace ABI: packed configuration records for Bayer and RGB processing blocks, DMA buffer addresses, format metadata, AXI bus settings, crop/scale/output programming, HOG output, and tile descriptors. It is a hardware register and buffer contract rather than executable logic.

## Important APIs, Types, And Functions
Key exports include `pisp_be_global_config`, `pisp_be_config`, `pisp_tile`, and `pisp_be_tiles_config`. Enable masks split into `pisp_be_bayer_enable`, `pisp_be_rgb_enable`, and `pisp_be_dirty`. Processing structs cover DPC, GEQ, TDN, SDN, HDR stitch, CDN, LSC, CAC, debin, tonemap, demosaic, CCM, saturation, false colour, sharpen, gamma, CSC, downscale, resample, crop, output format, and HOG.

## Control Flow
Userspace populates `pisp_be_tiles_config`: global enable bits select which pipeline blocks are live, block structs provide register values, dirty flags indicate which sections need reprogramming, and each `pisp_tile` supplies per-tile offsets, crop margins, phases, output dimensions, and buffer offsets. Drivers validate alignment, dimensions, tile count, and enabled-block dependencies before submitting work.

## State, Persistence, And Dependencies
All state is explicit in packed UAPI structs and DMA addresses. Temporal denoise and stitch blocks add frame-to-frame persistence through TDN/stitch input and output buffers. The header depends on `linux/types.h` and `pisp_common.h`; all ABI layout depends on fixed-width integer sizes and packed attributes.

## Integration Points
Integrated with Raspberry Pi media/V4L2 ISP drivers and userspace camera algorithms that compute PiSP block parameters. It shares image format, compression, decompression, black-level, white-balance, and AXI structs with `pisp_common.h`, and its HOG/output branches align with downstream capture buffers.

## Risks
The ABI is dense and highly layout-sensitive. Risks include misaligned DMA addresses, stale dirty flags, tile count greater than 64, overflow in 16-bit tile dimensions/phases, invalid grid offsets into LSC/CAC LUTs, and userspace/kernel disagreement over packed struct layout. Buffer address arrays allow multi-plane formats, so plane count and stride validation are critical.

## Test Signals
Useful tests assert `sizeof`/offset stability, tile geometry bounds, alignment rules, enable/dirty mask handling, per-output branch independence, HOG output behavior, and successful rendering of edge tiles. Runtime signals include DMA faults, corrupted tile seams, invalid colour transforms, denoise history artifacts, and driver rejection of malformed configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_be_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_common.h

## Purpose
Provides common Raspberry Pi PiSP UAPI definitions shared by front-end and back-end configuration headers: image format descriptors, Bayer order encodings, image format bitfields, compression/decompression parameters, black-level/white-balance blocks, and AXI bus configuration.

## Important APIs, Types, And Functions
Important types are `pisp_image_format_config`, `pisp_bayer_order`, `pisp_image_format`, `pisp_bla_config`, `pisp_wbg_config`, `pisp_compress_config`, `pisp_decompress_config`, and `pisp_axi_config`. Helper macros decode bits-per-sample, shift, channel count, compression, sampling, order, planarity, wallpaper layout, 32-bit pixels, and HOG mode.

## Control Flow
This header has no runtime branches; it encodes the decision table that front-end/back-end drivers and userspace use when parsing formats. Userspace chooses format bitfields, dimensions, strides, offsets, and AXI flags; drivers interpret those flags to program bus transfers and pixel pipeline format paths.

## State, Persistence, And Dependencies
State is fully caller-owned and passed in packed structs. Compression and decompression structs carry mode and offset, but no persistent memory is owned here. Dependencies are limited to `linux/types.h`.

## Integration Points
Included by `pisp_fe_config.h` and `pisp_be_config.h`. It is the common ABI vocabulary for camera pipeline formats and is expected to match userspace camera stack assumptions about Bayer order, planar layout, compression mode, and AXI behavior.

## Risks
Format values are bitfield composites, so invalid combinations can pass C type checks. Packed layouts and signed stride fields must be identical in userspace and kernel. Plane stride handling is a risk for semi-planar/planar formats, and AXI burst flags share the byte with burst length.

## Test Signals
Validate macro decoding for representative formats, packed struct sizes, RGB/Bayer greyscale handling, compression mode acceptance, stride/stride2 interpretation, and AXI maxlen flag masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_config.h

## Purpose
Defines Raspberry Pi PiSP front-end configuration UAPI for input acquisition, decompression/decompanding, black-level correction, defect correction, lens shading, stats generation, and two output branches.

## Important APIs, Types, And Functions
Primary exports are `pisp_fe_config`, `pisp_fe_global_config`, input/output AXI configs, input/output buffer configs, stats buffer config, decompand LUT, DPC/LSC/RGBY/AGC/AWB/CDAF/floating stats configs, crop/downscale configs, and `pisp_fe_output_branch_config`. Enable masks are in `pisp_fe_enable`; extra dirty bits are in `pisp_fe_dirty`.

## Control Flow
Userspace fills `pisp_fe_config`, sets global enable bits and dirty flags, provides DMA addresses, and configures stats/output branches. Drivers parse enabled blocks in pipeline order: input, optional decompress/decompand, correction blocks, stats windows, and per-branch crop/downscale/compress/output programming.

## State, Persistence, And Dependencies
The struct captures per-request hardware state. It persists only through the driver queue and DMA buffers; statistics output is written to the configured stats buffer. It depends on `pisp_common.h` and `pisp_fe_statistics.h`.

## Integration Points
Used by RP1 PiSP front-end media drivers and camera control algorithms. Statistics configuration must match the layout consumed through `pisp_fe_statistics.h`; output branches feed later pipeline stages or capture nodes.

## Risks
Packed layout, LUT sizes, stats window bounds, output buffer addresses, branch index macros, and enable/dirty consistency are the key ABI risks. Misconfigured stats weights or output dimensions can produce bad auto-exposure/autofocus feedback rather than immediate failures.

## Test Signals
Assert struct sizes/offsets, two-output branch handling, enable macro shifts, stats buffer sizing, decompand LUT length, AGC/AWB/CDAF window validation, and rejection of invalid DMA addresses or downscale ratios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_statistics.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_statistics.h

## Purpose
Defines the packed statistics buffer ABI emitted by the Raspberry Pi PiSP front end for AWB, AGC, and CDAF algorithms.

## Important APIs, Types, And Functions
Exports zone-count constants and packed structs: `pisp_agc_statistics_zone`, `pisp_agc_statistics`, `pisp_awb_statistics_zone`, `pisp_awb_statistics`, `pisp_cdaf_statistics`, and aggregate `pisp_statistics`. Constants define 4 floating zones, 1024 AGC bins, 16x16 AGC zones, 512 row sums, 32x32 AWB zones, and 8x8 CDAF figures of merit.

## Control Flow
The front-end hardware writes a single `pisp_statistics` buffer according to enabled stats blocks and configured windows. Userspace reads fixed arrays and floating regions to update exposure, white balance, and focus algorithms.

## State, Persistence, And Dependencies
No owned state exists in the header. Persistence is the DMA statistics buffer supplied through FE configuration. It depends only on `linux/types.h` and packed fixed-width integer layouts.

## Integration Points
Consumed by camera middleware that also writes `pisp_fe_config` stats windows. The struct layout must match the FE driver’s stats buffer size and the hardware’s row/histogram/zone ordering.

## Risks
Large fixed arrays make buffer size assumptions important. Counter width can still saturate for extreme frame/window configurations, and packed 64-bit fields may be misread by userspace that assumes natural alignment.

## Test Signals
Check aggregate `sizeof(struct pisp_statistics)`, zone counts, DMA buffer length, histogram bin count, floating-zone ordering, and sane nonzero counted fields under known test patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_statistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/v4l2-isp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/v4l2-isp.h

## Purpose
Defines a generic V4L2 ISP extensible parameters buffer ABI: versioned top-level parameter buffers containing a packed sequence of driver-specific parameter blocks with a common header.

## Important APIs, Types, And Functions
Exports `v4l2_isp_params_version`, block flags `V4L2_ISP_PARAMS_FL_BLOCK_DISABLE` and `V4L2_ISP_PARAMS_FL_BLOCK_ENABLE`, macro `V4L2_ISP_PARAMS_FL_DRIVER_FLAGS(n)`, `v4l2_isp_params_block_header`, and `v4l2_isp_params_buffer`.

## Control Flow
Userspace sets the buffer version, appends block-specific records back-to-back in `data[]`, and sets `data_size`. Drivers walk the byte stream by reading each aligned block header, validating `size`, checking enable/disable flags, and dispatching by driver-specific `type`.

## State, Persistence, And Dependencies
No persistent state is owned by the header. It defines a userspace-to-driver serialization format. Dependencies are `linux/stddef.h` and `linux/types.h`.

## Integration Points
Shared by ISP drivers that support V4L2 controls or buffers carrying algorithm parameters. Driver-specific headers define block type IDs and payload structs that embed `v4l2_isp_params_block_header` first.

## Risks
Malformed `data_size` or block `size` can desynchronize parsing. Version V0 and V1 are intentionally identical, which must be preserved for compatibility. Alignment and flexible array handling are ABI-sensitive.

## Test Signals
Exercise zero-block buffers, unknown versions, short block headers, oversized and undersized block `size`, enable/disable flag combinations, driver flag bit positions, and exact 8-byte header alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/v4l2-isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mei.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mei.h

## Purpose
Defines Intel Management Engine Interface userspace ioctls for connecting an open MEI device file to a firmware client by UUID, optionally with a virtual tag, and for enabling/retrieving event notifications.

## Important APIs, Types, And Functions
Exports `IOCTL_MEI_CONNECT_CLIENT`, `IOCTL_MEI_NOTIFY_SET`, `IOCTL_MEI_NOTIFY_GET`, `IOCTL_MEI_CONNECT_CLIENT_VTAG`, `mei_client`, `mei_connect_client_data`, `mei_connect_client_vtag`, and `mei_connect_client_data_vtag`.

## Control Flow
Userspace opens the MEI device, issues a connect ioctl with input UUID or UUID plus vtag, receives firmware client properties in the same union, then uses read/write on that fd for the selected firmware channel. Notification ioctls set and acknowledge pending events.

## State, Persistence, And Dependencies
Connection state is bound to the file descriptor and is released on close. The header depends on `linux/mei_uuid.h` for `uuid_le`.

## Integration Points
Used by MEI userspace services and libraries to communicate with Intel firmware clients. It integrates with file operations, MEI driver connection management, and optional notification support.

## Risks
The connect structs use unions for input/output, so callers must not expect input fields to remain intact after ioctl success. Tagged connections may fail with `-EOPNOTSUPP`. Max message size and protocol version must be honored by userspace.

## Test Signals
Test connect by UUID, vtag rejection/support, notification set/get behavior, max message length enforcement, close-triggered disconnect, and ABI ioctl numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mei_uuid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mei_uuid.h

## Purpose
Provides the little-endian UUID representation and construction macros used by MEI userspace ABI.

## Important APIs, Types, And Functions
Exports `uuid_le`, `UUID_LE(...)`, and `NULL_UUID_LE`. `UUID_LE` expands UUID fields into a 16-byte little-endian layout for the first three fields followed by raw trailing bytes.

## Control Flow
There is no runtime control flow. Callers use macros to initialize `uuid_le` constants passed into MEI connect ioctls.

## State, Persistence, And Dependencies
No persistent state. Depends on `linux/types.h` for `__u8`.

## Integration Points
Included by `linux/mei.h` and any userspace client that identifies ME firmware services.

## Risks
The macro is layout-specific; confusing canonical string order with in-memory little-endian order can connect to the wrong firmware client. It is a legacy MEI-specific UUID type, not a generic libuuid replacement.

## Test Signals
Validate byte layout for known MEI UUIDs, `NULL_UUID_LE` all-zero initialization, and compiler acceptance in constant initializers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mei_uuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/membarrier.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/membarrier.h

## Purpose
Defines the `membarrier(2)` command and flag ABI for issuing process-wide, system-wide, expedited, sync-core, and restartable-sequence memory ordering operations.

## Important APIs, Types, And Functions
Exports `enum membarrier_cmd` with query, global, global expedited, private expedited, private expedited sync-core, private expedited rseq, registration commands, `MEMBARRIER_CMD_GET_REGISTRATIONS`, and compatibility alias `MEMBARRIER_CMD_SHARED`. `enum membarrier_cmd_flag` exports `MEMBARRIER_CMD_FLAG_CPU`.

## Control Flow
Userspace calls `membarrier(MEMBARRIER_CMD_QUERY, ...)` to discover support, registers for relevant expedited commands, then invokes barriers. Some commands require prior registration and return `-EPERM`; unsupported architecture features return `-EINVAL`. RSEQ command can target one CPU when the CPU flag is supplied.

## State, Persistence, And Dependencies
Registration state is per-process and visible through `MEMBARRIER_CMD_GET_REGISTRATIONS`. The header has no dependencies beyond standard C enum layout.

## Integration Points
Used by runtimes, JITs, RCU-like libraries, and restartable sequence users that need inter-thread ordering or instruction stream serialization.

## Risks
Commands are bit positions except query value zero; treating query as a bit is wrong. Missing registration, unsupported sync-core/rseq support, or assuming non-running threads execute barriers immediately can lead to subtle correctness bugs.

## Test Signals
Check query bitmasks, registration idempotence, `GET_REGISTRATIONS`, failure paths for unregistered expedited calls, CPU-targeted rseq behavior, and architecture-specific sync-core availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/membarrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/memfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/memfd.h

## Purpose
Defines `memfd_create(2)` flags for anonymous file creation, sealing, executable policy, hugetlb backing, and hugepage size encodings.

## Important APIs, Types, And Functions
Exports `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, `MFD_EXEC`, `MFD_HUGE_SHIFT`, `MFD_HUGE_MASK`, and all known `MFD_HUGE_*` size constants from `asm-generic/hugetlb_encode.h`.

## Control Flow
Userspace passes flags to `memfd_create`; the kernel creates a file descriptor with close-on-exec, sealing permission, executable restrictions, or hugetlb allocation as requested. Hugepage size bits are meaningful only with `MFD_HUGETLB`.

## State, Persistence, And Dependencies
Resulting state lives in the returned anonymous file descriptor and its seals/mapping behavior. Dependencies are hugetlb encoding macros.

## Integration Points
Used by sandboxing, shared-memory IPC, JITs, loaders, and tests that need anonymous sealed files or explicit executable policy.

## Risks
Executable flags are policy-sensitive, sealing must be requested up front, and hugepage sizes are platform dependent. Passing unsupported hugepage encodings or conflicting exec flags should be validated by syscall tests.

## Test Signals
Test close-on-exec, adding seals only after `MFD_ALLOW_SEALING`, `MFD_NOEXEC_SEAL` behavior, `MFD_EXEC` behavior, hugetlb creation, and failure on unsupported hugepage sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/memfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mempolicy.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mempolicy.h

## Purpose
Defines NUMA memory policy modes and flags for `set_mempolicy(2)`, `get_mempolicy(2)`, `mbind(2)`, and zone reclaim sysctl bit meanings.

## Important APIs, Types, And Functions
Exports policy modes `MPOL_DEFAULT`, `MPOL_PREFERRED`, `MPOL_BIND`, `MPOL_INTERLEAVE`, `MPOL_LOCAL`, `MPOL_PREFERRED_MANY`, `MPOL_WEIGHTED_INTERLEAVE`, mode flags `MPOL_F_STATIC_NODES`, `MPOL_F_RELATIVE_NODES`, `MPOL_F_NUMA_BALANCING`, get flags, mbind move/strict flags, internal flags, and reclaim bits.

## Control Flow
Userspace combines a mode with legal mode flags, supplies nodemasks to policy syscalls, and optionally requests strict validation or page migration through mbind flags. `get_mempolicy` flags choose whether to query by address, node, or allowed memories.

## State, Persistence, And Dependencies
Policies persist in task or VMA memory policy state inside the kernel. Header dependency is `linux/errno.h`.

## Integration Points
Used by NUMA-aware allocators, databases, HPC runtimes, and test tools. Zone reclaim constants map to `/proc/sys/vm/zone_reclaim_mode`.

## Risks
Mode flags share integer space with modes, internal flags are not syscall inputs, and unsupported `MPOL_MF_LAZY` is explicitly invalid. Incorrect nodemask relativity/static semantics can place memory on unintended nodes.

## Test Signals
Exercise each public mode, nodemask validation, get flags, mbind strict/move behavior, NUMA balancing flag acceptance, weighted interleave support, and sysctl bit interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mempolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mii.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mii.h

## Purpose
Defines MII/PHY register numbers, bitfields, advertised link modes, link partner ability bits, flow-control bits, MMD access flags, and ioctl payload for PHY register access.

## Important APIs, Types, And Functions
Exports `MII_*` register constants, `BMCR_*`, `BMSR_*`, `ADVERTISE_*`, `LPA_*`, `EXPANSION_*`, `ESTATUS_*`, SGMII encodings, 1000BASE-T control/status bits, `FLOW_CTRL_*`, `MII_MMD_CTRL_*`, and `struct mii_ioctl_data`.

## Control Flow
Networking tools issue SIOCxMII ioctls using `mii_ioctl_data` with PHY id/register number and input/output values. Drivers interpret register bitfields to reset PHYs, start autonegotiation, advertise modes, and report link capabilities.

## State, Persistence, And Dependencies
State lives in PHY hardware registers and driver-managed link state. Dependencies are `linux/types.h` and `linux/ethtool.h`.

## Integration Points
Used by legacy `mii-tool`, ethtool paths, PHY drivers, and network device ioctl handlers.

## Risks
Some bit values are overloaded between twisted-pair and 1000BASE-X contexts. Register accesses can be hardware-specific, and ioctl callers must handle endianness and unsupported registers correctly.

## Test Signals
Validate ioctl read/write round trips on simulated PHYs, reset/autoneg bits, advertisement masks, SGMII speed decode, MMD access modes, and compatibility of `struct mii_ioctl_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/minix_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/minix_fs.h

## Purpose
Defines Minix filesystem on-disk constants and structs for inode, superblock, and directory entry layouts across Minix v1/v2/v3 variants.

## Important APIs, Types, And Functions
Exports root inode, link limits, map slots, clean/error flags, `minix_inode`, `minix2_inode`, `minix_super_block`, `minix3_super_block`, `minix_dir_entry`, and `minix3_dir_entry`.

## Control Flow
Filesystem code reads the superblock, detects version/magic externally, then interprets inode and directory layouts according to the variant. Directory entries use flexible names after the inode field.

## State, Persistence, And Dependencies
These structs map persistent on-disk bytes. Dependencies are `linux/types.h` and `linux/magic.h`; block-size macro availability affects `MINIX_INODES_PER_BLOCK`.

## Integration Points
Used by Minix filesystem mounting, fsck tools, and disk image parsers.

## Risks
Layouts differ substantially between v1 and v2/v3, including inode size, time fields, uid/gid widths, and zone pointer widths. Flexible directory names require external record-size knowledge.

## Test Signals
Mount/read known Minix v1/v2/v3 images, validate superblock parsing, inode size/layout, root inode handling, link limits, and directory entry traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/minix_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/misc/bcm_vk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/misc/bcm_vk.h

## Purpose
Defines Broadcom Valkyrie misc device ioctls and firmware status register bit encodings for firmware loading, reset, readiness, deinit, and reset reason reporting.

## Important APIs, Types, And Functions
Exports `vk_image`, `vk_reset`, `VK_IOCTL_LOAD_IMAGE`, `VK_IOCTL_RESET`, image types `VK_IMAGE_TYPE_BOOT1/BOOT2`, firmware status BAR offsets, readiness/deinit masks, and reset reason fields.

## Control Flow
Userspace passes a firmware image descriptor or reset arguments through ioctls. Firmware status is read from BAR offsets and decoded through bit masks to determine boot phases, app readiness, deinit progress, reset completion, and reset cause.

## State, Persistence, And Dependencies
Persistent state is in device firmware and BAR registers. The header depends on `linux/ioctl.h` and `linux/types.h`.

## Integration Points
Used by the BCM VK kernel driver and device-management utilities that stage boot images and monitor firmware lifecycle.

## Risks
The filename is a fixed 64-byte array and must be terminated/validated by userspace and driver. Firmware state bits may be transient, and reset reason decoding depends on top-nibble masking.

## Test Signals
Verify ioctl numbers, image type validation, filename bounds, reset argument handling, BAR status decode, ready/deinit masks, and reset reason extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/misc/bcm_vk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mman.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mman.h

## Purpose
Adds generic Linux memory-management UAPI definitions around remap flags, overcommit policy, shared/private mmap flags, droppable mappings, hugepage encodings, and `cachestat` structures.

## Important APIs, Types, And Functions
Exports `MREMAP_MAYMOVE`, `MREMAP_FIXED`, `MREMAP_DONTUNMAP`, overcommit constants, `MAP_SHARED`, `MAP_PRIVATE`, `MAP_SHARED_VALIDATE`, `MAP_DROPPABLE`, `MAP_HUGE_*` encodings, `cachestat_range`, and `cachestat`.

## Control Flow
Callers pass flags to `mmap`, `mremap`, or `cachestat`-style interfaces. `MAP_SHARED_VALIDATE` asks the kernel to reject unknown extension flags. `MAP_HUGE_*` bits select a hugetlb size when combined with architecture-defined hugetlb mapping flags.

## State, Persistence, And Dependencies
State is VM-area configuration in the kernel and cached page accounting returned by `cachestat`. Depends on `asm/mman.h`, `asm-generic/hugetlb_encode.h`, and `linux/types.h`.

## Integration Points
Used by libc, memory allocators, databases, shared-memory applications, and page-cache observability tools.

## Risks
Some flags are architecture-dependent through `asm/mman.h`; unsupported hugepage sizes must fail cleanly. `MAP_DROPPABLE` has pressure-related semantics that differ from normal shared/private mappings.

## Test Signals
Exercise mremap flag combinations, unknown flag rejection with `MAP_SHARED_VALIDATE`, hugepage size acceptance/failure, overcommit sysctl values, and `cachestat` range accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mmc/ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mmc/ioctl.h

## Purpose
Defines MMC block-device ioctl ABI for issuing raw MMC commands and bounded multi-command sequences from userspace.

## Important APIs, Types, And Functions
Exports `mmc_ioc_cmd`, `mmc_ioc_multi_cmd`, `MMC_IOC_CMD`, `MMC_IOC_MULTI_CMD`, `MMC_IOC_MAX_BYTES`, `MMC_IOC_MAX_CMDS`, and helper macro `mmc_ioc_cmd_set_data`.

## Control Flow
Userspace fills opcode, argument, flags, block size/count, timeouts, direction, optional reliable-write bit, and `data_ptr`; the driver sends the command and writes response words back. Multi-command ioctl executes `cmds[]` in sequence.

## State, Persistence, And Dependencies
Command effects persist on the card depending on opcode, especially RPMB or write commands. Dependencies are `linux/types.h` and `linux/major.h`.

## Integration Points
Used by eMMC/SD provisioning, RPMB tooling, diagnostics, and card-management utilities on MMC block devices.

## Risks
Raw commands can corrupt media. `data_ptr` alignment and 32/64-bit ABI padding are critical. The ioctl enforces per-call byte and command-count limits; larger transfers must use normal block I/O.

## Test Signals
Validate struct size on 32/64-bit builds, read-command response/data, multi-command ordering, max byte/count rejection, reliable-write flag handling, and timeout overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mmc/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mmtimer.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mmtimer.h

## Purpose
Defines Intel Multimedia Timer character-device ioctls for querying timer register offset, resolution, frequency, counter width, mmap availability, and current counter value.

## Important APIs, Types, And Functions
Exports ioctl base `MMTIMER_IOCTL_BASE` and ioctls `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`.

## Control Flow
Userspace issues required query ioctls to learn timing parameters, optionally maps registers if available, and reads counter values either through ioctl or mmap.

## State, Persistence, And Dependencies
State lives in hardware timer registers and driver implementation. No header dependencies are required.

## Integration Points
Used by legacy SGI/Intel multimedia timer applications and drivers exposing IA-PC multimedia timer-compatible devices.

## Risks
Some commands are optional, hardware may not safely support mmap, and return units differ: resolution is in femtoseconds while frequency is in Hz.

## Test Signals
Validate ioctl numbers, required-command support, nonzero frequency/resolution, counter monotonicity, mmap availability consistency, and graceful handling of unsupported offset queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mmtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/module.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/module.h

## Purpose
Defines flags accepted by `finit_module(2)` for loading kernel modules with version/vermagic override behavior or compressed module input.

## Important APIs, Types, And Functions
Exports `MODULE_INIT_IGNORE_MODVERSIONS`, `MODULE_INIT_IGNORE_VERMAGIC`, and `MODULE_INIT_COMPRESSED_FILE`.

## Control Flow
Userspace passes these flags to `finit_module`; the kernel module loader either enforces or bypasses selected compatibility checks and optionally treats the file as compressed.

## State, Persistence, And Dependencies
Successful calls persist by loading module state into the kernel. The header has no dependencies.

## Integration Points
Used by module-loading tools such as kmod/insmod and kernel selftests.

## Risks
Ignoring modversions or vermagic can load incompatible modules and destabilize the kernel. Compressed-file support is kernel-configuration dependent.

## Test Signals
Test flag acceptance/rejection, compressed module loading, incompatible vermagic/modversion behavior, and permission/capability enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/module_signature.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/module_signature.h

## Purpose
Defines the appended kernel module signature marker, signature type enum, and trailing metadata block layout used to locate and verify signed modules.

## Important APIs, Types, And Functions
Exports `MODULE_SIGNATURE_MARKER`, `MODULE_SIGNATURE_TYPE_PKCS7`, and packed metadata `module_signature` fields: algorithm, hash, id type, signer/key lengths, padding, and big-endian signature length.

## Control Flow
Module loading scans for the marker, parses the appended signature data sequence, reads the metadata block, and verifies a PKCS#7 signature according to kernel key policy.

## State, Persistence, And Dependencies
Signature data persists appended to module files. Depends on `linux/types.h` for fixed-width and big-endian types.

## Integration Points
Used by module signing tools, kernel module loader, and secure boot/module signature enforcement.

## Risks
The length field is big-endian and the structure is at the end of appended data. Incorrect signer/key lengths or marker scanning can make valid modules unverifiable.

## Test Signals
Validate signed module parsing, marker detection, PKCS#7 type handling, big-endian `sig_len`, rejection of truncated trailers, and unsigned-module behavior under enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/module_signature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mount.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mount.h

## Purpose
Defines the Linux mount syscall UAPI: classic `mount(2)` flags, new mount API flags, fsconfig commands, mount attributes, and `statmount(2)`/`listmount(2)` query structures and masks.

## Important APIs, Types, And Functions
Key exports include `MS_*`, `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN_CLOEXEC`, `FSPICK_*`, `fsconfig_command`, `FSMOUNT_*`, `MOUNT_ATTR_*`, `mount_attr`, `statmount`, `mnt_id_req`, `STATMOUNT_*`, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

## Control Flow
Classic mount calls use `MS_*` flags. New API flow creates/picks trees, configures filesystems with `fsconfig_command`, mounts/moves them, and changes attributes with `mount_setattr`. Query syscalls accept `mnt_id_req` and fill `statmount`, including variable strings after `str[]`.

## State, Persistence, And Dependencies
State persists in VFS mount namespace, superblock, propagation, and mount attributes. Depends on `linux/types.h` and externally on `O_CLOEXEC` availability.

## Integration Points
Used by mount utilities, container runtimes, namespace tools, systemd, and filesystem management libraries.

## Risks
Many flags are kernel-internal despite UAPI exposure. Struct version sizes must be honored. `statmount` string offsets and buffer sizing can return `EOVERFLOW`. Propagation and idmapped mount attributes have security implications.

## Test Signals
Validate classic remount masks, new API flag masks, fsconfig command handling, mount attribute set/clear behavior, `statmount` mask/string offsets, `listmount` ordering, versioned struct sizes, and fd-based queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mpls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mpls.h

## Purpose
Defines MPLS label stack entry layout, reserved label constants, netlink statistics attributes, and link statistics struct.

## Important APIs, Types, And Functions
Exports `mpls_label`, masks/shifts for label, TC, bottom-of-stack, and TTL fields, reserved label constants, `MPLS_STATS_*`, and `mpls_link_stats`.

## Control Flow
Networking code encodes/decodes a 32-bit big-endian MPLS label stack entry using masks and shifts. Netlink stats embed `mpls_link_stats` under AF_MPLS attributes.

## State, Persistence, And Dependencies
State lives in packets, routes, and per-link counters. Depends on `linux/types.h` and byteorder definitions.

## Integration Points
Used by MPLS route configuration, packet parsing, rtnetlink stats, and diagnostic tools.

## Risks
Endianness is critical: `entry` is `__be32`. Reserved labels have protocol-specific semantics and should not be treated as ordinary forwarding labels.

## Test Signals
Test label encode/decode, reserved label handling, TTL/TC/S bit extraction, link stats dump layout, and AF_MPLS netlink nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mpls_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mpls_iptunnel.h

## Purpose
Defines rtnetlink encapsulation attributes for MPLS IP tunnels.

## Important APIs, Types, And Functions
Exports `MPLS_IPTUNNEL_UNSPEC`, `MPLS_IPTUNNEL_DST`, `MPLS_IPTUNNEL_TTL`, and `MPLS_IPTUNNEL_MAX`.

## Control Flow
Userspace configures routes with `RTA_ENCAP` containing nested MPLS IP tunnel attributes: destination label stack and optional TTL. The kernel route code parses those attributes to build the encapsulation action.

## State, Persistence, And Dependencies
State persists in route entries. The header has no include dependencies.

## Integration Points
Used by iproute2 and rtnetlink consumers configuring MPLS encap routes.

## Risks
The header only defines numeric attributes; payload validation is external. Wrong nesting under `RTA_ENCAP` or missing destination attributes makes routes invalid.

## Test Signals
Validate netlink policy for `MPLS_IPTUNNEL_DST` and TTL, route add/dump round trips, and rejection of malformed nested attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mpls_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mptcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mptcp.h

## Purpose
Defines Multipath TCP socket option ABI for connection info, subflow flags/addrs, full info buffers, reset reason codes, path-manager names, endpoint flags, and socket option IDs.

## Important APIs, Types, And Functions
Exports `mptcp_info`, subflow flag macros, PM event/address flags, reset reason constants, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, `mptcp_full_info`, and socket options `MPTCP_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`, `MPTCP_FULL_INFO`.

## Control Flow
Userspace calls `getsockopt` on MPTCP sockets. Simple info returns `mptcp_info`; full info uses size fields and user pointers for arrays of subflow and TCP info. Kernel writes actual counts and structure sizes for compatibility.

## State, Persistence, And Dependencies
State is live MPTCP connection and subflow state inside the kernel. Depends on socket, IPv4/IPv6 address, const, types, and `linux/mptcp_pm.h`.

## Integration Points
Used by MPTCP-aware diagnostics, network managers, tests, and path-management tooling.

## Risks
Several fields preserve old names via macros and include holes that must not be repurposed casually. Full-info pointers and size fields need careful 32/64-bit compatibility and bounds checking.

## Test Signals
Validate `getsockopt` size negotiation, fallback and key-received flags, subflow count/address reporting, full-info truncation behavior, reset reason exposure, and endpoint flag masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mptcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mptcp_pm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mptcp_pm.h

## Purpose
Defines the auto-generated generic netlink ABI for the MPTCP path manager: family metadata, event types, address/subflow/endpoint attributes, command attributes, event attributes, and command IDs.

## Important APIs, Types, And Functions
Exports `MPTCP_PM_NAME`, `MPTCP_PM_VER`, `mptcp_event_type`, `MPTCP_PM_ADDR_ATTR_*`, `MPTCP_SUBFLOW_ATTR_*`, `MPTCP_PM_ENDPOINT_ADDR`, `MPTCP_PM_ATTR_*`, `mptcp_event_attr`, and `MPTCP_PM_CMD_*`.

## Control Flow
Userspace sends generic netlink commands to add/delete/get/flush endpoints, set/get limits, set flags, announce/remove addresses, and create/destroy subflows. Kernel sends events for connection creation, establishment, close, address announcement/removal, subflow establishment/close/priority, and listener lifecycle.

## State, Persistence, And Dependencies
State persists in MPTCP path-manager endpoint tables, per-connection tokens, limits, and active subflows. The header is generated from a netlink YAML spec.

## Integration Points
Used by `ip mptcp`, MPTCP daemons, tests, and monitoring agents subscribing to command and event multicast groups defined in `mptcp.h`.

## Risks
Auto-generated numeric IDs are ABI; changing them breaks netlink clients. Events have optional attributes and gaps in numbering, so parsers must tolerate missing fields and sparse event values.

## Test Signals
Check YNL spec conformance, command round trips, event multicast delivery, endpoint address nesting, subflow token reporting, limits update, and unknown attribute tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mptcp_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mqueue.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mqueue.h

## Purpose
Defines POSIX message queue limits, attributes, and Linux-specific netlink cookie behavior for `SIGEV_THREAD` notification emulation.

## Important APIs, Types, And Functions
Exports `MQ_PRIO_MAX`, `MQ_BYTES_MAX`, `mq_attr`, notification states `NOTIFY_NONE`, `NOTIFY_WOKENUP`, `NOTIFY_REMOVED`, and `NOTIFY_COOKIE_LEN`.

## Control Flow
Userspace configures queues with `mq_attr`. For `SIGEV_THREAD`, userspace passes an AF_NETLINK fd in `sigev_signo` and a cookie pointer; kernel sends the cookie to the netlink socket and rewrites its last byte with a notification code.

## State, Persistence, And Dependencies
Queue state persists in mqueue objects and per-uid kernel memory accounting. Depends on `linux/types.h`.

## Integration Points
Used by libc POSIX mqueue implementation, real-time applications, and notification helpers.

## Risks
`SIGEV_THREAD` is explicitly userspace-implemented; misuse of signal fields or cookie length breaks notification. Limits are defaults/ceilings interacting with sysctls and per-uid accounting.

## Test Signals
Test queue creation with attributes, priority limit, per-uid byte limit behavior, notify set/remove, netlink cookie contents, and reserved fields zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mroute.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mroute.h

## Purpose
Defines IPv4 multicast routing socket option/ioctl/netlink ABI compatible with historical mrouted/PIMd control planes.

## Important APIs, Types, And Functions
Exports `MRT_*` commands, `SIOCGETVIFCNT`, `SIOCGETSGCNT`, `SIOCGETRPF`, flush flags, `vifctl`, `mfcctl`, `sioc_sg_req`, `sioc_vif_req`, `igmpmsg`, IPMR netlink table/vif/cache-report attributes, and IGMP pseudo-message constants.

## Control Flow
A multicast routing daemon initializes mroute state, adds VIFs and multicast forwarding cache entries, receives cache-miss/control messages, queries counters, and eventually flushes or shuts down routing.

## State, Persistence, And Dependencies
State persists in kernel multicast routing tables, VIF entries, MFC entries, and counters. Depends on sockios, types, and IPv4 address definitions.

## Integration Points
Used by mrouted, PIM daemons, rtnetlink table dumps, and IPv4 multicast forwarding code.

## Risks
Compatibility typedefs (`vifbitmap_t`, `vifi_t`) and `MAXVIFS` are ABI constraints. Interface selection can be by address or ifindex depending on flags. Counter fields are `unsigned long`, creating ABI-width considerations.

## Test Signals
Test daemon init/done, VIF add/delete, MFC add/delete, cache miss messages, counter ioctls, flush flags, PIM register messages, and netlink dump attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mroute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mroute6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mroute6.h

## Purpose
Defines IPv6 multicast routing UAPI for MIF management, multicast forwarding cache, counters, kernel-to-daemon control messages, and cache-report netlink attributes.

## Important APIs, Types, And Functions
Exports `MRT6_*`, `SIOCGETMIFCNT_IN6`, `SIOCGETSGCNT_IN6`, flush flags, `mifi_t`, `if_set` and macros, `mif6ctl`, `mf6cctl`, `sioc_sg_req6`, `sioc_mif_req6`, `mrt6msg`, and `IP6MRA_CREPORT_*`.

## Control Flow
IPv6 multicast daemons initialize routing, add MIFs, install MFC entries, receive `mrt6msg` notifications on cache misses or whole-packet events, query counters, and flush or close state.

## State, Persistence, And Dependencies
State is kernel IPv6 multicast routing table, interface bitsets, and counters. Depends on const, types, sockios, and IPv6 sockaddr definitions.

## Integration Points
Used by PIM6/mrouted-style daemons, IPv6 raw socket control flows, and netlink cache-report consumers.

## Risks
The `if_set` macros use BSD `bcopy`/`bzero` names for userspace compatibility. `SIOCGETRPF` collides in name with IPv4 header. ABI width for `unsigned long` counters must be respected.

## Test Signals
Validate MIF add/delete, MFC entries, bitset operations, cache miss delivery, raw socket message format, counter ioctls, flush flags, and netlink cache reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mroute6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mrp_bridge.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mrp_bridge.h

## Purpose
Defines bridge Media Redundancy Protocol constants and enums for ring/interconnect roles, states, port states/roles, TLV headers, and sub-TLV headers.

## Important APIs, Types, And Functions
Exports frame/domain/version/prio constants and enums `br_mrp_ring_role_type`, `br_mrp_in_role_type`, `br_mrp_ring_state_type`, `br_mrp_in_state_type`, `br_mrp_port_state_type`, `br_mrp_port_role_type`, `br_mrp_tlv_header_type`, and `br_mrp_sub_tlv_header_type`.

## Control Flow
Bridge MRP code and userspace configure roles and states, then encode/decode MRP Ethernet TLVs according to these numeric values.

## State, Persistence, And Dependencies
State persists in bridge MRP instance configuration and received/transmitted protocol frames. Depends on `linux/types.h` and `linux/if_ether.h`.

## Integration Points
Used by bridge netlink MRP configuration and industrial Ethernet redundancy control planes.

## Risks
Protocol numeric values are wire-visible. Inconsistent role/state handling can block or forward ports incorrectly in a redundancy ring.

## Test Signals
Validate netlink role/state round trips, TLV type encoding, max frame length, port state transitions, and interoperability with MRP peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mrp_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/msdos_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/msdos_fs.h

## Purpose
Defines FAT/MS-DOS filesystem constants, on-disk boot/FSINFO/directory layouts, attribute bits, FAT limits, endian helpers, and VFAT/FAT ioctl ABI.

## Important APIs, Types, And Functions
Exports sector and directory sizing constants, attribute flags, FAT cluster markers, FSINFO signatures, `__fat_dirent`, VFAT/FAT ioctls, `fat_boot_sector`, `fat_boot_fsinfo`, `msdos_dir_entry`, and `msdos_dir_slot`.

## Control Flow
Filesystem code parses the boot sector, determines FAT variant by cluster count, reads FSINFO when signatures match, walks directory entries and long-name slots, and exposes ioctls for readdir compatibility, attributes, and volume ID.

## State, Persistence, And Dependencies
Structs map persistent disk bytes. Depends on `linux/types.h`, `linux/magic.h`, and byteorder helpers.

## Integration Points
Used by FAT/VFAT filesystem drivers, fsck/mkfs tools, mount utilities, and Android/Linux attribute utilities.

## Risks
On-disk fields are little-endian and packed by layout convention. Long filename slots and deleted/free markers are easy to misparse. FAT12/16/32 boundary constants determine variant behavior.

## Test Signals
Test FAT12/16/32 image parsing, FSINFO validation, long-name reconstruction, ioctl attribute get/set, volume ID query, deleted/free entries, and endian conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/msdos_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/msg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/msg.h

## Purpose
Defines System V message queue UAPI constants, legacy structs, message buffer layout, info struct, and default queue/message limits.

## Important APIs, Types, And Functions
Exports `MSG_STAT`, `MSG_INFO`, `MSG_STAT_ANY`, `MSG_NOERROR`, `MSG_EXCEPT`, `MSG_COPY`, legacy `msqid_ds`, `msgbuf`, `msginfo`, and defaults `MSGMNI`, `MSGMAX`, `MSGMNB`, plus obsolete pool/map constants.

## Control Flow
Userspace uses msgsnd/msgrcv/msgctl. Receive flags control truncation, type exclusion, and copy-without-remove behavior. `msgctl` info/stat commands return queue metadata through legacy or architecture-specific 64-bit structs.

## State, Persistence, And Dependencies
State persists in IPC namespaces as message queue objects and queued messages. Depends on `linux/ipc.h` and includes `asm/msgbuf.h`.

## Integration Points
Used by SysV IPC libraries, `ipcs`, checkpoint/restore tools, and compatibility layers.

## Risks
Legacy structs are retained for ABI compatibility and contain unused pointer fields. Defaults can be changed by sysctl, and arithmetic around limits must avoid overflow.

## Test Signals
Validate send/receive flags, `MSG_COPY`, msgctl stat/info, namespace limits, queue byte accounting, permission checks, and 32/64-bit ABI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mshv.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mshv.h

## Purpose
Defines Microsoft Hypervisor device UAPI for creating partitions and VPs, mapping guest memory, eventfd/ioeventfd routing, MSI routing, access bitmaps, root hypercalls, VP run/state ioctls, VTL devices, VMBus SINT operations, and hypercall setup.

## Important APIs, Types, And Functions
Primary exports include `mshv_create_partition`, `mshv_create_partition_v2`, `mshv_create_vp`, `mshv_user_mem_region`, `mshv_user_irqfd`, `mshv_user_ioeventfd`, `mshv_user_irq_table`, `mshv_gpap_access_bitmap`, `mshv_root_hvcall`, `mshv_run_vp`, `mshv_get_set_vp_state`, VTL/VMBus structs, capability constants, and many `MSHV_*` ioctls.

## Control Flow
VMMs open `/dev/mshv`, create a partition, set early properties, initialize it, create VPs, map guest memory, route interrupts/events, then run VPs and handle intercept messages. State pages may be mmaped at documented offsets. VTL and hypercall devices expose additional control paths.

## State, Persistence, And Dependencies
State persists in hypervisor partition, VP, memory map, interrupt routing, eventfd bindings, and VTL/hypercall device contexts. Depends on `linux/types.h`.

## Integration Points
Used by virtualization monitors targeting Microsoft Hypervisor APIs, with interactions to eventfd, mmap, userspace memory, and Hyper-V data structures.

## Risks
Many fields are MBZ, page-aligned, or architecture-specific. Ioctl numbers are reused per derived fd type, so callers must issue them on the correct fd. User pointers, variable arrays, and page-size assumptions require careful validation.

## Test Signals
Validate partition lifecycle, v2 feature banks, memory map/unmap alignment, VP creation/run, mmap offsets, state get/set buffer sizing, IRQ/eventfd routing, access bitmap clear/set, hypercall status propagation, and MBZ rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mshv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mtio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mtio.h

## Purpose
Defines magnetic tape ioctl ABI: operation commands, status/position structs, device type constants, generic status bit macros, and SCSI tape option encodings.

## Important APIs, Types, And Functions
Exports `mtop`, `mtget`, `mtpos`, tape operations `MTRESET` through `MTWEOFI`, ioctls `MTIOCTOP`, `MTIOCGET`, `MTIOCPOS`, device type constants, `GMT_*` status macros, and `MT_ST_*` SCSI tape options.

## Control Flow
Userspace sends `MTIOCTOP` with an operation/count, queries status with `MTIOCGET`, and position with `MTIOCPOS`. Drivers return residual counts, generic/device status, error registers, file number, and block number.

## State, Persistence, And Dependencies
State persists in tape drive position, media, buffering, density, compression, locks, and driver options. Depends on `linux/types.h` and `linux/ioctl.h`.

## Integration Points
Used by `mt`, backup software, SCSI tape drivers, and legacy QIC/ftape interfaces.

## Risks
Some operations are destructive (`MTERASE`, destructive self tests, partition formatting). Not all drives support all commands. Status field interpretation is driver/device-specific.

## Test Signals
Validate ioctl numbers, no-op/status query, rewind/space operations on virtual tape, status macros, block/density option encoding, unsupported operation errors, and position reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mtio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nbd-netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nbd-netlink.h

## Purpose
Defines generic netlink family, multicast group, commands, and nested attributes for configuring Network Block Device instances.

## Important APIs, Types, And Functions
Exports `NBD_GENL_FAMILY_NAME`, `NBD_GENL_VERSION`, `NBD_GENL_MCAST_GROUP_NAME`, command enum `NBD_CMD_*`, top-level attrs `NBD_ATTR_*`, nested device-list attrs `NBD_DEVICE_*`, and nested socket attrs `NBD_SOCK_*`.

## Control Flow
Userspace sends netlink CONNECT, DISCONNECT, RECONFIGURE, STATUS requests with attributes such as index, size, block size, timeouts, flags, sockets, backend identifier, and device list. Kernel replies or multicasts link-dead events.

## State, Persistence, And Dependencies
State persists in configured NBD devices, socket attachments, timeouts, and flags. No external header dependencies.

## Integration Points
Used by nbd-client tooling and kernel NBD generic netlink configuration paths, complementing legacy ioctl setup in `nbd.h`.

## Risks
Nested list policies must be parsed exactly. Socket fds are passed as attributes and must be validated. Reconfigure semantics can race with active block I/O.

## Test Signals
Validate family/version, connect with multiple sockets, status dumps, device list nesting, disconnect events, backend identifier round trip, and malformed attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nbd-netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nbd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nbd.h

## Purpose
Defines legacy Network Block Device ioctl ABI, NBD protocol command/flag constants, and wire request/reply packet layouts.

## Important APIs, Types, And Functions
Exports `NBD_SET_*`, `NBD_DO_IT`, `NBD_DISCONNECT`, command enum `NBD_CMD_*`, server flags `NBD_FLAG_*`, command flags, client flags, magics `NBD_REQUEST_MAGIC`/`NBD_REPLY_MAGIC`, and packed `nbd_request`/`nbd_reply`.

## Control Flow
Userspace configures an NBD block device with ioctls, hands sockets to the kernel, starts serving with `NBD_DO_IT`, and handles read/write/flush/trim/write-zeroes requests over the socket protocol.

## State, Persistence, And Dependencies
State persists in NBD device configuration, sockets, block queue, and protocol request cookies. Depends on `linux/types.h`.

## Integration Points
Used by legacy nbd-client/server implementations and kernel block device request paths. Generic netlink configuration is defined separately in `nbd-netlink.h`.

## Risks
Wire fields are network byte order and packed. Unsupported structured replies are explicitly not defined here. Server/client flags have different semantics and gaps preserved for userspace compatibility.

## Test Signals
Validate ioctl setup, block size/size flags, disconnect behavior, request/reply magic and cookie matching, command flag handling, flush/trim/write-zeroes support, and endian correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ncsi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ncsi.h

## Purpose
Defines NC-SI generic netlink command and attribute ABI for inspecting packages/channels, selecting preferred interfaces, setting package/channel masks, and sending raw NC-SI commands.

## Important APIs, Types, And Functions
Exports `ncsi_nl_commands`, `ncsi_nl_attrs`, `ncsi_nl_pkg_attrs`, and `ncsi_nl_channel_attrs` with fields for ifindex, package/channel IDs, command data, masks, version, link state, active/forced flags, and VLAN lists.

## Control Flow
Userspace requests package info, sets or clears preferred package/channel combinations, sends NC-SI commands, or changes allow masks. Dump replies nest packages and channels under list attributes.

## State, Persistence, And Dependencies
State persists in NCSI device package/channel selection and masks. No external header dependencies.

## Integration Points
Used by BMC/network management tools and kernel NCSI netlink family.

## Risks
Commands require specific attribute combinations. Multi-mode and masks can alter which management channels are available, so validation and rollback matter.

## Test Signals
Validate package/channel dump nesting, preferred channel set/clear, raw command payload handling, package/channel masks, VLAN list attributes, and missing-required-attribute errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ncsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ndctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ndctl.h

## Purpose
Defines NVDIMM/ndctl ioctl ABI for DIMM flags, label/config data, vendor calls, address range scrub, error clearing, device type flags, and generic firmware command packages.

## Important APIs, Types, And Functions
Exports command structs for DIMM flags/config/vendor/ARS/clear-error, command IDs `ND_CMD_*`, helper inline command-name functions, `ND_IOCTL_*`, device type constants, `nd_driver_flags`, ARS masks, `nd_cmd_pkg`, and NVDIMM family IDs.

## Control Flow
Userspace issues ioctls on nvdimm bus/dimm/region devices. Some commands read/write label storage, some start/status ARS scans, some clear errors, and `ND_IOCTL_CALL` passes firmware-specific packages with input/output size negotiation.

## State, Persistence, And Dependencies
State persists in NVDIMM label/config areas, firmware state, ARS scan state, and persistent memory error metadata. Depends on `linux/types.h`.

## Integration Points
Used by ndctl/libndctl, persistent memory management tools, and ACPI NFIT/vendor firmware interfaces.

## Risks
Packed flexible-array structs require exact allocation sizing. Firmware package commands have reserved fields that must be zero. ARS status uses variable records and status masks.

## Test Signals
Validate ioctl numbers, config get/set bounds, vendor command size negotiation, ARS cap/start/status records, clear-error accounting, command-name helpers, and reserved-field rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ndctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/neighbour.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/neighbour.h

## Purpose
Defines rtnetlink neighbour/FDB and neighbour-table ABI: neighbour messages, attributes, flags, NUD states, cacheinfo, table stats/config, table parameters, and FDB extension attributes.

## Important APIs, Types, And Functions
Exports `ndmsg`, `NDA_*`, neighbour flags `NTF_*`, extended flags, `NUD_*`, `nda_cacheinfo`, `ndt_stats`, `NDTPA_*`, `ndtmsg`, `ndt_config`, `NDTA_*`, FDB notification bits, and `NFEA_*`.

## Control Flow
Userspace sends rtnetlink messages to add/delete/get neighbours or FDB entries and to get/set neighbour table parameters. Dumps may be split across messages with global table data followed by device-specific parameter sets.

## State, Persistence, And Dependencies
State persists in neighbour caches, bridge FDBs, and neighbour table configuration per namespace/interface. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by `ip neigh`, bridge tooling, routing daemons, EVPN control planes, and kernel neighbour discovery/ARP/NDP subsystems.

## Risks
Some flags are bridge-FDB-specific and states may be ignored for externally learned entries. Managed/locked/externally validated flags have control-plane semantics. Timing fields are milliseconds with 64-bit attrs.

## Test Signals
Validate add/delete/dump, state transitions, cacheinfo fields, extended flags, table parameter get/set, split table dumps, FDB activity notifications, and locked/managed entry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/neighbour.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/net.h

## Purpose
Defines legacy networking syscall multiplexor operation numbers, socket state enum, protocol count alias, and accept-state bit.

## Important APIs, Types, And Functions
Exports `NPROTO`, `SYS_SOCKET` through `SYS_SENDMMSG`, `socket_state`, and `__SO_ACCEPTCON`.

## Control Flow
Historically, architectures with `socketcall` used `SYS_*` operation numbers to dispatch individual socket operations. `socket_state` describes socket connection lifecycle states used in user-visible headers.

## State, Persistence, And Dependencies
Socket state persists in kernel socket objects. Depends on `linux/socket.h` and `asm/socket.h`.

## Integration Points
Used by libc compatibility layers, tracing, seccomp filters, and old architecture socketcall paths.

## Risks
This is a compatibility header; modern direct syscalls may not use `SYS_*`. `SS_*` names can conflict with userspace expectations if mixed with other socket state definitions.

## Test Signals
Validate socketcall numbering on applicable architectures, seccomp filter constants, socket state value stability, and `NPROTO == AF_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_dropmon.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/net_dropmon.h

## Purpose
Defines drop monitor netlink ABI for configuring packet/drop alerts and reporting software/hardware drop summaries, packet metadata, ports, stats, origins, and reasons.

## Important APIs, Types, And Functions
Exports legacy `net_dm_drop_point`, config/alert/user message structs, `NET_DM_CMD_*`, alert group, `net_dm_attr`, `net_dm_alert_mode`, port attrs, stats attrs, and `net_dm_origin`.

## Control Flow
Userspace configures alert mode/count/delay, starts or stops monitoring, and receives summary or packet alerts. Newer netlink attributes describe program counter/symbol, ingress port, timestamps, payload, hardware trap data, stats, cookies, and reason strings.

## State, Persistence, And Dependencies
State persists in drop monitor configuration and counters. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by dropwatch, network observability agents, devlink/hardware trap reporting, and kernel drop monitor subsystem.

## Risks
Legacy flexible arrays and newer nested attributes coexist. Packet-alert payloads may be truncated, and hardware/software origins need clear handling to avoid misleading diagnostics.

## Test Signals
Validate config get/set, start/stop, summary vs packet alerts, payload truncation/original length, hardware trap attrs, stats counters, port attrs, and multicast group delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_dropmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_namespace.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/net_namespace.h

## Purpose
Defines rtnetlink namespace ID attributes for creating, querying, and translating network namespace identifiers.

## Important APIs, Types, And Functions
Exports `NETNSA_NONE`, `NETNSA_NSID_NOT_ASSIGNED`, `NETNSA_NSID`, `NETNSA_PID`, `NETNSA_FD`, `NETNSA_TARGET_NSID`, `NETNSA_CURRENT_NSID`, and `NETNSA_MAX`.

## Control Flow
Userspace sends RTM_NEWNSID/RTM_GETNSID messages with pid or fd identifying a namespace and receives/sets namespace IDs, optionally translating from current to target namespace IDs.

## State, Persistence, And Dependencies
Namespace ID mappings persist in kernel net namespace state. No external include dependencies.

## Integration Points
Used by iproute2, container runtimes, namespace-aware netlink tooling, and rtnetlink.

## Risks
`NETNSA_NSID_NOT_ASSIGNED` is negative while attrs are enum IDs; callers must not confuse sentinel values with attribute numbers. Fd/pid lifetimes affect namespace lookup.

## Test Signals
Validate nsid assignment/query, pid/fd lookup, target/current translation, unassigned sentinel handling, and namespace teardown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_shaper.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/net_shaper.h

## Purpose
Defines the auto-generated generic netlink ABI for network shapers: family metadata, shaper scope/metric enums, handle/capability attributes, and get/set/delete/group/capability commands.

## Important APIs, Types, And Functions
Exports `NET_SHAPER_FAMILY_NAME`, `NET_SHAPER_FAMILY_VERSION`, `net_shaper_scope`, `net_shaper_metric`, `NET_SHAPER_A_*`, handle attrs, capability attrs, and `NET_SHAPER_CMD_*`.

## Control Flow
Userspace queries capabilities, then gets/sets/deletes/groups shapers by handle. Scope determines whether handle ID is a netdevice, queue, or sched-tree node; metrics select BPS or PPS shaping.

## State, Persistence, And Dependencies
Shaper state persists in device or queue scheduling configuration. The header is generated from `net_shaper.yaml`.

## Integration Points
Used by YNL-aware tools, network drivers exposing hardware shapers, and traffic-management configuration.

## Risks
This ABI is generated and numeric IDs must remain stable. Capability attrs must be consulted before setting optional properties such as nesting, burst, priority, or weight.

## Test Signals
Validate family version, capability queries per ifindex/scope, set/get/delete round trips, nested group handling, unsupported metric rejection, and handle attr parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_shaper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_tstamp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/net_tstamp.h

## Purpose
Defines network timestamping UAPI for `SO_TIMESTAMPING`, hardware timestamp configuration, timestamp packet info control messages, transmit-time scheduling, and provider qualifiers.

## Important APIs, Types, And Functions
Exports `hwtstamp_provider_qualifier`, `SOF_TIMESTAMPING_*`, `SOF_TIMESTAMPING_TX_RECORD_MASK`, `so_timestamping`, `hwtstamp_config`, `hwtstamp_flags`, `hwtstamp_tx_types`, `hwtstamp_rx_filters`, `scm_ts_pktinfo`, `txtime_flags`, and `sock_txtime`.

## Control Flow
Applications set socket timestamping flags or pass control messages, configure hardware timestamping through SIOCG/SIOCSHWTSTAMP using `hwtstamp_config`, receive timestamps on normal data or error queues, and optionally schedule transmit times with `SO_TXTIME`.

## State, Persistence, And Dependencies
State persists in socket options, network-device hardware timestamp configuration, PHC binding, and per-packet control metadata. Depends on `linux/types.h` and `linux/socket.h`.

## Integration Points
Used by PTP/IEEE 1588 stacks, time synchronization daemons, packet capture, AF_XDP/NIC timestamp feature reporting, and qdisc transmit-time scheduling.

## Risks
Flags are split between recording and reporting semantics. Drivers may broaden requested RX filters and return the actual filter. Bonded PHC index can change after failover.

## Test Signals
Validate socket option flags/mask, TX software/hardware timestamps, RX filter fallback, PHC binding, packet info cmsgs, one-step timestamp modes, `SO_TXTIME` deadline/error reporting, and invalid flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/net_tstamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netconf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netconf.h

## Purpose
Defines rtnetlink network-configuration message and attributes for per-family/per-interface forwarding and related kernel networking settings.

## Important APIs, Types, And Functions
Exports `netconfmsg`, `NETCONFA_*`, `NETCONFA_MAX`, `NETCONFA_ALL`, `NETCONFA_IFINDEX_ALL`, and `NETCONFA_IFINDEX_DEFAULT`.

## Control Flow
Userspace sends netconf rtnetlink queries or updates with an address family and ifindex/default/all selectors, and receives attributes such as forwarding, rp_filter, multicast forwarding, proxy neighbour, and link-down route behavior.

## State, Persistence, And Dependencies
State persists in per-network-namespace and per-interface sysctl-like network configuration. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by iproute2 and network managers to observe IPv4/IPv6 forwarding-related configuration.

## Risks
Special negative ifindex constants are selectors, not normal interface indices. Attribute availability is family-specific.

## Test Signals
Validate all/default/interface queries, family-specific attrs, forwarding/rp_filter values, multicast forwarding reporting, and selector handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netdev.h

## Purpose
Defines the auto-generated generic netlink ABI for netdev introspection and control: XDP features, page pools, NAPI, queues, qstats, dmabuf binding, queue leases, and netdev multicast groups.

## Important APIs, Types, And Functions
Exports `NETDEV_FAMILY_NAME`, `NETDEV_FAMILY_VERSION`, feature enums `netdev_xdp_act`, `netdev_xdp_rx_metadata`, `netdev_xsk_flags`, queue/qstats/NAPI enums, many `NETDEV_A_*` attribute families, `NETDEV_CMD_*`, and multicast groups `NETDEV_MCGRP_MGMT`/`PAGE_POOL`.

## Control Flow
Userspace sends generic netlink get/set/bind/create requests and receives device, page-pool, queue, NAPI, qstats, lease, and dmabuf attributes. Notifications report device and page-pool add/delete/change events.

## State, Persistence, And Dependencies
State is live netdevice, NAPI, queue, page-pool, AF_XDP, dmabuf, and lease state in the kernel. The header is generated from `netdev.yaml`.

## Integration Points
Used by YNL tools, network diagnostics, AF_XDP setup, page-pool observability, and advanced queue binding.

## Risks
Generated numeric attributes are ABI. Some enums are bitmasks while others are ordinal. Empty enum families exist as generated placeholders and should be tolerated by clients.

## Test Signals
Validate YNL schema conformance, dev get/dump, page-pool stats, NAPI set/get, queue/qstats get, dmabuf bind, RX/TX bind, queue create, multicast notifications, and feature bit decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netdevice.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netdevice.h

## Purpose
Defines basic network device UAPI constants for hardware address length, default device group, name assignment type, media port selection, and hardware address assignment type.

## Important APIs, Types, And Functions
Exports `MAX_ADDR_LEN`, `INIT_NETDEV_GROUP`, `NET_NAME_*`, media port enum values `IF_PORT_*`, and `NET_ADDR_*`.

## Control Flow
Drivers and netlink/ioctl paths report naming origin, port type, and address origin to userspace. No executable logic is defined in the header.

## State, Persistence, And Dependencies
State persists as netdevice metadata. Depends on `linux/if.h`, `linux/if_ether.h`, `linux/if_packet.h`, and `linux/if_link.h`.

## Integration Points
Used by sysfs `name_assign_type`, iproute2, udev naming logic, network drivers, and hardware address reporting.

## Risks
Values are long-standing ABI and must not be renumbered. `MAX_ADDR_LEN` bounds hardware address arrays across many link types.

## Test Signals
Validate sysfs/netlink exposure of name assignment, MAC address assignment type, media port values, and max address length assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter.h

## Purpose
Defines base netfilter UAPI verdicts, verdict encoding helpers, hook numbers, protocol family IDs, and generic IPv4/IPv6 address union.

## Important APIs, Types, And Functions
Exports verdict constants `NF_DROP` through `NF_STOP`, masks/flags `NF_VERDICT_*`, helpers `NF_QUEUE_NR` and `NF_DROP_ERR`, hooks `nf_inet_hooks`/`nf_dev_hooks`, `NFPROTO_*`, and `nf_inet_addr`.

## Control Flow
Netfilter rules/hooks return verdict values; high bits encode queue numbers or drop errno. Hook numbers identify traversal points for IPv4/IPv6/netdev, and protocol IDs identify rule family.

## State, Persistence, And Dependencies
State persists in netfilter rulesets and packet traversal context. Depends on types, compiler annotations, and IPv4/IPv6 address headers.

## Integration Points
Used by nftables/iptables, nfqueue, conntrack/NAT headers, firewall extensions, and kernel hooks.

## Risks
Verdict lower 8 bits and high-bit auxiliary encoding must be masked correctly. `NF_STOP` is deprecated but retained for userspace compatibility. DECnet is userspace-only.

## Test Signals
Validate verdict masking, queue-number encoding, drop errno encoding, hook IDs, protocol family IDs, and address union layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set.h

## Purpose
Defines core ipset UAPI: protocol versions, command IDs, netlink attributes, error codes, command/create/CADT flags, dimensions, counter match structs, and legacy socket-option requests.

## Important APIs, Types, And Functions
Exports `IPSET_PROTOCOL`, `IPSET_MAXNAMELEN`, `ipset_cmd`, `IPSET_ATTR_*`, `ipset_errno`, `ipset_cmd_flags`, `ipset_cadt_flags`, `ipset_create_flags`, `ipset_adt`, `ip_set_id_t`, dimension/kopt enums, counter match structs, `SO_IP_SET`, and get/version request structs.

## Control Flow
Userspace manages sets through netlink commands: create/destroy/flush/rename/swap/list/save/add/del/test/header/type/get. Attributes nest command data and ADT entries; flags tune existence behavior, counters, comments, skb metadata, nomatch, and ordering.

## State, Persistence, And Dependencies
State persists in kernel ipset sets, elements, counters, comments, skbinfo, and references from firewall rules. Depends on `linux/types.h`.

## Integration Points
Used by ipset userspace, iptables/ip6tables match/target compatibility, and netfilter set lookups.

## Risks
Protocol version compatibility matters. Attribute spaces overlap by command context. Set IDs are 16-bit, and `IPSET_INVALID_ID` is a sentinel. Counter structs differ for backward compatibility.

## Test Signals
Validate protocol negotiation, all management commands, nested ADT parsing, restore line numbers, type revision min/max, counter/comment/skbinfo flags, legacy socket options, and type-specific error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_bitmap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_bitmap.h

## Purpose
Defines bitmap ipset type-specific error codes.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_BITMAP_RANGE` and `IPSET_ERR_BITMAP_RANGE_SIZE`, starting from `IPSET_ERR_TYPE_SPECIFIC` in `ip_set.h`.

## Control Flow
Bitmap set create/add/test/delete operations report these errors when an element is outside the configured range or the requested range exceeds type size limits.

## State, Persistence, And Dependencies
State is bitmap set range and element bits in kernel ipset storage. Depends on `linux/netfilter/ipset/ip_set.h`.

## Integration Points
Used by ipset bitmap type implementations and userspace error decoding.

## Risks
Error values are ABI and must not collide with other type-specific ranges. Userspace must distinguish range validation from generic invalid address errors.

## Test Signals
Create bitmap sets with boundary ranges, add/delete/test endpoints, and assert expected errors for out-of-range and too-large ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_hash.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_hash.h

## Purpose
Defines hash ipset type-specific error codes.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_HASH_FULL`, `IPSET_ERR_HASH_ELEM`, `IPSET_ERR_INVALID_PROTO`, `IPSET_ERR_MISSING_PROTO`, `IPSET_ERR_HASH_RANGE_UNSUPPORTED`, and `IPSET_ERR_HASH_RANGE`.

## Control Flow
Hash set operations return these errors when tables are full, elements are null/invalid, protocol constraints fail, or ranges are unsupported/invalid.

## State, Persistence, And Dependencies
State persists in hash set buckets and elements. Depends on `ip_set.h`.

## Integration Points
Used by hash-based ipset types and userspace diagnostics.

## Risks
Range support is type/revision-specific. Protocol fields may be mandatory for some set dimensions and invalid for others.

## Test Signals
Exercise full-table behavior, null elements, protocol-required and invalid-protocol cases, unsupported range adds, and hash resize behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_list.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_list.h

## Purpose
Defines list:set ipset type-specific error codes for referenced set management.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_NAME`, `IPSET_ERR_LOOP`, `IPSET_ERR_BEFORE`, `IPSET_ERR_NAMEREF`, `IPSET_ERR_LIST_FULL`, and `IPSET_ERR_REF_EXIST`.

## Control Flow
List set operations add/delete/test referenced sets, optionally before another set, and return these errors for missing names/references, loops, full lists, or absent references.

## State, Persistence, And Dependencies
State persists as ordered references from a list:set to other sets. Depends on `ip_set.h`.

## Integration Points
Used by ipset list type implementation and userspace error messages.

## Risks
Loop prevention is critical to avoid recursive matching. Ordering operations depend on correct `BEFORE`/reference attribute handling.

## Test Signals
Validate add/delete/test references, before/after ordering, loop rejection, missing reference errors, full-list behavior, and reference removal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_common.h

## Purpose
Defines common netfilter connection tracking UAPI states, status bits, event IDs, expectation events, and expectation flags.

## Important APIs, Types, And Functions
Exports `ip_conntrack_info`, state-bit macros `NF_CT_STATE_*`, `ip_conntrack_status`, `ip_conntrack_events`, `ip_conntrack_expect_events`, and expectation flags `NF_CT_EXPECT_*`.

## Control Flow
Conntrack classifies packets as new, related, established, reply-direction, invalid, or untracked. Status bits mark lifecycle and NAT/helper/offload conditions. Netlink/event consumers receive state/status updates by event ID.

## State, Persistence, And Dependencies
State persists in conntrack entries, expectations, NAT status, helper/offload markers, and event streams. No external dependencies.

## Integration Points
Used by nftables/iptables ct matches, ctnetlink, NAT, helpers, flow offload, and userspace conntrack tools.

## Risks
Some bits are unchangeable from userspace and some have in-kernel repurposing under `__KERNEL__`. Reply-direction arithmetic underlies state bit macros and must be preserved.

## Test Signals
Validate state bit expansion, NAT done/mask behavior, event emission, helper/offload bits, expectation flags, and userspace attempts to modify unchangeable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_ftp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_ftp.h

## Purpose
Defines FTP conntrack helper message types exposed to userspace.

## Important APIs, Types, And Functions
Exports `nf_ct_ftp_type` values for FTP `PORT`, `PASV`, `EPRT`, and `EPSV`.

## Control Flow
The FTP helper parses control-channel commands/replies and classifies expectations by these types for userspace visibility or helper logic.

## State, Persistence, And Dependencies
State persists in FTP-related conntrack expectations and helper metadata. No external dependencies.

## Integration Points
Used by conntrack helpers and ctnetlink users decoding FTP expectation type.

## Risks
Only type identifiers are defined; parsing and security validation happen elsewhere. FTP control parsing is sensitive to NAT and malformed commands.

## Test Signals
Validate helper classification for active/passive IPv4 and extended IPv6-aware FTP commands, and ctnetlink reporting of expectation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_ftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_sctp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_sctp.h

## Purpose
Defines SCTP conntrack state enum exposed to userspace.

## Important APIs, Types, And Functions
Exports `sctp_conntrack` states from none/closed through cookie wait/echoed, established, shutdown states, heartbeat sent/acked, and max.

## Control Flow
SCTP conntrack transitions among these states as SCTP chunks are observed. Userspace tools decode the enum in conntrack state dumps.

## State, Persistence, And Dependencies
State persists in SCTP conntrack entries. Depends on `nf_conntrack_tuple_common.h`.

## Integration Points
Used by conntrack, nftables/iptables ct modules, and userspace conntrack tooling.

## Risks
`SCTP_CONNTRACK_HEARTBEAT_ACKED` is marked no longer used but remains ABI. Invalid transitions must be handled in implementation, not this header.

## Test Signals
Validate state reporting for SCTP association setup/shutdown, cookie paths, heartbeat cases, and compatibility for the unused heartbeat-acked value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tcp.h

## Purpose
Defines TCP conntrack state enum, TCP tracking flags, challenge-ACK/simultaneous-open bits, and flag/mask struct exposed to userspace.

## Important APIs, Types, And Functions
Exports `tcp_conntrack`, alias `TCP_CONNTRACK_SYN_SENT2`, timeout/diagnostic states, `IP_CT_TCP_FLAG_*`, `IP_CT_EXP_CHALLENGE_ACK`, `IP_CT_TCP_SIMULTANEOUS_OPEN`, and `nf_ct_tcp_flags`.

## Control Flow
Conntrack updates TCP states as packets progress through handshake, established data, FIN/close, retransmission, ignore, and unacknowledged paths. Flags capture negotiated TCP options and tracking policy.

## State, Persistence, And Dependencies
State persists in TCP conntrack protocol info. Depends on `linux/types.h`.

## Integration Points
Used by ctnetlink, conntrack tools, nft/iptables ct matches, and TCP NAT sequence adjustment.

## Risks
`TCP_CONNTRACK_LISTEN` is obsolete but aliased for SYN_SENT2 compatibility. Flags have mask semantics, so updates must distinguish desired value from affected bits.

## Test Signals
Validate state machine reporting across handshakes/closes/retransmits, TCP option flags, simultaneous open, challenge ACK expectation, and ctnetlink flag mask updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tuple_common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tuple_common.h

## Purpose
Defines common conntrack tuple direction enum, manipulable protocol-port/key union, and ctinfo-to-direction helper macro.

## Important APIs, Types, And Functions
Exports `ip_conntrack_dir`, `nf_conntrack_man_proto`, and `CTINFO2DIR(ctinfo)`. The union includes generic `all`, TCP/UDP/DCCP/SCTP ports, ICMP id, and GRE key fields in network byte order.

## Control Flow
Conntrack/NAT code maps ctinfo values to original or reply direction and manipulates protocol-specific tuple fields when applying NAT or matching flows.

## State, Persistence, And Dependencies
Tuple state persists in conntrack entries and NAT ranges. Depends on `linux/types.h`, `linux/netfilter.h` for userspace, and `nf_conntrack_common.h`.

## Integration Points
Used by NAT UAPI, ctnetlink, protocol helpers, and nftables/iptables tuple-related code.

## Risks
All fields are network order. GRE key is represented as 16 bits for PPTP compatibility though GRE keys can be 32-bit.

## Test Signals
Validate direction macro around `IP_CT_IS_REPLY`, NAT port/key manipulation, network-order encoding, and compatibility with `nf_nat.h` range structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tuple_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_log.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_log.h

## Purpose
Defines netfilter logging option flags and maximum log prefix length.

## Important APIs, Types, And Functions
Exports `NF_LOG_TCPSEQ`, `NF_LOG_TCPOPT`, `NF_LOG_IPOPT`, `NF_LOG_UID`, reserved `NF_LOG_NFLOG`, `NF_LOG_MACDECODE`, `NF_LOG_MASK`, and `NF_LOG_PREFIXLEN`.

## Control Flow
Userspace logging rules pass these flags to request extra packet metadata in log output; logging backends mask and decode supported options.

## State, Persistence, And Dependencies
State persists in firewall logging rule configuration. No dependencies.

## Integration Points
Used by iptables/nftables log targets, kernel netfilter loggers, and userspace rule builders.

## Risks
`NF_LOG_NFLOG` is marked unsupported and must not be reused. Prefix length is an ABI limit for rule validation.

## Test Signals
Validate flag mask handling, prefix length enforcement, TCP/IP option logging, UID logging, MAC decode output, and rejection/ignore behavior for unsupported bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_nat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_nat.h

## Purpose
Defines netfilter NAT range flags and IPv4/generic NAT range structs used by userspace rule APIs and conntrack/NAT integrations.

## Important APIs, Types, And Functions
Exports `NF_NAT_RANGE_*`, `NF_NAT_RANGE_PROTO_RANDOM_ALL`, `NF_NAT_RANGE_MASK`, `nf_nat_ipv4_range`, `nf_nat_ipv4_multi_range_compat`, `nf_nat_range`, and `nf_nat_range2`.

## Control Flow
Firewall/NAT userspace supplies address and protocol min/max ranges plus flags controlling IP mapping, protocol specificity, randomization, persistence, offsets, and netmap behavior. Kernel NAT code applies these ranges to conntrack tuples.

## State, Persistence, And Dependencies
NAT state persists in rules and conntrack NAT mappings. Depends on `linux/netfilter.h` and `nf_conntrack_tuple_common.h`.

## Integration Points
Used by iptables/nftables NAT expressions, ctnetlink, and NAT helpers.

## Risks
IPv4 compatibility range differs from generic `nf_inet_addr` ranges. `nf_nat_range2` adds `base_proto`; older userspace may only understand earlier structs.

## Test Signals
Validate each flag, IPv4 and IPv6 range rule insertion, random/full-random behavior, persistent mappings, proto offsets, netmap, compatibility multi-range handling, and mask rejection of unknown bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_nat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_synproxy.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_synproxy.h

## Purpose
Defines SYNPROXY option flags and configuration struct for netfilter SYN proxy handling.

## Important APIs, Types, And Functions
Exports `NF_SYNPROXY_OPT_MSS`, `NF_SYNPROXY_OPT_WSCALE`, `NF_SYNPROXY_OPT_SACK_PERM`, `NF_SYNPROXY_OPT_TIMESTAMP`, `NF_SYNPROXY_OPT_ECN`, `NF_SYNPROXY_OPT_MASK`, and `nf_synproxy_info`.

## Control Flow
Userspace configures SYNPROXY rules with selected TCP option handling, window scale, and MSS. Kernel SYN proxy logic uses this data when synthesizing handshake responses and validating connections.

## State, Persistence, And Dependencies
State persists in netfilter rules and per-flow SYNPROXY/conntrack state. Depends on `linux/types.h`.

## Integration Points
Used by nftables/iptables SYNPROXY targets and conntrack TCP handling.

## Risks
`NF_SYNPROXY_OPT_ECN` is defined but excluded from `NF_SYNPROXY_OPT_MASK`, so callers must follow mask semantics. Incorrect MSS/window scale settings can break legitimate clients.

## Test Signals
Validate rule insertion, option mask handling, SYN/SYN-ACK option synthesis, MSS/wscale values, timestamp/SACK behavior, and ECN handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_synproxy.h -->
