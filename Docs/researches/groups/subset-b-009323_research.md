# subset-b-009323 research

Grouped research report for Linux UAPI headers bundled with strace under `sources/test-tools/strace/bundled/linux/include/uapi/linux`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/userfaultfd.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/userfaultfd.h

Purpose: declares the userfaultfd userspace ABI as strace sees it: `/dev/userfaultfd` creation, `userfaultfd(2)` flags, the UFFD API handshake, ioctl command numbers, page-fault/event message layouts, supported feature bits, range operation structs, and operation modes for resolving faults. It is a pure UAPI contract header, not an implementation.

Important APIs/types/functions: important constants are `USERFAULTFD_IOC_NEW`, `UFFD_API`, `UFFD_API_REGISTER_MODES`, `UFFD_API_FEATURES`, `UFFD_API_IOCTLS`, `UFFD_API_RANGE_IOCTLS`, `_UFFDIO_*` command indexes, and ioctl macros such as `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_COPY`, `UFFDIO_ZEROPAGE`, `UFFDIO_MOVE`, `UFFDIO_WRITEPROTECT`, `UFFDIO_CONTINUE`, and `UFFDIO_POISON`. Core types are `struct uffd_msg`, `uffdio_api`, `uffdio_range`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_writeprotect`, `uffdio_continue`, `uffdio_poison`, and `uffdio_move`. Feature bits include write-protect page-fault flags, fork/remap/remove/unmap events, missing/minor fault support for hugetlbfs and shmem, `SIGBUS`, thread id reporting, exact address reporting, async write protection, poisoning, and move support.

Control flow: a userspace monitor creates a userfaultfd, calls `UFFDIO_API` with `UFFD_API` and requested feature bits, registers a memory range with `UFFDIO_REGISTER`, then reads packed `uffd_msg` records from the fd. Page-fault messages carry fault flags, address, and optionally faulting thread id; non-fault events describe forked fd, remap ranges, removed ranges, or unmapped ranges. The monitor resolves faults or updates tracked memory with range ioctls: copy from a source address, install zero pages, continue minor faults, move pages, poison pages, toggle write protection, wake waiters, or unregister a range.

State/persistence behavior: the header defines per-fd kernel state negotiated by `uffdio_api.features` and `uffdio_api.ioctls`, plus per-range registration state returned in `uffdio_register.ioctls`. There is no on-disk persistence. The state lives behind the userfaultfd and registered virtual memory ranges until unregister or fd close. Several structs deliberately place kernel-written result fields at the end (`copy`, `zeropage`, `mapped`, `updated`, `move`) so kernel `copy_from_user` does not read output-only fields.

Dependencies/integration: depends on `linux/types.h` and ioctl encoding macros from the including environment. strace integration must decode both the syscall flag `UFFD_USER_MODE_ONLY` and all userfaultfd ioctl payloads, including the historical `_IOR` direction quirk for `UFFDIO_UNREGISTER` and `UFFDIO_WAKE`. Decoders should use the negotiated bitmasks to print feature, event, mode, and range ioctl names accurately.

Risks and test signals: ABI compatibility is sensitive to packed `uffd_msg`, fixed ioctl numbers, 64-bit bitmasks, output fields at the tail of structs, and mode bits whose validity depends on negotiated range ioctls. Tests should exercise `UFFDIO_API` feature probing, register modes, each range operation, write-protect `DONTWAKE` behavior, event message union decoding, and unknown future bits. strace-specific tests should confirm ioctl direction, packed message sizes, and feature/mode flag names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/userfaultfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/utsname.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/utsname.h

Purpose: defines the historical and current Linux UTS name structures returned by uname-related syscalls. The file preserves old ABI layouts while exposing `struct new_utsname` with the domain name field used by modern `uname`.

Important APIs/types/functions: exported constants are `__OLD_UTS_LEN` set to 8 and `__NEW_UTS_LEN` set to 64. Exported types are `struct oldold_utsname`, with five 9-byte character arrays; `struct old_utsname`, with five 65-byte arrays; and `struct new_utsname`, with six 65-byte arrays for `sysname`, `nodename`, `release`, `version`, `machine`, and `domainname`. There are no functions or inline helpers.

Control flow: none in this header. Kernel uname paths fill one of these fixed-size records, and user space reads the resulting character arrays according to the syscall/compat ABI it invoked.

State/persistence behavior: the structs carry snapshots of kernel UTS state at syscall time. The header itself owns no state and has no persistence. The terminating-byte sizing pattern is explicit: usable lengths are 8 or 64 characters plus one byte for NUL termination.

Dependencies/integration: has only an include guard and no type includes. strace and compat layers use these layouts to decode `oldolduname`, `olduname`, and `uname` results and to distinguish whether `domainname` is present.

Risks and test signals: the main risk is confusing payload length with array size, especially `__NEW_UTS_LEN + 1`, or printing `domainname` for old layouts. Tests should cover all three layouts, exact string truncation/termination, and architecture compat paths where older uname syscalls still appear.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/utsname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-common.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-common.h

Purpose: provides common Video4Linux2 selection and EDID definitions shared by main V4L2 and V4L2 subdevice APIs. The comment advises including it indirectly through `videodev2.h` or `v4l2-subdev.h`, but the header carries reusable ABI constants.

Important APIs/types/functions: selection target constants describe crop and compose rectangles: `V4L2_SEL_TGT_CROP`, `CROP_DEFAULT`, `CROP_BOUNDS`, `NATIVE_SIZE`, `COMPOSE`, `COMPOSE_DEFAULT`, `COMPOSE_BOUNDS`, and `COMPOSE_PADDED`. Selection flags are `V4L2_SEL_FLAG_GE`, `V4L2_SEL_FLAG_LE`, and `V4L2_SEL_FLAG_KEEP_CONFIG`. `struct v4l2_edid` contains `pad`, `start_block`, `blocks`, five reserved `__u32` fields, and a user pointer `__u8 *edid`. Backward-compatibility aliases map older crop/compose target and subdevice flag names to the common constants.

Control flow: none locally. Drivers and applications use the constants in V4L2 selection ioctls to request current/default/bounds/native rectangles and use `struct v4l2_edid` to read or write EDID block ranges through video device ioctls.

State/persistence behavior: selection values are runtime device or subdevice configuration, and `KEEP_CONFIG` asks the driver not to reconfigure dependent settings while satisfying a requested rectangle constraint. EDID data is transferred through the pointer provided in `v4l2_edid`; reserved fields are ABI padding and should remain zeroed by callers.

Dependencies/integration: depends on `linux/types.h`. It is integrated by V4L2 core headers and must stay source-compatible with both video-node and subdevice users. strace should decode selection target and flag values wherever V4L2 selection or subdevice selection structs appear, and decode `v4l2_edid` pointer/block metadata when handling EDID ioctls.

Risks and test signals: risks are alias drift, mixing crop and compose target ranges, and unsafe decoding of the user pointer inside `struct v4l2_edid`. Tests should cover each target name, flag combinations, old alias names, EDID block count/start values, null and non-null EDID pointers, and reserved fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-controls.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-controls.h

Purpose: declares the V4L2 control ID namespace, menu enumerations, bit flags, and compound control payload structures. The file is the canonical userspace ABI catalog for standard controls, driver-private base ranges, stateful codec controls, stateless codec controls, colorimetry controls, and backward-compatible MPEG aliases that are included by `videodev2.h`.

Important APIs/types/functions: the top-level namespace is organized by `V4L2_CTRL_CLASS_*` values: user, codec, camera, FM TX/RX, flash, JPEG, image source, image processing, DV, RF tuner, detection, stateless codec, and colorimetry. User controls define common video and audio properties such as brightness, contrast, saturation, hue, volume, white balance, gamma, exposure, gain, flips, power-line frequency, color effects, rotation, alpha, and minimum buffers. Driver-private base constants reserve stable ranges for meye, bttv, s2255, si476x, TI VPE, saa7134, adv7180, tc358743, max217x, imx, Atmel ISC, CODA, CCS, Allegro, isl7998x, DW100, Aspeed, NPCM, THP7312, UVC, RKISP1, and Mali-C55.

The codec class contains multiplexed stream, MPEG audio, MPEG video, H.263/H.264/MPEG-4/VP8/VP9/HEVC/AV1 stateful controls, bitrate and profile/level enums, frame skipping, display delay, average QP, and legacy CX2341x and MFC51 driver controls. Camera controls cover exposure, pan/tilt, focus, zoom, privacy, iris, white balance presets, ISO, metering, scene mode, 3A locks, autofocus status/range, orientation, sensor rotation, and HDR sensor mode. Other classes cover RDS FM transmit/receive controls, audio limiter/compression, tuner gains and PLL lock, flash LED/strobe/fault controls, JPEG compression and markers, sensor blanking/gain/test-pattern controls, pixel/link rate, DV HDMI/DVI mode and RGB range, motion detection, and HDR10 metadata.

Compound stateless codec payloads are the densest part of the file. H.264 exports SPS/PPS/scaling matrix/prediction weights/slice/decode parameter structs with DPB entries and reference lists. FWHT exports versioned frame parameters and bit flags. VP8 exports segment, loop filter, quantization, entropy, coder state, and frame structs. MPEG-2 exports sequence, picture, and quantisation structs. HEVC exports SPS, PPS, DPB, prediction weights, slice params, decode params, scaling matrix, and extended short/long-term RPS structs, including dynamic-array control notes. VP9 exports loop filter, quantization, segmentation, frame, motion-vector probability, and compressed-header structs. AV1 exports sequence, tile group entry, global motion, loop restoration, CDEF, segmentation, loop filter, quantization, tile info, frame, and film grain structs. Colorimetry exports HDR10 content light level and mastering display structs.

Control flow: there is no executable control flow in the header. The runtime flow is V4L2 control discovery and use: applications enumerate/query controls, read menu values and bounds, pass scalar values for simple controls, or pass typed compound payloads for stateless codec and HDR metadata controls. Stateful codec controls configure encoder/decoder behavior, while stateless controls provide parsed bitstream syntax for one frame, slice, tile, reference set, or probability update to hardware that does not parse everything itself.

State/persistence behavior: control values live in kernel driver state for an open V4L2 device or subdevice and may affect subsequent streaming, capture, encoding, or decoding. Stateless codec structs are per-request or per-buffer metadata; they often contain reference timestamps that point at `struct v4l2_buffer` timestamps and arrays describing DPB/reference state. Reserved and padding fields are ABI stability fields and should be zeroed. Compatibility aliases such as `V4L2_CTRL_CLASS_MPEG` and `V4L2_CID_MPEG_*` preserve older user-space names while mapping to codec class identifiers.

Dependencies/integration: depends on `linux/const.h` for `_BITUL` and `GENMASK`, and `linux/types.h` for fixed-width ABI types. The header integrates with `videodev2.h`, the V4L2 control framework, media drivers, codec request APIs, and strace's ioctl/control decoders. strace needs value-name tables for control classes, control IDs, enum menus, flags, compound control IDs, and selected nested structs to decode `VIDIOC_QUERYCTRL`, `VIDIOC_QUERY_EXT_CTRL`, `VIDIOC_G_CTRL`, `VIDIOC_S_CTRL`, `VIDIOC_G_EXT_CTRLS`, `VIDIOC_S_EXT_CTRLS`, and request-based codec controls.

Risks and test signals: risks include ID collisions across class base ranges, stale aliases, enum value typos retained for compatibility, architecture-sensitive layout of large compound structs, incorrect handling of `__u64` timestamps, dynamic arrays, nested arrays, and zeroed reserved fields. Stateless codec controls are especially error-prone because many fields mirror external codec specifications and several flags determine which arrays are meaningful. Tests should cover class/id name decoding, menu enum decoding, flag bitsets, legacy MPEG aliases, HDR10 payloads, simple scalar controls, compound control sizes and selected field formatting for H.264/HEVC/VP8/VP9/AV1/FWHT/MPEG-2, and unknown control IDs or future flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/version.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/version.h

Purpose: exposes the bundled Linux kernel version constants used by generated or vendored UAPI headers. It records a version code for Linux 7.1.0 and provides the standard `KERNEL_VERSION(a,b,c)` packing macro.

Important APIs/types/functions: `LINUX_VERSION_CODE` is `459008`, matching `KERNEL_VERSION(7,1,0)`. `KERNEL_VERSION(a,b,c)` shifts major by 16 bits, patchlevel by 8 bits, and clamps sublevel values above 255 to 255. The component macros are `LINUX_VERSION_MAJOR 7`, `LINUX_VERSION_PATCHLEVEL 1`, and `LINUX_VERSION_SUBLEVEL 0`.

Control flow: none at runtime. The macro is compile-time arithmetic used in preprocessor conditionals or C expressions that compare kernel header versions.

State/persistence behavior: no mutable state. The constants are a snapshot of the kernel UAPI version from which this bundled header set was generated.

Dependencies/integration: no includes. strace and its bundled-header generation logic can use these constants to gate version-specific decoders or to report the header baseline.

Risks and test signals: risks are stale version snapshots, incorrect clamping expectations for sublevels greater than 255, and mismatches between this bundled version and individual header content. Tests should verify `LINUX_VERSION_CODE == KERNEL_VERSION(7,1,0)`, major/patchlevel/sublevel parsing, and macro clamping behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/version.h -->
