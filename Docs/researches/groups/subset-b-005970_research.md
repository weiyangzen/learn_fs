# Research: subset-b-005970

Grouped research for DRM UAPI headers under `sources/distributed-fs/ceph-client/include/uapi/drm`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_fourcc.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/drm_fourcc.h

## Purpose

`drm_fourcc.h` is the DRM UAPI registry for framebuffer pixel format FourCC values and format modifiers. It defines the stable identifiers that user space, KMS, GEM/GBM, EGL, Vulkan WSI, display controllers, GPUs, media blocks, and DMA-BUF import/export paths use to agree on buffer component order, plane layout, tiling, compression, endian handling, and vendor-specific memory layout. The file is a protocol catalog rather than executable code: changing a constant changes ABI expectations across kernel drivers and user-space graphics stacks.

The header's high-level contract is that a `DRM_FORMAT_*` code plus an optional `DRM_FORMAT_MOD_*` modifier must uniquely describe the buffer layout. The comments explicitly warn against aliases and pitch-alignment-only modifiers because userspace commonly intersects opaque format/modifier pairs across producers and consumers.

## Important APIs, Types, And Constants

- `fourcc_code(a, b, c, d)` packs four ASCII bytes into a little-endian `__u32` format code. `DRM_FORMAT_BIG_ENDIAN` marks big-endian variants, and `DRM_FORMAT_INVALID` reserves zero.
- `DRM_FORMAT_*` constants cover indexed formats (`C1`/`C2`/`C4`/`C8`), darkness/monochrome formats, single-channel red formats, RG/RGBA/RGB/BGR packed formats, high-bit-depth integer and floating formats, packed YCbCr, semi-planar and planar YUV families, packed 10/12/16-bit video formats, and vendor/media-specific YUV layouts.
- `DRM_FORMAT_MOD_VENDOR_*` and `fourcc_mod_code(vendor, val)` namespace 64-bit modifiers by vendor. `DRM_FORMAT_MOD_INVALID` and `DRM_FORMAT_MOD_LINEAR` cover no-valid-modifier and linear layout.
- Intel/i915 modifiers describe X/Y/Yf/Tile4 tiling, Gen12/DG2/MTL CCS compression planes, clear-color surfaces, and modifier-specific pitch/plane rules.
- NVIDIA, Broadcom, Arm, Allwinner, Amlogic, MediaTek, Apple, and AMD sections encode vendor layouts. Notable macro families include `DRM_FORMAT_MOD_NVIDIA_*`, Broadcom SAND helpers, Arm `DRM_FORMAT_MOD_ARM_AFBC()` / AFBC feature bits / AFRC coding-unit bits, Amlogic FBC layout/options, `DRM_FORMAT_MOD_MTK()`, Apple tiled/compressed modifiers, and AMD `AMD_FMT_MOD_SET/GET/CLEAR`.

## Control Flow And Data Flow

There are no functions or runtime branches. The header participates in flows where userspace chooses or queries a pixel format and modifier, allocates/imports a buffer, then passes the same pair to DRM ioctls such as `ADDFB2`, plane property blobs, DMA-BUF negotiation, EGL/GBM allocation, or Vulkan image creation. Kernel drivers compare the numeric constants against their supported lists and validate pitches, offsets, plane counts, and modifier-specific alignment.

The implicit data flow is producer to consumer: a rendering/media producer advertises a DMA-BUF plus FourCC/modifier metadata; a display, GPU, or codec importer accepts only pairs it supports. Modifier comments define whether extra planes represent compression metadata, clear color, or implicit side storage, so user space must not infer layout solely from the base FourCC.

## State And Persistence Behavior

The file defines persistent ABI tokens. Numeric values are long-lived and must remain stable across kernel releases, userspace libraries, and recorded buffer metadata. It does not allocate memory, hold state, or persist runtime data. The state risk is semantic persistence: once a format/modifier is published, aliases, repurposing, or changed plane interpretation can break cross-driver sharing.

## Dependencies

The header depends on `drm.h` for fixed-width UAPI types. Some helper macros use Linux integer conventions such as `__u32` and `__u64`. It is consumed by `drm_mode.h` framebuffer structures, driver-specific UAPI headers that accept FourCC/modifier pairs, Mesa/GBM/EGL/Vulkan integration layers, and display/media drivers.

## Integration Points

Key integration points are `struct drm_mode_fb_cmd2.pixel_format`, `struct drm_mode_fb_cmd2.modifier[]`, `struct drm_format_modifier_blob`, plane `IN_FORMATS` property blobs, DMA-BUF format negotiation, and driver-specific image-processing APIs such as Exynos IPP. Vendor-specific sections connect to i915, nouveau/NVIDIA-compatible consumers, vc4/v3d/Broadcom, Arm Mali/AFBC/AFRC, Allwinner VPU, Amlogic codecs, MediaTek display/video blocks, Apple GPU, and AMD display/render compression.

## Risks And Edge Cases

- ABI stability is critical: changing numeric values or deleting constants breaks existing binaries.
- Modifier aliasing can silently prevent sharing when two drivers describe the same layout differently.
- Multi-plane formats can be misleading because a modifier may change the required number of planes or place metadata in separate planes despite the base FourCC.
- Some modifiers describe non-mappable or producer-private layouts, such as Amlogic scatter FBC, so tests must not assume CPU mapping works for every DMA-BUF.
- AMD and Arm modifiers pack many fields into bit ranges; incorrect masks or shifts lead to accepting incompatible tiling/compression.
- Endianness, component order, and alpha/x padding are easy to confuse because names encode memory order rather than abstract color order.

## Test Signals

Useful checks include compile/UAPI header selftests, ABI-diff checks that constants do not change, KMS `ADDFB2` validation for representative RGB/YUV formats, modifier round-trip tests through `IN_FORMATS`, DMA-BUF import/export tests across producer/consumer drivers, GBM/EGL/Vulkan format enumeration tests, and negative tests for invalid modifier/format combinations, plane counts, pitches, offsets, and unsupported CPU mmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_fourcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_mode.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/drm_mode.h

## Purpose

`drm_mode.h` defines the UAPI data model for DRM/KMS mode setting. It exposes display mode timings, CRTC/encoder/connector/plane discovery, framebuffer creation and dirty tracking, cursor movement, gamma/color pipelines, HDR metadata, page flips, dumb buffers, atomic commits, format modifier blobs, blob properties, leases, damage rectangles, and ARGB helper macros. It is the central user-kernel ABI for display servers, compositors, test tools, and graphics libraries that drive KMS.

## Important APIs, Types, And Constants

- Mode description: `struct drm_mode_modeinfo` plus `DRM_MODE_TYPE_*`, sync/scan/stereo/aspect flags, content type, DPMS, scaling, dithering, dirty, link status, panel type, rotation/reflection, and content-protection constants.
- Resource discovery: `struct drm_mode_card_res`, `drm_mode_get_connector`, `drm_mode_get_encoder`, `drm_mode_get_plane`, and `drm_mode_get_plane_res`.
- Object property ABI: property flags (`RANGE`, `ENUM`, `BLOB`, `BITMASK`, `OBJECT`, `SIGNED_RANGE`, `ATOMIC`), `drm_mode_get_property`, `drm_mode_obj_get_properties`, `drm_mode_obj_set_property`, `drm_mode_property_enum`, and object type IDs for CRTCs/connectors/encoders/FBs/planes/blobs/colorops.
- Framebuffers and planes: legacy `drm_mode_fb_cmd`, modern `drm_mode_fb_cmd2`, dirty clips, `drm_format_modifier_blob`, and `drm_format_modifier`.
- CRTC operations: `drm_mode_crtc`, `drm_mode_set_plane`, cursor structs, LUT structs, `drm_mode_crtc_page_flip`, and `drm_mode_crtc_page_flip_target`.
- Color/HDR: `drm_color_ctm`, `drm_color_ctm_3x4`, `drm_color_lut`, `drm_color_lut32`, color operation enums, LUT interpolation enums, `hdr_metadata_infoframe`, and `hdr_output_metadata`.
- Buffer and blob management: `drm_mode_create_dumb`, `drm_mode_map_dumb`, `drm_mode_destroy_dumb`, `drm_mode_create_blob`, `drm_mode_destroy_blob`, and `drm_mode_closefb`.
- Atomic and leasing: `drm_mode_atomic`, `DRM_MODE_ATOMIC_*` flags, `drm_mode_create_lease`, `drm_mode_list_lessees`, `drm_mode_get_lease`, and `drm_mode_revoke_lease`.
- ARGB helpers: `DRM_ARGB64_PREP*` and `DRM_ARGB64_GET*` pack/unpack 16-bit component values with optional bit-depth conversion.

## Control Flow And Data Flow

The file models several ioctl flows. Discovery usually starts with count-first calls: userspace calls resource, connector, plane, or property ioctls with zero counts or temporary storage, allocates arrays sized by returned counts, then retries. Connector probing can force slow hotplug/EDID refresh when `count_modes` is zero and the caller is DRM master.

Legacy modesetting flows create a GEM/dumb buffer, create an FB, set a CRTC or plane, then page-flip to a new FB. Atomic flows create blob properties for modes, HDR metadata, LUTs, or damage, populate arrays of object IDs, property counts, property IDs, and values in `struct drm_mode_atomic`, optionally run `TEST_ONLY`, then commit blocking or nonblocking with optional vblank events.

Format modifier data flows from plane `IN_FORMATS` blobs into framebuffer creation through `drm_mode_fb_cmd2.pixel_format` and `modifier[]`. Lease flows create a new DRM master FD with a subset of object IDs, and later list, inspect, or revoke that lease.

## State And Persistence Behavior

The header itself has no runtime state, but it defines handles for kernel-managed persistent objects: framebuffer IDs, blob IDs, leased master IDs, GEM handles, CRTC/connector/encoder/plane object IDs, and property IDs. User-created blobs persist until destroyed or FD cleanup. Framebuffers can be closed separately from last display use via `CLOSEFB`; dumb buffers persist as GEM objects until destroyed/closed. Atomic commits may be asynchronous, so userspace state must track event completion and object lifetimes carefully.

## Dependencies

It includes `<linux/bits.h>`, `<linux/const.h>`, and `drm.h`. It references FourCC/modifier definitions from `drm_fourcc.h` by contract, even though it does not include that file directly in this copy. It integrates with generic DRM ioctl numbering in `drm.h`, KMS core object/property semantics, and userspace libraries such as libdrm, Mesa GBM, wlroots, Xorg modesetting, Weston, mutter, KWin, and IGT.

## Integration Points

This header is the display ABI shared by all KMS drivers. Driver-specific headers rely on its format, rotation, event, and framebuffer conventions. The `drm_event_vblank` / flip-complete event path comes from `drm.h`; format modifier definitions come from `drm_fourcc.h`; driver GEM handles are passed through framebuffer and dumb-buffer paths. Color-management and HDR property blobs connect display server policy to hardware-specific color pipelines.

## Risks And Edge Cases

- Count-first enumeration is racy around hotplug; callers must retry until counts stabilize.
- Forced connector probing can block and flicker, so it should only happen on startup, hotplug, or explicit request.
- `drm_mode_fb_cmd2` supports up to four planes but all modifier entries must be identical for a framebuffer; unused entries must be zero, while zero can also be a valid offset or linear modifier.
- Atomic commits require correct object/property array packing. Missing `ALLOW_MODESET` or incorrect event CRTC inclusion can return errors that compositors must handle.
- Asynchronous page flips can tear and are driver-dependent; the first async transition may still be synchronous.
- Blob lifetimes are subtle: blobs may be destroyed after commit submission when not reused, but user space must not reuse destroyed IDs.
- Fixed-point source coordinates, sign-magnitude CTM values, HDR unit scaling, and ARGB bit-depth conversion are easy places for off-by-one or sign mistakes.

## Test Signals

Relevant tests include IGT KMS discovery, hotplug retry, connector force-probe, atomic `TEST_ONLY` and commit coverage, legacy and atomic page-flip event timing, dumb-buffer create/map/destroy, framebuffer modifier validation, plane format blob parsing, property enumeration, color LUT/CTM/HDR blob validation, lease create/revoke/list behavior, damage clip handling, and ABI compile checks on 32-bit and 64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_ras.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/drm_ras.h

## Purpose

`drm_ras.h` is an auto-generated YNL UAPI header for the `drm-ras` generic netlink family. It defines a small reliability, availability, and serviceability interface for discovering DRM RAS nodes and reading error counters associated with hardware or software components.

## Important APIs, Types, And Constants

- `DRM_RAS_FAMILY_NAME` is `drm-ras`; `DRM_RAS_FAMILY_VERSION` is `1`.
- `enum drm_ras_node_type` currently defines `DRM_RAS_NODE_TYPE_ERROR_COUNTER`.
- Node attributes include `NODE_ID`, `DEVICE_NAME`, `NODE_NAME`, and `NODE_TYPE`.
- Error-counter attributes include `NODE_ID`, `ERROR_ID`, `ERROR_NAME`, and `ERROR_VALUE`.
- Commands are `DRM_RAS_CMD_LIST_NODES` and `DRM_RAS_CMD_GET_ERROR_COUNTER`, with max sentinels for generated netlink policy handling.

## Control Flow And Data Flow

The intended flow is netlink-based. Userspace opens the generic netlink family, sends `LIST_NODES`, receives node records that identify devices/components and node types, then sends `GET_ERROR_COUNTER` for a node/error ID to retrieve a named counter value. The header does not implement policy or marshaling; generated YNL and kernel netlink code use the enum IDs to encode and decode messages.

## State And Persistence Behavior

The header has no local state. RAS counter values are maintained by kernel DRM drivers or subsystems and are read through netlink. Counter persistence is implementation-defined: the comments only define exposure of reliability counters, not reset semantics, monotonicity, or lifetime across device reset/driver reload.

## Dependencies

This header is generated from `Documentation/netlink/specs/drm_ras.yaml` and is expected to stay in sync with the YNL spec. It uses plain enum constants and does not include other headers in this copy. Runtime integration depends on Linux generic netlink, YNL-generated helpers, and DRM drivers that register RAS nodes.

## Integration Points

It integrates with user-space monitoring tools, telemetry collectors, driver diagnostics, and kernel DRM RAS providers. Unlike the ioctl-heavy DRM headers in this subset, this is a netlink control plane suitable for enumerating counters across DRM devices/components.

## Risks And Edge Cases

- Because it is generated, manual edits risk being lost or diverging from `drm_ras.yaml`.
- Only one node type is currently defined; user space should reject or ignore unknown future node types gracefully.
- Counter size and reset behavior are not described here; monitoring code must not assume a specific persistence model beyond the `ERROR_VALUE` field name.
- Attribute and command enum values are ABI-relevant for netlink compatibility.

## Test Signals

Useful signals include YNL regeneration diffs, generic netlink family discovery, schema/policy validation against `drm_ras.yaml`, list-node calls on systems with and without providers, get-counter calls for valid and invalid node/error IDs, and compatibility tests that older userspace ignores future attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_sarea.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/drm_sarea.h

## Purpose

`drm_sarea.h` defines the legacy DRM shared area (SAREA) ABI used by older direct-rendering drivers. SAREA is a shared memory page or architecture-sized area containing hardware locks, drawable metadata, frame dimensions, and a dummy context. Modern KMS/GEM paths generally do not use it, but the structure remains UAPI for compatibility with old DRI clients and drivers.

## Important APIs, Types, And Constants

- `SAREA_MAX` selects the shared area size by architecture: 8 KiB on most systems and Alpha, 16 KiB on MIPS, and 64 KiB on IA-64.
- `SAREA_MAX_DRAWABLES` is 256; `SAREA_DRAWABLE_CLAIMED_ENTRY` marks a drawable table entry.
- `struct drm_sarea_drawable` stores a drawable stamp and flags.
- `struct drm_sarea_frame` stores x/y/width/height/fullscreen state.
- `struct drm_sarea` embeds `struct drm_hw_lock lock`, `struct drm_hw_lock drawable_lock`, a drawable table, a frame, and `drm_context_t dummy_context`.
- Non-kernel typedefs expose legacy `_t` aliases.

## Control Flow And Data Flow

The header only defines shared-memory layout. Legacy userspace maps the SAREA, coordinates with the kernel and other clients through `drm_hw_lock`, updates or reads drawable/frame records, and uses stamps/flags to synchronize drawable ownership or validity. The first field must remain the DRM lock so old lock-handling code can interpret the mapped region.

## State And Persistence Behavior

SAREA contents are mutable shared process/kernel state while the DRM device and mapping exist. It does not persist across driver unload, device close, or process lifetime. Lock fields and drawable table entries are concurrency-sensitive and can be stale if a client exits or if old DRI paths mishandle lock release.

## Dependencies

The header includes `drm.h` for `struct drm_hw_lock` and `drm_context_t`. It is tied to legacy DRM locking/context APIs and old DRI driver/user-space expectations.

## Integration Points

Integration points are old direct-rendering stacks and drivers that still expose or understand SAREA. It is not the modern integration path for GEM, KMS atomic modesetting, dma-fence, or DRM syncobj. Compatibility is its main reason to remain in the tree.

## Risks And Edge Cases

- Architecture-dependent `SAREA_MAX` must match old userspace assumptions.
- Shared locks can deadlock or leak ownership if a legacy client fails while holding a lock.
- The fixed 256-entry drawable table can overflow logical drawable needs; callers need external allocation or fallback behavior.
- ABI layout changes would break mapped-memory clients because fields are read directly from shared memory.
- The header uses legacy typedefs and comments that do not describe modern memory-ordering requirements.

## Test Signals

Signals are mostly compatibility checks: compile UAPI for 32/64-bit, verify `sizeof(struct drm_sarea)` fits `SAREA_MAX` for supported architectures, run any legacy DRI/SAREA users if present, validate lock offset assumptions, and ensure no modern changes reorder fields or alter legacy typedef visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/drm_sarea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/ethosu_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/ethosu_accel.h

## Purpose

`ethosu_accel.h` defines the DRM accelerator UAPI for Arm Ethos-U NPUs. It provides ioctls for querying device/NPU information, creating regular and command-stream GEM buffer objects, waiting on buffer fences, retrieving mmap offsets, and submitting NPU jobs that reference command streams and memory regions.

## Important APIs, Types, And Constants

- `enum drm_ethosu_ioctl_id` allocates stable command IDs: `DEV_QUERY`, `BO_CREATE`, `BO_WAIT`, `BO_MMAP_OFFSET`, `CMDSTREAM_BO_CREATE`, and `SUBMIT`.
- `enum drm_ethosu_dev_query_type` currently exposes `DRM_ETHOSU_DEV_QUERY_NPU_INFO`.
- `struct drm_ethosu_npu_info` returns `id`, `config`, and `sram_size`, with macros to decode architecture/product/version/status fields.
- `struct drm_ethosu_dev_query` implements extensible size/pointer querying: NULL pointer returns size; non-NULL copies `min(size, actual)`.
- `struct drm_ethosu_bo_create`, `drm_ethosu_bo_mmap_offset`, and `drm_ethosu_bo_wait` define GEM allocation, mmap offset lookup, and absolute-timeout waiting. `DRM_ETHOSU_BO_NO_MMAP` prevents userspace CPU mapping.
- `struct drm_ethosu_cmdstream_bo_create` creates command-stream BOs from a user data pointer.
- `struct drm_ethosu_job` references one command-stream BO, requested SRAM, and up to `ETHOSU_MAX_REGIONS` region BO handles. `struct drm_ethosu_submit` passes an array of jobs.
- `DRM_IOCTL_ETHOSU()` builds ioctl numbers over `DRM_COMMAND_BASE`; the enum at the end exposes concrete `DRM_IOCTL_ETHOSU_*` numbers.

## Control Flow And Data Flow

Typical userspace flow is: query NPU info, create memory BOs for tensors/regions, create a command-stream BO from command data, optionally request mmap offsets for mappable BOs, submit an array of jobs, and wait for BO completion through the BO wait ioctl. Jobs in a single `drm_ethosu_submit` are scheduled by the kernel with dependency awareness, while tasks within a job execute sequentially on the same core to reuse SRAM residency.

Command data flows from userspace to a kernel GEM object, then job submissions refer to BO handles rather than raw pointers. Region BO handles connect command stream address regions to backing memory.

## State And Persistence Behavior

Kernel GEM BO handles persist for the DRM file lifetime or until closed. Command-stream BOs are also GEM handles. Submit operations create scheduled work and fences associated with affected BOs; `BO_WAIT` observes the last submit completion for a BO. Device query information is read-only runtime state. SRAM use is per job and managed by the scheduler, not persisted in the header.

## Dependencies

The header includes `drm.h` and uses DRM ioctl macros and fixed-width UAPI types. It integrates with DRM accel/GEM infrastructure, mmap fake-offset handling, scheduler/fence logic, and the Ethos-U kernel driver.

## Integration Points

User-space ML runtimes, inference delegates, or driver libraries use this ABI to allocate tensors, upload command streams, and schedule inference jobs. The file sits beside DRM driver UAPIs but is NPU-focused rather than display-focused. GEM BO handles can potentially integrate with dma-buf sharing depending on the driver.

## Risks And Edge Cases

- Ioctl IDs are explicitly append-only; reordering/removal breaks ABI.
- Query structs are extensible only if old userspace honors the `size`/`pointer` protocol.
- `timeout_ns` is absolute, so callers need a correct monotonic time basis.
- `DRM_ETHOSU_BO_NO_MMAP` means mmap offset requests should reject or avoid non-mappable BOs.
- `ETHOSU_MAX_REGIONS` is fixed at 8; command streams needing more regions must be rejected or split.
- Job arrays and command-stream data are user pointers, so kernel validation must defend against invalid sizes, null pointers, stale BO handles, and region mismatches.

## Test Signals

Tests should cover ioctl numbering, query size negotiation with old/new struct sizes, BO create page alignment and flags validation, mmap offset success/failure for mappable and no-mmap BOs, command-stream BO creation from invalid and valid data pointers, submit with zero/one/multiple jobs, invalid region handles, SRAM limit validation, fence/wait timeout behavior, and 32-bit userspace pointer compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/ethosu_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/etnaviv_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/etnaviv_drm.h

## Purpose

`etnaviv_drm.h` defines the DRM UAPI for Etnaviv Vivante GPU drivers. It exposes GPU parameter queries, GEM buffer allocation and mapping, CPU/GPU synchronization, command-stream submission with relocation or softpin support, explicit fence fd integration, userptr import, buffer waits, and performance monitor domain/signal enumeration.

## Important APIs, Types, And Constants

- ABI notes at the top require `__u64` instead of pointers, natural alignment, and append-only struct extension with zero-compatible defaults.
- `struct drm_etnaviv_timespec` is a 32/64-bit-safe monotonic absolute timeout.
- `ETNAVIV_PARAM_*` constants query GPU model, revision, feature words, stream/register/thread/cache/shader/pixel/constant/varying capabilities, softpin start address, product/customer/ECO IDs, and more.
- GEM types include `drm_etnaviv_gem_new`, `drm_etnaviv_gem_info`, `drm_etnaviv_gem_cpu_prep`, `drm_etnaviv_gem_cpu_fini`, `drm_etnaviv_gem_userptr`, and `drm_etnaviv_gem_wait`.
- Submit structures include reloc entries (`drm_etnaviv_gem_submit_reloc`), BO table entries (`drm_etnaviv_gem_submit_bo`), performance monitor requests (`drm_etnaviv_gem_submit_pmr`), and the top-level `drm_etnaviv_gem_submit`.
- Submit flags include no implicit sync, fence fd input/output, and softpin. Pipes are 3D, 2D, and VG.
- Wait and PM structs include `drm_etnaviv_wait_fence`, `drm_etnaviv_pm_domain`, and `drm_etnaviv_pm_signal`.
- Ioctl constants cover get-param, GEM new/info/cpu-prep/cpu-fini/submit/userptr/wait, wait-fence, and PM query domain/signal.

## Control Flow And Data Flow

Userspace first queries per-pipe parameters, creates GEM buffers, retrieves mmap offsets, and uses CPU prep/fini to synchronize CPU access. Command submission passes a BO table, relocation list, command stream pointer, optional PM read requests, and optional fence fd. For reloc-based submissions, relocation entries must be sorted by increasing `submit_offset`; the kernel patches command-stream addresses from referenced BO GPU addresses. For softpin submissions, `presumed` is interpreted as the fixed GPU virtual address and userspace manages the GPU VA layout.

Fence flow can be implicit through BO dependencies or explicit via `ETNA_SUBMIT_FENCE_FD_IN` and `ETNA_SUBMIT_FENCE_FD_OUT`. Wait ioctls block or poll on fence sequence numbers or BO readiness using absolute monotonic timeouts.

## State And Persistence Behavior

GEM handles persist for the DRM file lifetime; userptr handles pin user memory while valid. The kernel tracks GPU virtual mappings, fences, command sequence numbers, performance monitor readbacks, and CPU-prep synchronization state. `presumed` BO addresses are in/out hints that userspace may cache across submits, but they can become invalid unless softpin fixes them.

## Dependencies

The header includes `drm.h` and relies on DRM GEM, scheduler/fence, mmap-offset, dma-fence/sync-file, and Etnaviv GPU MMU/command parser support. It uses fixed-width UAPI types to maintain 32/64-bit compatibility.

## Integration Points

Mesa's Etnaviv Gallium driver is the primary userspace consumer. The UAPI integrates with DRM render nodes, GEM buffer sharing, explicit sync fence fds, CPU cache management, performance monitoring, and GPU pipe selection for 2D/3D/VG engines.

## Risks And Edge Cases

- Relocations must be sorted; unsorted entries should return `EINVAL`.
- Softpin shifts address-space ownership to userspace and can fail if the requested VA is unavailable.
- Cache flags (`CACHED`, `WC`, `UNCACHED`) and CPU prep/fini must be honored to avoid stale CPU/GPU data.
- Absolute timeouts require consistent monotonic timestamps.
- Userptr import requires page alignment and careful pin/unpin handling.
- Append-only struct extension requires zero values to remain backward-compatible.
- Fence sequence numbers are per pipe and should not be confused across engines.

## Test Signals

Tests should cover get-param for every supported pipe, GEM allocation flags and mmap offset, CPU prep/fini read/write/no-sync paths, submit with valid and invalid BO tables, unsorted reloc rejection, softpin collision/failure, explicit fence fd in/out behavior, wait-fence and GEM-wait timeout/nonblock status, userptr alignment validation, PM domain/signal enumeration, and 32-bit userspace ABI layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/etnaviv_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/exynos_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/exynos_drm.h

## Purpose

`exynos_drm.h` defines Samsung Exynos DRM driver-specific UAPI for GEM buffer creation/mapping/query, virtual display connection, legacy G2D command submission, and IPP v2 image post-processing. It bridges Exynos-specific memory and image-processing hardware to generic DRM concepts such as GEM handles, FourCC formats, modifiers, rotation flags, and DRM events.

## Important APIs, Types, And Constants

- GEM structs: `drm_exynos_gem_create`, `drm_exynos_gem_map`, and `drm_exynos_gem_info`.
- GEM memory flags: contiguous/non-contiguous, cacheable/non-cacheable, write-combine, and `EXYNOS_BO_MASK`.
- VIDI: `drm_exynos_vidi_connection` supplies connection state, EDID extension flag, and EDID pointer.
- G2D: version, command, userptr, command-list, and exec structs (`drm_exynos_g2d_get_ver`, `drm_exynos_g2d_cmd`, `drm_exynos_g2d_userptr`, `drm_exynos_g2d_set_cmdlist`, `drm_exynos_g2d_exec`) plus event type constants.
- IPP v2: resource enumeration (`drm_exynos_ioctl_ipp_get_res`), capabilities/formats (`drm_exynos_ioctl_ipp_get_caps`, `drm_exynos_ipp_format`), limits (`drm_exynos_ioctl_ipp_get_limits`, `drm_exynos_ipp_limit`), task chunks for buffer/rectangle/transform/alpha, and commit (`drm_exynos_ioctl_ipp_commit`).
- IPP flags include event generation, test-only validation, and nonblocking execution.
- Ioctl constants define GEM, VIDI, G2D, and IPP operations. Events include `DRM_EXYNOS_G2D_EVENT` and `DRM_EXYNOS_IPP_EVENT` with event payload structs.

## Control Flow And Data Flow

GEM flow creates a BO with memory/cache flags, maps it through a fake offset, or queries its size/flags. VIDI flow lets userspace report virtual connector connection state and optional EDID data. G2D flow queries hardware version, sends a command list and buffers/userptrs, then executes synchronously or asynchronously with optional event delivery.

IPP v2 flow is discovery-driven: enumerate IPP modules, query each module's supported source/destination formats and capabilities, query limits for a FourCC/modifier/type pair, then commit a packed parameter array. The commit array contains typed task chunks for source/destination buffers, rectangles, transformations using DRM rotation/reflection values, and alpha. `TEST_ONLY` validates without execution; `NONBLOCK` and `EVENT` switch completion signaling to DRM events.

## State And Persistence Behavior

GEM handles and mmap offsets persist for the DRM file/object lifetime. VIDI connection state affects the virtual display connector until changed or the driver/device resets. G2D and IPP commits create transient hardware jobs; event structs carry user data, timestamps, and sequence/cmdlist identifiers. IPP resource/capability state is queried from driver hardware state and may vary by SoC.

## Dependencies

The header includes `drm.h`. It depends on `drm_fourcc.h` for format codes/modifiers by contract and on `drm_mode.h` rotation/reflection constants for IPP transforms. Runtime support depends on Exynos GEM memory backends, G2D, VIDI, IPP hardware, and DRM event delivery.

## Integration Points

Consumers include Exynos-specific display/media libraries, Mesa or libdrm helper code, test tools, and compositors/media pipelines using IPP for scaling, rotation, crop, conversion, or alpha. IPP buffer descriptors intentionally mirror `ADDFB2` plane fields (`gem_id`, `offset`, `pitch`, `modifier`) to align with generic DRM framebuffer semantics.

## Risks And Edge Cases

- Some structs use `unsigned long` in `drm_exynos_g2d_userptr`, which is a 32/64-bit ABI compatibility hazard compared with the `__u64` style used elsewhere.
- Pointer fields in command/IPP arrays require careful copy-from-user size validation.
- GEM cache/memory flags can be invalid or unsupported on particular SoCs.
- IPP task arrays are self-describing by `id` bits; malformed ordering, duplicated chunks, missing source/destination chunks, or mismatched FourCC/modifier fields should fail.
- `TEST_ONLY` must not mutate hardware state.
- Event `user_data` and sequence/cmdlist identifiers must be preserved for asynchronous clients.

## Test Signals

Tests should cover GEM create/map/get flag validation, VIDI connect/disconnect and EDID extension handling, G2D version and command-list validation, async G2D event delivery, IPP resource/caps/limits two-call enumeration, IPP test-only commits, valid and invalid task arrays, rotation/reflection support, FourCC/modifier rejection, nonblocking/event completion, and 32-bit compat behavior for `unsigned long` userptr fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/exynos_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/habanalabs_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/habanalabs_accel.h

## Purpose

`habanalabs_accel.h` defines the DRM accelerator UAPI for Intel/Habana Labs AI accelerators such as Goya, Gaudi, Gaudi2, and later devices. It exposes queue and engine identifiers, device information and telemetry, command-buffer lifecycle, command submission, waits and interrupts, device/host memory mapping, DMA-BUF export, timestamp pools, debug/profile configuration, security attestation, and event/error reporting.

## Important APIs, Types, And Constants

- Device topology constants enumerate queue IDs for Goya, Gaudi, and Gaudi2, plus engine IDs per ASIC generation. Reserved SRAM offsets, sync-object/monitor bases, and timestamp pool limits define device-specific resource ranges.
- `HL_INFO_*` operations cover hardware IP info, events, DRAM usage, idle/busy engines, status/utilization, clocks, reset counts, time sync, CS/PCI counters, throttling, sync managers, energy/power, open stats, DRAM row repair, timeout/RAZWI/page-fault/error events, user mappings, firmware generic requests, eventfd registration, secured attestation, and device signing.
- Info structs include `hl_info_hw_ip_info`, telemetry/counter structs, error-event structs, `hl_info_sec_attest`, `hl_info_signed`, `hl_page_fault_info`, `hl_user_mapping`, and top-level `hl_info_args`.
- Command buffers use `HL_CB_OP_CREATE`, `DESTROY`, and `INFO`, with `HL_MAX_CB_SIZE`, map/get-device-VA flags, `hl_cb_in`, `hl_cb_out`, and `union hl_cb_args`.
- Command submissions use `hl_cs_chunk`, `hl_cs_in`, `hl_cs_out`, and `union hl_cs_args`. Flags cover force-restore, signal/wait/collective wait, timestamps, staged submission, custom timeout, skip reset on timeout, encapsulated signals, reserve/unreserve signals, engine-core commands, flush PCI HBW writes, and engines commands.
- Waits use `hl_wait_cs_in/out`, multi-CS lists, interrupt waits, kernel CQ interrupt waits, timestamp registration, and status/flag constants.
- Memory uses `HL_MEM_OP_ALLOC/FREE/MAP/UNMAP/MAP_BLOCK/EXPORT_DMABUF_FD/TS_ALLOC`, memory flags, `hl_mem_in/out`, and `union hl_mem_args`.
- Debug/profile structs configure ETR/ETF/STM/FUNNEL/BMON/SPMU/timestamp/debug mode through `hl_debug_args`.
- Concrete ioctls are `DRM_IOCTL_HL_INFO`, `DRM_IOCTL_HL_CB`, `DRM_IOCTL_HL_CS`, `DRM_IOCTL_HL_WAIT_CS`, `DRM_IOCTL_HL_MEMORY`, and `DRM_IOCTL_HL_DEBUG`, spanning `HL_COMMAND_START` through `HL_COMMAND_END`.

## Control Flow And Data Flow

The normal runtime flow starts with `HL_INFO_HW_IP_INFO` and related queries to learn memory ranges, enabled engines, firmware versions, interrupts, page sizes, security state, and limits. Userspace allocates or maps device/host memory through `HL_MEMORY`, creates command buffers through `HL_CB` or uses user-allocated command buffers, then submits jobs through `HL_CS`. A CS contains restore and execution chunks targeted at queue IDs; the ioctl enqueues work asynchronously and returns sequence numbers or signal handles. Completion is observed through `HL_WAIT_CS`, multi-CS waits, interrupt waits, eventfd registration, or timestamp buffers.

Memory data can flow from host allocations pinned into the device MMU, device DRAM allocations mapped into device VA space, HW block mappings for configuration access, and exported DMA-BUF FDs for sharing with importer drivers. Debug data flows through trace sink/source configuration after a process enters exclusive debug mode. Error and RAS-like data flows through `HL_INFO_*` event records that snapshot page faults, RAZWI accesses, undefined opcodes, hardware errors, firmware errors, and engine errors.

## State And Persistence Behavior

The kernel maintains per-file/context state for command buffers, command submissions, sequence numbers, signal reservations, device/host memory mappings, timestamp pools, eventfd registrations, debug-mode ownership, and open statistics. Device-level state includes firmware/device status, clocks, reset counters, DRAM usage, error history, row-repair state, and security attestation/signing material. Many info records are snapshots; several event records explicitly allow a successful call with timestamp zero when no new data is available. Memory allocations and mappings persist until freed/unmapped or context close; timestamp allocation is freed on FD/context close.

## Dependencies

The header includes `<drm/drm.h>` and relies on Linux UAPI helpers such as `BIT`, `SZ_1M`, and fixed-width integer types as provided through the kernel UAPI include environment. Runtime integration depends on the Habana Labs DRM accel driver, device firmware/CPUCP, MMU, queues, sync manager, dma-buf, eventfd, interrupts, and debug/profile hardware blocks.

## Integration Points

Primary consumers are Habana/Intel accelerator runtime libraries, training/inference frameworks through those runtimes, monitoring tools, profilers, and diagnostic utilities. It integrates with DRM render-node ioctl dispatch, DMA-BUF sharing, eventfd-based notification loops, firmware request channels, secure attestation workflows, and system telemetry/health monitoring.

## Risks And Edge Cases

- The header is large and generation-specific; queue/engine IDs are ABI tokens and must not be renumbered.
- Command submission sequencing is not globally ordered in the simple way users might expect; completion of sequence N does not imply N-1 completed unless the submissions are equivalent as documented.
- Internal jobs on older generations can continue after external queue completion, so wait semantics can be surprising.
- Many unions depend on `op`/flag fields; kernels must validate that only relevant union members and sizes are used.
- Host memory mapping pins user pages and can hit OS pin limits; hint addresses may not be honored and callers must check returned addresses.
- DMA-BUF export address semantics differ for Gaudi1 versus later ASICs.
- Debug mode is exclusive and affects other users; failure to exit debug mode or abuse can block work.
- Error info calls may return timestamp zero for no data, so monitoring must distinguish no-event from a valid event.
- Security attestation buffers are fixed-size and must be length-checked carefully.
- Duplicate macro definitions and deprecated paths, such as timestamp debug opcode, are compatibility signals rather than new API patterns.

## Test Signals

Important tests include UAPI compile/layout checks on 32-bit and 64-bit, info query size/copy bounds, hardware IP info sanity per ASIC, eventfd register/unregister and event retrieval, CB create/map/info/destroy including max-size rejection, CS submission for restore/execution/staged/signal/wait/collective/engine-command paths, wait status for completed/busy/timed-out/aborted/multi-CS/interrupt modes, memory alloc/free/map/unmap/map-block/export/TS allocation, hint address handling, DMA-BUF export/import, debug-mode exclusivity and trace configuration, reset/error event reporting, security attestation output size validation, and negative tests for invalid queue IDs, stale handles, bad flags, and device reset races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/habanalabs_accel.h -->
