# Research Group subset-b-003787

Source-tree-aligned grouped research for subset B work item `subset-b-003787`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.c

## Purpose

`xe_wait_user_fence.c` implements the Xe DRM ioctl that blocks userspace until a 64-bit user-memory fence satisfies a comparison. It is the software wait side of Xe user fences, with optional association to an execution queue so waits fail if that queue resets.

## Important APIs, Types, And Functions

The exported entry point is `xe_wait_user_fence_ioctl()`. Helpers are `do_compare()`, which copies the 64-bit value from userspace and evaluates `EQ`, `NEQ`, `GT`, `GTE`, `LT`, or `LTE` with a mask, and `to_jiffies_timeout()`, which translates relative or absolute nanosecond timeout arguments to scheduler jiffies. It consumes `struct drm_xe_wait_user_fence`, `struct xe_file`, `struct xe_device`, and optional `struct xe_exec_queue`.

## Control Flow

The ioctl validates extension, padding, reserved fields, flags, operation, and 8-byte address alignment. If `exec_queue_id` is nonzero it looks up and references the queue. It converts the timeout, registers a wait entry on `xe->ufence_wq`, repeatedly compares the user address, handles signals, checks queue reset status, waits interruptibly, and on timeout performs an `LNL_FLUSH_WORKQUEUE()` plus one final compare before returning `-ETIME`. On relative-time waits it writes the remaining timeout back into the ioctl argument.

## State And Persistence Behavior

No durable kernel state is created. Temporary state is the waitqueue entry, queue reference, timeout accounting, and start timestamp. Persistent state observed by the wait is user memory at `args->addr`, the device user-fence waitqueue, and queue reset status. Relative timeout mutation is the only userspace-visible state update besides the return code.

## Dependencies And Integration Points

It depends on DRM ioctl plumbing, `copy_from_user()`, DRM timeout helpers, Xe file/device conversion helpers, `xe_exec_queue_lookup()`, queue reset callbacks, and `xe->ufence_wq` wakeups from other Xe paths. The ABI constants come from `uapi/drm/xe_drm.h`.

## Risks And Test Signals

Risks include user-address faults, missed wakeups if producers do not wake `ufence_wq`, subtle timeout semantics for zero, negative, absolute, and overflowed waits, and queue lifetime/reset races. Test signals are ioctl validation failures, successful masked comparisons for every operation, signal interruption, queue reset returning `-EIO`, zero-timeout retry behavior, absolute-timeout expiry, and relative timeout remainder updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.h

## Purpose

`xe_wait_user_fence.h` declares the Xe user-fence wait ioctl entry point for use by the driver ioctl table and related Xe DRM code.

## Important APIs, Types, And Functions

It forward declares `struct drm_device` and `struct drm_file`, then exports `int xe_wait_user_fence_ioctl(struct drm_device *dev, void *data, struct drm_file *file)`.

## Control Flow

The header has no runtime control flow. It is included by the implementation and by whichever file wires the ioctl into Xe's DRM ioctl dispatch.

## State And Persistence Behavior

The header owns no state. Its include guard `_XE_WAIT_USER_FENCE_H_` prevents duplicate declarations.

## Dependencies And Integration Points

It deliberately avoids pulling in large DRM headers by using forward declarations. Integration is the C ABI contract between Xe ioctl registration and `xe_wait_user_fence.c`.

## Risks And Test Signals

Risk is limited to declaration drift if the implementation signature changes. Compile coverage of the ioctl table and implementation is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.c

## Purpose

`xe_wopcm.c` partitions and programs Intel Xe Write Once Protected Content Memory for GuC and HuC firmware. It calculates platform WOPCM size, reserves mandatory regions, validates firmware fit, honors BIOS/IFWI prelocked registers, and writes the GuC WOPCM size/base registers when unlocked.

## Important APIs, Types, And Functions

Public APIs are `xe_wopcm_size()` and `xe_wopcm_init()`. Internal helpers include `context_reserved_size()`, `__check_layout()`, `__wopcm_regs_locked()`, and `__wopcm_init_regs()`. Constants define default WOPCM sizes, GuC/HuC reserved areas, GuC stack reservation, alignment, and hardware-context reservation.

## Control Flow

Initialization derives GuC and HuC upload sizes, rejects missing GuC firmware, chooses the platform WOPCM size, asserts force-wake ownership, and checks whether WOPCM registers are already locked. If locked, it reads and validates the programmed base/size against a maximum WOPCM size. If unlocked, it aligns the GuC base after the HuC firmware plus reserved area, clamps it below the hardware-context reservation, assigns the remaining aligned space to GuC, validates the layout, stores `wopcm->guc.base` and `wopcm->guc.size`, and writes/verifies `GUC_WOPCM_SIZE` and `DMA_GUC_WOPCM_OFFSET`.

## State And Persistence Behavior

Persistent driver state is stored in `struct xe_wopcm`: total WOPCM size and GuC region base/size. Hardware persistence is stronger: the GuC WOPCM size and offset registers are locked/valid write-once configuration until reset. If HuC firmware is available, the HuC-loading-agent bit is included in the offset programming.

## Dependencies And Integration Points

It depends on GT/device conversion, force-wake assertions, Xe MMIO read/write-and-verify helpers, GuC register definitions, firmware upload sizes from `xe_uc_fw`, platform info such as DGFX, Meteor Lake, and Nova Lake P, and DRM diagnostics. `ALLOW_ERROR_INJECTION()` allows failure testing in probe paths.

## Risks And Test Signals

Risks include firmware sizes exceeding static WOPCM assumptions, mismatch between prelocked BIOS layout and driver validation, per-GT vs global maximum-size FIXME behavior, alignment/mask mistakes, and write-once register failures that block GuC upload. Test by injecting `xe_wopcm_init()` errors, booting with GuC-only and GuC+HuC firmware, exercising locked and unlocked register paths, checking MMIO values, and validating error logs for too-large firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.h

## Purpose

`xe_wopcm.h` exposes the WOPCM initialization and sizing API to Xe GT/uC setup code.

## Important APIs, Types, And Functions

It includes `xe_wopcm_types.h`, forward declares `struct xe_device`, and declares `xe_wopcm_init()` and `xe_wopcm_size()`.

## Control Flow

There is no runtime control flow; this is a declaration boundary between WOPCM consumers and the implementation.

## State And Persistence Behavior

No state is owned by the header. It centralizes access to `struct xe_wopcm` through the included type header.

## Dependencies And Integration Points

The header integrates GT/uC initialization with the WOPCM implementation while avoiding full Xe device type inclusion.

## Risks And Test Signals

Risk is declaration/type mismatch. Build coverage in users of `xe_wopcm_init()` and `xe_wopcm_size()` is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm_types.h

## Purpose

`xe_wopcm_types.h` defines the small persistent data model for Xe WOPCM layout information.

## Important APIs, Types, And Functions

The sole type is `struct xe_wopcm`, containing the overall WOPCM `size` and a nested `guc` region with `base` and `size`.

## Control Flow

The file has no control flow. It supplies a shared structure definition to implementation and consumers.

## State And Persistence Behavior

Instances persist as part of GT uC state and reflect the software copy of the hardware WOPCM partition.

## Dependencies And Integration Points

It depends only on Linux integer types. It is included by `xe_wopcm.h` and any code needing the struct layout.

## Risks And Test Signals

Risks are field semantic drift from the hardware register interpretation. Compile coverage plus runtime WOPCM debug logs validate that populated fields are nonzero and aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Kconfig

## Purpose

This Kconfig file defines build selection for the Xen para-virtualized DRM frontend.

## Important APIs, Types, And Functions

It defines hidden `DRM_XEN` and user-visible tristate `DRM_XEN_FRONTEND`, described as a para-virtualized frontend DRM/KMS driver for Xen guest OSes.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution enables the frontend only when Xen and DRM are present and selects helper facilities.

## State And Persistence Behavior

No runtime state is stored. Configuration state is the selected kernel build symbol.

## Dependencies And Integration Points

`DRM_XEN_FRONTEND` depends on `XEN && DRM` and selects `DRM_XEN`, `DRM_KMS_HELPER`, `VIDEOMODE_HELPERS`, `XEN_XENBUS_FRONTEND`, and `XEN_FRONT_PGDIR_SHBUF`.

## Risks And Test Signals

Risks are missing selected helpers or invalid build combinations. Test signals are `allmodconfig`/`COMPILE_TEST`-style builds and module load availability only in Xen guest configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Makefile

## Purpose

The Makefile builds the Xen DRM frontend module from its control, KMS, connector, event-channel, config, and GEM sources.

## Important APIs, Types, And Functions

It defines `drm_xen_front-objs` as `xen_drm_front.o`, `xen_drm_front_kms.o`, `xen_drm_front_conn.o`, `xen_drm_front_evtchnl.o`, `xen_drm_front_cfg.o`, and `xen_drm_front_gem.o`.

## Control Flow

No runtime control flow exists. Kbuild links the object list into `drm_xen_front.o` when `CONFIG_DRM_XEN_FRONTEND` is enabled.

## State And Persistence Behavior

No runtime state. Build state is controlled by the Kconfig symbol.

## Dependencies And Integration Points

The object list mirrors the driver architecture: XenBus lifecycle, simple KMS, virtual connectors, Xen rings/event channels, XenStore config, and GEM/grant sharing.

## Risks And Test Signals

Risk is omitting an object that provides exported intra-module symbols. Test signal is successful module link with no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.c

## Purpose

`xen_drm_front.c` is the Xen PV display frontend core. It handles XenBus lifecycle, backend state transitions, DRM device creation, dumb-buffer allocation, grant-shared display-buffer protocol requests, framebuffer attach/detach, page flips, and cleanup of backend-visible resources.

## Important APIs, Types, And Functions

The central state is `struct xen_drm_front_info` and internal `struct xen_drm_front_dbuf`. Public cross-file operations include `xen_drm_front_mode_set()`, `xen_drm_front_dbuf_create()`, `xen_drm_front_fb_attach()`, `xen_drm_front_fb_detach()`, `xen_drm_front_page_flip()`, `xen_drm_front_on_frame_done()`, and `xen_drm_front_gem_object_free()`. XenBus entry points are `xen_drv_probe()`, `xen_drv_remove()`, and `displback_changed()`.

## Control Flow

Probe initializes DMA mask, allocates frontend state, and switches the frontend to `Initialising`. On backend `InitWait`, it reads XenStore config, creates and publishes event channels, then moves to `Initialised`. On backend `Connected`, it marks channels connected and creates/registers the DRM device. DRM dumb create builds a GEM object, shares its pages or backend allocation directory with `XENDISPL_OP_DBUF_CREATE`, then exposes the handle. Framebuffer creation calls into this file for `FB_ATTACH`; KMS mode enable and flips send `SET_CONFIG` and `PG_FLIP` requests. Disconnect/unplug tears down DRM, channels, display buffers, and XenBus state.

## State And Persistence Behavior

Persistent state includes XenBus device pointer, event-channel pairs, parsed config, DRM private state, an `io_lock`, and `dbuf_list` entries containing cookies and `xen_front_pgdir_shbuf` grant-directory state. Backend-visible resources persist until explicit destroy/detach or disconnect. Backend-allocated buffers release local grants before destroy; frontend-allocated buffers keep local resources until after destroy attempt.

## Dependencies And Integration Points

It depends on XenBus, Xen display protocol `displif`, `xen-front-pgdir-shbuf`, DRM GEM/modeset core, simple KMS, and helper modules in this directory. It integrates with `xen_drm_front_evtchnl.c` for rings, `xen_drm_front_cfg.c` for XenStore, `xen_drm_front_gem.c` for pages, and `xen_drm_front_kms.c` for frame-done delivery.

## Risks And Test Signals

Risks include backend timeouts, stale grant mappings on abnormal guest/backend death, races between handle publication and backend buffer creation, cookie reuse because cookies are kernel pointers cast to `u64`, and complicated XenBus reconnect behavior. Test with frontend- and backend-allocated buffers, backend restart, module remove, dumb create failure injection, framebuffer lifecycle, page flips with frame-done events, and Xen page-size mismatch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.h

## Purpose

`xen_drm_front.h` defines shared state and protocol-facing APIs for the Xen PV DRM frontend.

## Important APIs, Types, And Functions

It documents buffer allocation modes and driver limitations, defines `XEN_DRM_FRONT_WAIT_BACK_MS`, and declares `struct xen_drm_front_info`, `struct xen_drm_front_drm_pipeline`, and `struct xen_drm_front_drm_info`. Inline cookie helpers convert framebuffer and GEM pointers to backend cookies. Function declarations cover mode set, display-buffer create, framebuffer attach/detach, page flip, frame-done notification, and GEM object free.

## Control Flow

No direct control flow. It defines the call graph used by KMS, GEM, event-channel, and core files.

## State And Persistence Behavior

The structs persist for the lifetime of the XenBus frontend and DRM device. `xen_drm_front_info` owns channels, config, and display-buffer list; per-pipeline state owns connector/pipe metadata, pending vblank event, delayed flip timeout work, and connection status.

## Dependencies And Integration Points

It depends on DRM connector/simple-KMS types, scatterlist support, and `xen_drm_front_cfg.h`. It is the shared contract across all Xen frontend source files.

## Risks And Test Signals

Risks include fixed limits (`XEN_DRM_FRONT_MAX_CRTCS`), pointer-as-cookie assumptions, and documented feature limitations such as primary-plane-only and fixed 60 Hz virtual modes. Compile coverage and multi-connector runtime tests validate struct and API alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.c

## Purpose

`xen_drm_front_cfg.c` reads the XenStore display configuration supplied by the backend/domain config.

## Important APIs, Types, And Functions

The public function is `xen_drm_front_cfg_card()`. The internal helper `cfg_connector()` reads a connector path and parses its `resolution` field into width and height.

## Control Flow

Configuration starts by checking whether backend allocation is advertised through `XENDISPL_FIELD_BE_ALLOC`. It scans connector indices from 0 through `XEN_DRM_FRONT_MAX_CRTCS - 1`, stopping at the first missing or malformed connector resolution. At least one connector must be present or the call returns `-ENODEV`.

## State And Persistence Behavior

It fills `struct xen_drm_front_cfg`: `front_info`, `be_alloc`, `num_connectors`, per-connector dimensions, and devm-allocated XenStore connector paths. This state persists through event-channel creation and KMS initialization.

## Dependencies And Integration Points

It depends on XenBus reads, Xen display protocol field names, DRM logging, and `xen_drm_front_cfg.h`. The core file calls it during backend `InitWait`.

## Risks And Test Signals

Risks include accepting only contiguous connector indices, rejecting malformed resolution strings, and trusting backend-provided dimensions. Test by varying XenStore resolution entries, missing connector 0, backend allocation flag, and maximum connector count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.h

## Purpose

`xen_drm_front_cfg.h` defines the frontend's parsed XenStore display configuration.

## Important APIs, Types, And Functions

It defines `XEN_DRM_FRONT_MAX_CRTCS` as 4, `struct xen_drm_front_cfg_connector` with width, height, and XenStore path, `struct xen_drm_front_cfg` with connector array and `be_alloc`, and declares `xen_drm_front_cfg_card()`.

## Control Flow

No runtime control flow exists in the header.

## State And Persistence Behavior

The config struct is stored inside `struct xen_drm_front_info` and persists across channel publishing and DRM/KMS setup.

## Dependencies And Integration Points

It depends on Linux types and is shared by the core, config reader, and KMS pipeline initialization.

## Risks And Test Signals

Risks are fixed connector capacity and assumptions that dimensions are valid for DRM mode creation. Build coverage and XenStore-driven multi-connector tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.c

## Purpose

`xen_drm_front_conn.c` implements virtual DRM connector support and advertises the framebuffer formats accepted by the Xen PV display frontend.

## Important APIs, Types, And Functions

Public APIs are `xen_drm_front_conn_init()` and `xen_drm_front_conn_get_formats()`. It supports RGB565, RGB888, XRGB/ARGB8888, XRGB/ARGB4444, XRGB/ARGB1555, and YUYV. Connector callbacks are `connector_detect()` and `connector_get_modes()`.

## Control Flow

Connector initialization installs helper funcs, marks the pipeline connected, enables connect/disconnect polling, and creates a `DRM_MODE_CONNECTOR_VIRTUAL`. Mode enumeration synthesizes one preferred 60 Hz mode from the backend-provided width and height with zero porch/sync fields. Detection reports disconnected after DRM unplug, otherwise follows `pipeline->conn_connected`.

## State And Persistence Behavior

Connection state is `pipeline->conn_connected`; fixed dimensions are stored in the pipeline by KMS setup. No EDID or persistent mode database exists.

## Dependencies And Integration Points

It depends on DRM atomic connector helpers, fourcc definitions, probe helpers, videomode conversion, and the Xen KMS pipeline struct. KMS uses the format list for simple display pipe initialization.

## Risks And Test Signals

Risks include simplistic timing generation, fixed 60 Hz behavior, no EDID, and connector status being used as an error signal after backend failures. Test connector polling, mode list dimensions, unplug behavior, and format acceptance/rejection in framebuffer creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.h

## Purpose

`xen_drm_front_conn.h` declares connector initialization and format-list access for Xen PV KMS.

## Important APIs, Types, And Functions

It declares `xen_drm_front_conn_init()` and `xen_drm_front_conn_get_formats()`, with forward declarations for DRM connector and frontend DRM info.

## Control Flow

There is no runtime control flow.

## State And Persistence Behavior

No state is owned by the header.

## Dependencies And Integration Points

The header connects `xen_drm_front_kms.c` to connector implementation while keeping compile dependencies small.

## Risks And Test Signals

Risk is signature drift against implementation. KMS build and simple display pipe creation validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.c

## Purpose

`xen_drm_front_evtchnl.c` allocates, publishes, services, flushes, state-manages, and frees Xen event-channel pairs used by the display frontend for request/response traffic and backend events.

## Important APIs, Types, And Functions

Public APIs are `xen_drm_front_evtchnl_create_all()`, `xen_drm_front_evtchnl_publish_all()`, `xen_drm_front_evtchnl_flush()`, `xen_drm_front_evtchnl_set_state()`, and `xen_drm_front_evtchnl_free_all()`. Interrupt handlers are `evtchnl_interrupt_ctrl()` for response rings and `evtchnl_interrupt_evt()` for asynchronous events.

## Control Flow

Creation allocates a request ring and an event page per configured connector, allocates event-channel ports, and binds IRQ handlers. Publishing writes grant references and ports to each connector's XenStore path inside a retried transaction. Request flushing advances `req_prod_pvt`, pushes requests, and notifies the backend. The control IRQ scans responses up to `rsp_prod`, matches the expected response id, stores status, and completes waiters. The event IRQ scans backend events, checks event ids, and dispatches page-flip frame-done notifications.

## State And Persistence Behavior

Each channel stores grant ref, port, IRQ, index, state, type, response/event ids, and either a front ring/completion/mutex or event page pointer. State transitions to connected gate IRQ processing. Freeing disconnects, completes waiters with `-EIO`, unbinds IRQs, frees event channels, tears down rings, and zeros the struct.

## Dependencies And Integration Points

It depends on Xen event channels, grant-table setup through XenBus ring helpers, Xen display interface ring/event structures, DRM logging, and the frontend `io_lock`. It calls `xen_drm_front_on_frame_done()` for flip events and is driven by core XenBus lifecycle code.

## Risks And Test Signals

Risks include lost completions on id mismatch, ring index handling errors, failing to abort XenBus transactions, IRQs arriving after disconnect, and one global `io_lock` serializing request and event paths. Test by creating multiple connectors, forcing backend response errors/timeouts, injecting event id gaps, backend reconnect, and module removal while waits are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.h

## Purpose

`xen_drm_front_evtchnl.h` defines the event-channel state model and public API for the Xen PV display frontend.

## Important APIs, Types, And Functions

It defines `GENERIC_OP_EVT_CHNL`, state enum `EVTCHNL_STATE_DISCONNECTED/CONNECTED`, type enum `EVTCHNL_TYPE_REQ/EVT`, `struct xen_drm_front_evtchnl`, and `struct xen_drm_front_evtchnl_pair`. Function declarations cover create, publish, flush, state set, and free.

## Control Flow

No runtime flow; it defines data consumed by request construction, IRQ handling, and XenBus lifecycle.

## State And Persistence Behavior

The structs persist in `front_info->evt_pairs`. Request channels own a front ring, completion, response status, and serializer mutex; event channels own an event page.

## Dependencies And Integration Points

It depends on Linux completions, Xen ring macros, and `xen/interface/io/displif.h`. It is shared by core protocol code and event-channel implementation.

## Risks And Test Signals

Risks include layout mismatch with implementation and misuse of request-only union fields on event channels. Compile coverage and runtime channel creation/publishing validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_evtchnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.c

## Purpose

`xen_drm_front_gem.c` implements GEM object allocation, import, mmap, SG-table export, vmap/vunmap, and backend-allocated page handling for the Xen PV display frontend.

## Important APIs, Types, And Functions

Internal `struct xen_gem_object` extends `drm_gem_object` with page array, backend-allocation flag, and imported SG table. Public APIs are `xen_drm_front_gem_create()`, `xen_drm_front_gem_free_object_unlocked()`, `xen_drm_front_gem_get_pages()`, `xen_drm_front_gem_get_sg_table()`, `xen_drm_front_gem_import_sg_table()`, `xen_drm_front_gem_prime_vmap()`, and `xen_drm_front_gem_prime_vunmap()`.

## Control Flow

GEM creation rounds size to page boundaries and creates the GEM object. For backend allocation it allocates a page-pointer array and Xen unpopulated pages for grant mapping. For frontend allocation it obtains shmem-backed GEM pages. Mmap clears `VM_PFNMAP`, sets mixed/DONTEXPAND flags, uses normal cacheable protection, and inserts all pages with `vm_map_pages()`. PRIME import creates a GEM shell, converts SG entries to a page array, then shares the imported pages with the backend through `xen_drm_front_dbuf_create()`.

## State And Persistence Behavior

Object lifetime state includes page arrays, unpopulated pages or shmem pages, imported SG table references, and backend display-buffer state created by the core file. Freeing reverses those resources and releases the GEM object.

## Dependencies And Integration Points

It depends on DRM GEM/PRIME/shmem helpers, DMA-buf, scatterlists, Xen balloon/unpopulated pages, and core frontend buffer creation/free callbacks. The DRM driver uses it for dumb buffers and PRIME import/export.

## Risks And Test Signals

Risks include leaks on error paths in PRIME import after partial allocation, backend allocation grant mapping assumptions, page-attribute requirements on ARM Xen, and the FIXME that mmap installs pages eagerly without a fault handler. Test mmap CPU access, PRIME import/export, backend-allocated buffers, object free during unplug, SG offset handling, and allocation failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.h

## Purpose

`xen_drm_front_gem.h` declares the GEM helper interface used by the Xen PV frontend DRM driver.

## Important APIs, Types, And Functions

It declares create, PRIME import, SG-table export, page-array access, free, vmap, and vunmap functions, with forward declarations for DRM, DMA-buf, SG, and iosys-map types.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned by the header; it describes operations on GEM objects allocated by the implementation.

## Dependencies And Integration Points

It connects `xen_drm_front.c` and DRM driver callbacks to the GEM implementation without exporting the private `struct xen_gem_object`.

## Risks And Test Signals

Risks are declaration drift and mismatched callback signatures. Module link and PRIME/dumb-buffer build coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.c

## Purpose

`xen_drm_front_kms.c` implements the Xen frontend's simple KMS pipeline: framebuffer creation/destruction with backend attach/detach, mode config, display enable/disable, page flip submission, frame-done event delivery, and per-connector simple display pipe setup.

## Important APIs, Types, And Functions

Public APIs are `xen_drm_front_kms_init()`, `xen_drm_front_kms_fini()`, and `xen_drm_front_kms_on_frame_done()`. Important helpers include `fb_create()`, `fb_destroy()`, `display_enable()`, `display_disable()`, `display_update()`, `display_send_page_flip()`, and `send_pending_event()`.

## Control Flow

KMS init initializes mode config, creates a simple display pipe for each configured connector, resets mode config, and starts polling. Framebuffer creation uses DRM GEM FB helpers then asks the backend to attach the framebuffer cookie. Display enable sends `SET_CONFIG` with framebuffer geometry and bpp; disable sends a zero config and releases any pending event. Atomic update captures the DRM event, sends page flip only for old-fb-to-new-fb transitions, schedules a timeout worker, and otherwise completes the event immediately. Backend frame-done IRQ cancels the timeout and sends the event.

## State And Persistence Behavior

Per-pipeline persistent state includes dimensions, connector, simple pipe, pending vblank event, delayed timeout work, and `conn_connected`. Mode config limits are fixed at 4095x2047. Pending events are protected by DRM `event_lock` and always drained on disable/fini.

## Dependencies And Integration Points

It depends on DRM atomic/simple-KMS/GEM framebuffer/vblank helpers, connector format declarations, and core Xen protocol functions. It receives frame-done notifications from event-channel IRQ handling.

## Risks And Test Signals

Risks include event leaks or double sends under timeout/IRQ races, treating page-flip failure as connector disconnect, fixed mode limits, and no real vblank initialization despite custom event handling. Test page-flip completion, timeout fallback, enable/disable transitions, framebuffer attach failure, connector poll after backend error, and multi-connector KMS setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.h

## Purpose

`xen_drm_front_kms.h` declares the simple-KMS interface for the Xen PV display frontend.

## Important APIs, Types, And Functions

It declares `xen_drm_front_kms_init()`, `xen_drm_front_kms_fini()`, and `xen_drm_front_kms_on_frame_done()` with forward declarations for frontend DRM info and pipeline types.

## Control Flow

The header has no runtime control flow.

## State And Persistence Behavior

No state is owned here; the declarations operate on state defined in `xen_drm_front.h`.

## Dependencies And Integration Points

It connects core DRM creation and event-channel frame-done dispatch to KMS implementation.

## Risks And Test Signals

Risk is signature drift. Build coverage and frame-done dispatch linkage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Kconfig

## Purpose

This Kconfig file defines the Xilinx ZynqMP DisplayPort Subsystem DRM/KMS driver and optional DisplayPort audio support.

## Important APIs, Types, And Functions

It defines `DRM_ZYNQMP_DPSUB` and `DRM_ZYNQMP_DPSUB_AUDIO`. The display driver selects DRM bridge connector, DP helpers, GEM DMA helpers, KMS helpers, client selection, generic PHY, and DMA engine support. Audio depends on ASoC and the display driver.

## Control Flow

No runtime control flow. Kconfig resolves platform, clock, OF, DMA, PHY, DPDMA, DRM, and sound dependencies.

## State And Persistence Behavior

No runtime state. Selected symbols control built objects and optional audio integration.

## Dependencies And Integration Points

The driver depends on `ARCH_ZYNQMP || COMPILE_TEST`, common clocks, OF, DMADEVICES, `PHY_XILINX_ZYNQMP`, and `XILINX_ZYNQMP_DPDMA`. Audio selects generic DMAengine PCM.

## Risks And Test Signals

Risks include invalid modular ASoC combinations and missing DMA/PHY dependencies. Test with built-in and module configurations, with and without `DRM_ZYNQMP_DPSUB_AUDIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Makefile

## Purpose

The Makefile builds the ZynqMP DisplayPort Subsystem DRM module.

## Important APIs, Types, And Functions

`zynqmp-dpsub-y` includes `zynqmp_disp.o`, `zynqmp_dpsub.o`, `zynqmp_dp.o`, and `zynqmp_kms.o`; `zynqmp_dp_audio.o` is added when audio support is enabled.

## Control Flow

No runtime flow. Kbuild links the module when `CONFIG_DRM_ZYNQMP_DPSUB` is selected.

## State And Persistence Behavior

No runtime state.

## Dependencies And Integration Points

The object list maps to display-controller register programming, platform lifecycle, DP bridge/link handling, DRM/KMS integration, and optional ASoC audio.

## Risks And Test Signals

Risk is missing optional object linkage. Build with audio enabled and disabled validates the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.c

## Purpose

`zynqmp_disp.c` drives the display-controller portion of the ZynqMP DP subsystem: AV buffer manager, video blender, audio buffer routing, DRM display layers, DPDMA channel setup, live-input format setup, and display clock programming.

## Important APIs, Types, And Functions

Key types are `struct zynqmp_disp`, `struct zynqmp_disp_layer`, `struct zynqmp_disp_layer_dma`, and `struct zynqmp_disp_format`. Public APIs include `zynqmp_disp_probe()`, `zynqmp_disp_remove()`, `zynqmp_disp_enable()`, `zynqmp_disp_disable()`, `zynqmp_disp_setup_clock()`, `zynqmp_disp_blend_set_global_alpha()`, `zynqmp_disp_layer_drm_formats()`, `zynqmp_disp_live_layer_formats()`, `zynqmp_disp_layer_set_format()`, `zynqmp_disp_layer_set_live_format()`, `zynqmp_disp_layer_update()`, `zynqmp_disp_layer_enable()`, and `zynqmp_disp_layer_disable()`.

## Control Flow

Probe maps `blend` and `av_buf` resources, creates VID/GFX layers, chooses non-live DPDMA mode or live mode from `dpsub->dma_enabled`, requests DPDMA channels in non-live mode, and exports layer pointers to `dpsub`. Format setup writes AV buffer format fields and component scaling factors. Plane updates prepare repeating interleaved DMA descriptors per framebuffer plane and start DPDMA channels. Enabling the display configures RGB blender output, background, clock sources, AV buffer reset, channel burst lengths, and audio routing. Layer enable/disable coordinates AV buffer output selection and blender CSC/layer control.

## State And Persistence Behavior

Persistent software state includes mapped register bases, layer format/mode pointers, DMA channels, current DRM format, and DPDMA alignment exported through `dpsub->dma_align`. Hardware state persists in AV buffer format/output/channel/reset/clock registers, blender output/CSC/background/global-alpha/layer-control registers, and running DPDMA descriptors until terminated.

## Dependencies And Integration Points

It depends on DRM format/framebuffer/plane helpers, `drm_fb_dma_get_gem_addr()`, DMAengine interleaved transfers, Xilinx DPDMA peripheral config, media bus formats, common clocks through `dpsub`, and register definitions from `zynqmp_disp_regs.h`. It integrates with `zynqmp_kms.c` for non-live planes and `zynqmp_dp.c` for live input bus formats.

## Risks And Test Signals

Risks include unsupported hybrid live/non-live mode, strict no-scaling assumptions, DMA descriptor/pitch alignment errors, incorrect RGB/YUV swap or CSC matrix programming, channel termination races, and clock source mismatch between DT and hardware. Test VID/GFX formats including multi-plane YUV, alpha on graphics layer, live input bus-format negotiation, DMA alignment in dumb buffers and FB pitches, enable/disable cycles, and underflow/overflow interrupt diagnostics from DP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.h

## Purpose

`zynqmp_disp.h` declares the ZynqMP display-controller API shared by the platform, DP bridge, and DRM/KMS layers.

## Important APIs, Types, And Functions

It defines maximum display dimensions, 44-bit DMA limit, layer IDs `VID` and `GFX`, and declarations for display enable/disable, clock setup, global alpha, format-list queries, layer format/update/enable/disable, probe, and remove.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned, but the declarations operate on opaque `struct zynqmp_disp` and `struct zynqmp_disp_layer` instances maintained by `zynqmp_disp.c`.

## Dependencies And Integration Points

It forward declares DRM format/plane state, platform device, and DPSUB types to keep dependencies small. `zynqmp_dpsub.h`, `zynqmp_dp.c`, and `zynqmp_kms.c` consume this interface.

## Risks And Test Signals

Risks are API drift and mismatch between max dimensions/DMA limit and hardware/KMS constraints. Build coverage and mode validation around the advertised limits are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp_regs.h

## Purpose

`zynqmp_disp_regs.h` names register offsets and bit fields for the ZynqMP display controller's blender, AV buffer manager, and audio mixer.

## Important APIs, Types, And Functions

It defines blender background/global-alpha/output-format/layer-control/CSC registers, AV buffer format/channel/STC/output/clock/reset/scaling/live-config/palette registers, and audio mixer volume/channel-status/data/reset registers.

## Control Flow

No runtime control flow. These macros are consumed by direct MMIO reads/writes in `zynqmp_disp.c`, `zynqmp_dp_audio.c`, and related paths.

## State And Persistence Behavior

The macros describe persistent hardware register state for layer routing, format selection, CSC matrices, buffer channel enable/flush, clock source selection, and audio mixer/control state.

## Dependencies And Integration Points

It depends on `linux/bits.h` for bit helpers and integrates tightly with the display and audio source files. Values must match the ZynqMP DP subsystem hardware specification.

## Risks And Test Signals

Risks include incorrect offsets/masks silently corrupting adjacent hardware state, especially shared AV buffer output fields and audio reset/volume registers. Test through register readback where available, format/output changes, alpha/CSC behavior, audio playback, and underflow/overflow interrupt observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.c

## Purpose

`zynqmp_dp.c` implements the ZynqMP DisplayPort transmitter as a DRM bridge. It owns DP core MMIO programming, PHY/reset handling, AUX transactions, sink detection and EDID, link training, stream timing/TU programming, live-layer bus-format negotiation, debugfs test modes, HPD handling, vblank interrupt control, and minimal DP audio register helpers.

## Important APIs, Types, And Functions

Important state is `struct zynqmp_dp`, including AUX, bridge, work items, lock, PHYs, DPCD, link config, mode, test state, and flags. Public APIs are `zynqmp_dp_probe()`, `zynqmp_dp_remove()`, `zynqmp_dp_enable_vblank()`, `zynqmp_dp_disable_vblank()`, `zynqmp_dp_audio_set_channels()`, `zynqmp_dp_audio_enable()`, `zynqmp_dp_audio_disable()`, and `zynqmp_dp_audio_write_n_m()`. Major helpers include PHY init/exit/probe/ready, `zynqmp_dp_mode_configure()`, `zynqmp_dp_train_loop()`, AUX transfer, bridge atomic enable/disable/check, detect, EDID read, test-pattern debugfs, and IRQ handling.

## Control Flow

Probe allocates the bridge object, maps the `dp` resource, gets IRQ/reset/PHYs, resets hardware, initializes default RGB 8bpc config, powers down lanes, initializes PHYs, enables transmitter, requests IRQ, and exposes `dpsub->dp`/`dpsub->bridge`. Bridge attach registers AUX and enables interrupts. Detection polls HPD, reads DPCD, and records common max link rate/lane count. Atomic enable powers runtime PM, enables live DISP input if present, configures format, validates bandwidth, chooses lane/rate, programs TU and main stream timing, powers sink to D0, trains the link with downshift on failure, resets stream/AUX blocks, and enables main stream. IRQ handling clears status, reports under/overflow, handles vblank, schedules HPD/HPD-IRQ work, and completes AUX replies.

## State And Persistence Behavior

Software state persists in `struct zynqmp_dp`: connection status, enabled flag, DPCD, link capabilities, current mode, test/debugfs settings, and cached format bits. Hardware state persists in DP link, lane, PHY, AUX, main-stream, interrupt, audio, and test-pattern registers until disabled/reset. Runtime PM keeps the device active during stream/audio operations.

## Dependencies And Integration Points

It depends on DRM bridge/DP helpers, EDID/DDC through `drm_dp_aux`, OF bridge lookup, PHY framework, reset controls, common clocks through DPSUB, PM runtime, debugfs, and display-layer APIs for live input. It integrates with KMS through a bridge connector and vblank callbacks, and with audio through exported DP audio register helpers.

## Risks And Test Signals

Risks include AUX timeout tuning, HPD debounce heuristics, link training failures and downshift limits, only two lanes supported, horizontal backporch adjustment side effects, debugfs test modes overriding live link state, interrupt mask/status name confusion for reply bits, and runtime-PM balance on early errors. Test hotplug, EDID reads, modes near bandwidth limits, 1/2 lane training at RBR/HBR/HBR2, HPD IRQ retraining, vblank delivery, suspend/resume, debugfs test patterns, AUX error ignore mode, and live-input bus format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.h

## Purpose

`zynqmp_dp.h` declares the ZynqMP DisplayPort bridge/control API used by platform, KMS, and audio code.

## Important APIs, Types, And Functions

It forward declares `struct zynqmp_dp` and `struct zynqmp_dpsub`, and declares probe/remove, vblank enable/disable, audio channel enable/disable, and audio N/M programming helpers.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned by the header; all operations act on `struct zynqmp_dp` created by `zynqmp_dp_probe()`.

## Dependencies And Integration Points

It connects `zynqmp_dpsub.c`, `zynqmp_kms.c`, and `zynqmp_dp_audio.c` to the DP implementation.

## Risks And Test Signals

Risk is signature drift across display, KMS, and audio call sites. Build coverage with audio enabled and disabled validates the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp_audio.c

## Purpose

`zynqmp_dp_audio.c` adds optional ASoC/DMAengine PCM support for ZynqMP DisplayPort audio. It registers a CPU DAI, two DMAengine playback PCMs, a simple card, volume controls, and programs audio clocks/status/registers when playback starts.

## Important APIs, Types, And Functions

State is `struct zynqmp_dpsub_audio`, containing MMIO base, card, DAI/PCM/link names, DAI driver, PCM configs, links, component descriptors, enable mutex, enabled stream count, current rate, and two cached volumes. Public APIs are `zynqmp_audio_init()` and `zynqmp_audio_uninit()`. Runtime callbacks include `dp_dai_hw_params()`, `dp_dai_hw_free()`, `zynqmp_dp_dai_read()`, and `zynqmp_dp_dai_write()`.

## Control Flow

Init exits silently if no audio clock exists, maps `aud`, creates names, registers the CPU DAI, registers two DMAengine PCMs using `aud0`/`aud1`, builds a dummy-codec ASoC card, and restores platform driver data after card registration. `hw_params` accepts only 44.1 kHz or 48 kHz, prevents rate changes while streams are active, programs `aud_clk` to sample rate times 512, enables PM/runtime clocking, writes mixer volume and IEC958 channel status, configures two DP channels, writes audio N/M, and enables DP audio. `hw_free` decrements stream use, disables DP audio and clock on the last stream, and drops runtime PM.

## State And Persistence Behavior

Persistent state includes cached volumes, current sample rate, active stream count, and registered ASoC card/DAI/PCM objects. Hardware state includes audio mixer volume, channel status words, soft reset, DP audio channel count, and audio enable/N/M registers.

## Dependencies And Integration Points

It depends on ASoC core, DMAengine PCM, ALSA IEC958 definitions, clocks, PM runtime, display audio register macros, and DP audio helpers from `zynqmp_dp.c`. It integrates with the platform probe after DRM/display/DP setup.

## Risks And Test Signals

Risks include only S16_LE stereo 44.1/48 kHz support, clock-rate tolerance failures, no audio reset because reset breaks restart, devm card registration overwriting driver data, older DTs missing audio DMA channels, and multi-PCM rate sharing. Test sound-card registration with/without audio DMA nodes, playback on both PCMs, concurrent same-rate streams, rejected rate changes, volume writes while idle/active, suspend/resume, and DP sink audio interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.c

## Purpose

`zynqmp_dpsub.c` is the platform-driver lifecycle for the Xilinx ZynqMP DisplayPort Subsystem. It allocates subsystem state, initializes clocks and DT topology, probes DP/display/KMS/audio components, and coordinates teardown, shutdown, and system sleep.

## Important APIs, Types, And Functions

Important helpers are `zynqmp_dpsub_init_clocks()`, `zynqmp_dpsub_parse_dt()`, `zynqmp_dpsub_probe()`, `zynqmp_dpsub_remove()`, `zynqmp_dpsub_shutdown()`, and exported `zynqmp_dpsub_release()`. PM callbacks use DRM mode-config helper suspend/resume.

## Control Flow

Probe allocates `struct zynqmp_dpsub`, sets a 44-bit DMA mask and 32-bit max segment size, initializes reserved memory, enables the APB clock, selects video/audio clocks from PL live or PS fallback sources, parses OF graph ports, enables runtime PM, probes DP first, probes the display controller, registers the DP bridge, initializes DRM/KMS if DMA mode is enabled, initializes optional audio, and reports success. Error paths unwind DRM, bridge, display, DP, PM, clocks, reserved memory, and manual allocation as needed.

## State And Persistence Behavior

Persistent subsystem state includes clock handles/source flags, connected port bitmask, `dma_enabled`, DRM/bridge/disp/layers/dp pointers, DMA alignment, and optional audio state. Runtime PM and APB clock state persist while the driver is bound. In DRM-managed mode, release is tied to DRM device cleanup.

## Dependencies And Integration Points

It depends on platform resources, OF graph, reserved memory, DMA masks, common clocks, PM runtime, DRM bridge/atomic helpers, and local DP/DISP/KMS/audio modules. It matches `xlnx,zynqmp-dpsub-1.7`.

## Risks And Test Signals

Risks include backward-compatible DT behavior without ports, rejecting multiple live inputs, requiring PL clock for live video, unsupported live audio/PL outputs, probe unwind differences before/after DRM allocation, and APB clock lifetime. Test old and new DT topologies, DMA and live modes, missing clocks, reserved-memory presence, probe deferral, module remove, shutdown, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.h

## Purpose

`zynqmp_dpsub.h` defines the shared subsystem object and topology enums for the ZynqMP DP subsystem.

## Important APIs, Types, And Functions

It defines `ZYNQMP_DPSUB_NUM_LAYERS`, port enum entries for live video/gfx/audio and output video/audio/DP, output format enum values, `struct zynqmp_dpsub`, optional audio init/uninit prototypes or stubs, and `zynqmp_dpsub_release()`.

## Control Flow

No direct runtime flow. Audio stubs compile to no-ops when audio support is disabled.

## State And Persistence Behavior

`struct zynqmp_dpsub` persists for the platform device lifetime or DRM-managed lifetime and owns pointers to clocks, DRM bridge/display/DP/audio components, layer handles, connected-port flags, DMA mode flag, and DMA alignment.

## Dependencies And Integration Points

It is the central type shared by platform, display, DP, KMS, and audio files. It forward declares most component types to reduce include dependencies.

## Risks And Test Signals

Risks include inconsistent interpretation of `dma_enabled`, connected port bits, and layer indices across modules. Build coverage and probe tests in DMA vs live mode validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.c

## Purpose

`zynqmp_kms.c` provides DRM/KMS integration for ZynqMP DPSUB in DMA mode. It creates VID/GFX planes, a CRTC, a simple encoder/bridge connector chain, GEM DMA dumb buffers, fbdev setup, vblank handling, and atomic plane/CRTC behavior.

## Important APIs, Types, And Functions

Public APIs are `zynqmp_dpsub_drm_init()`, `zynqmp_dpsub_drm_cleanup()`, and `zynqmp_dpsub_drm_handle_vblank()`. Key helpers include plane atomic check/update/disable, `zynqmp_dpsub_create_planes()`, CRTC atomic enable/disable/begin/flush, vblank enable/disable, `zynqmp_dpsub_dumb_create()`, `zynqmp_dpsub_fb_create()`, and `zynqmp_dpsub_kms_init()`.

## Control Flow

DRM init allocates a managed DRM device, attaches a release action for the subsystem, initializes mode config and vblank, creates planes from display layer format lists, creates a CRTC with GFX as primary and VID as overlay, maps possible CRTCs, initializes an encoder, attaches the DP bridge, creates a bridge connector, registers the DRM device, and starts fbdev emulation with RGB888. Atomic CRTC enable sets the pixel clock, enables `vid_clk`, enables the display, and waits three vblanks for timing stability. Plane update reprograms format if needed, submits layer DMA, applies graphics alpha, and enables the layer. CRTC flush arms vblank events.

## State And Persistence Behavior

Persistent DRM state is `struct zynqmp_dpsub_drm` embedded DRM device plus planes, CRTC, and encoder. Hardware state is delegated to `zynqmp_disp` and `zynqmp_dp`. Vblank state is managed by DRM and DP interrupt enable/disable. Dumb buffer and framebuffer creation enforce `dpsub->dma_align`.

## Dependencies And Integration Points

It depends on DRM atomic, bridge connector, GEM DMA, fbdev DMA, vblank, blend, probe helpers, clocks, PM runtime, and local display/DP APIs. It is only initialized when `dpsub->dma_enabled` is true.

## Risks And Test Signals

Risks include no scaling support, graphics plane as primary with video overlay assumptions, explicit primary-plane disable during CRTC disable, clock/PM leaks on enable failure, vblank event handling, and FB pitch alignment rewriting. Test atomic enable/disable, page flips with vblank events, RGB/YUV format changes, alpha property, dumb buffer alignment, bridge connector EDID/mode validation, and cleanup after unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.h

## Purpose

`zynqmp_kms.h` declares the DRM/KMS state and entry points for ZynqMP DPSUB DMA-mode display.

## Important APIs, Types, And Functions

It defines `struct zynqmp_dpsub_drm` with backpointer, DRM device, two planes, one CRTC, and one encoder. It declares `zynqmp_dpsub_drm_handle_vblank()`, `zynqmp_dpsub_drm_init()`, and `zynqmp_dpsub_drm_cleanup()`.

## Control Flow

No runtime flow. It is a shared declaration boundary.

## State And Persistence Behavior

The struct persists for the DRM device lifetime and owns DRM objects used by KMS.

## Dependencies And Integration Points

It includes DRM object headers and `zynqmp_dpsub.h`, and is consumed by platform, DP IRQ, and KMS implementation files.

## Risks And Test Signals

Risks are object lifetime mismatch and declaration drift. DRM init/cleanup and vblank IRQ paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/Kconfig

## Purpose

This Kconfig file defines NVIDIA Tegra host1x support, the host1x context bus, and an optional command-stream firewall.

## Important APIs, Types, And Functions

It defines hidden `TEGRA_HOST1X_CONTEXT_BUS`, tristate `TEGRA_HOST1X`, and boolean `TEGRA_HOST1X_FIREWALL`.

## Control Flow

No runtime control flow. Kconfig selects host1x support for Tegra or compile-test builds and selects required infrastructure.

## State And Persistence Behavior

No runtime state. Build-time symbols decide whether core host1x and context bus objects are compiled and whether firewall checks are enabled.

## Dependencies And Integration Points

`TEGRA_HOST1X` depends on `ARCH_TEGRA || COMPILE_TEST` and selects `DMA_SHARED_BUFFER`, `TEGRA_HOST1X_CONTEXT_BUS`, and `IOMMU_IOVA`. The firewall option defaults to enabled.

## Risks And Test Signals

Risks include compile-test exposure without runtime Tegra hardware and firewall configuration changing command-stream validation behavior. Test with Tegra defconfig, allmodconfig, and firewall on/off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/Makefile

## Purpose

The Makefile builds the Tegra host1x core and optional context bus support.

## Important APIs, Types, And Functions

`host1x-y` includes bus, syncpoint, device, interrupt, CDMA, channel, job, debug, MIPI, fence, and per-generation hardware files from host1x01 through host1x08. `context.o` is added when `CONFIG_IOMMU_API` is enabled. `context_bus.o` is built from `CONFIG_TEGRA_HOST1X_CONTEXT_BUS`.

## Control Flow

No runtime flow. Kbuild links the objects into `host1x.o` for `CONFIG_TEGRA_HOST1X`.

## State And Persistence Behavior

No runtime state. Build composition determines which host1x subsystems are present.

## Dependencies And Integration Points

The object list reflects host1x's bus/client infrastructure, scheduler/channel/job submission, synchronization, debug, MIPI, fence, and hardware-generation abstraction layers.

## Risks And Test Signals

Risk is missing generation-specific object or context support in configurations. Test by building with and without IOMMU API and context bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.c

## Purpose

`host1x/bus.c` implements the host1x logical bus, composite device/client matching, host1x driver registration, client lifecycle, debugfs device listing, suspend/resume reference counting, and host1x buffer-object pin/unpin caching.

## Important APIs, Types, And Functions

Important globals are `clients`, `drivers`, and `devices` lists with mutexes. Internal `struct host1x_subdev` maps DT nodes to clients. Exported APIs include `host1x_device_init()`, `host1x_device_exit()`, `host1x_register()`, `host1x_unregister()`, `host1x_driver_register_full()`, `host1x_driver_unregister()`, `__host1x_client_init()`, `host1x_client_exit()`, `__host1x_client_register()`, `host1x_client_unregister()`, `host1x_client_suspend()`, `host1x_client_resume()`, `host1x_bo_pin()`, and `host1x_bo_unpin()`.

## Control Flow

Host1x controller registration adds the controller to the global list, attaches already registered host1x drivers, and creates debugfs `devices`. Host1x driver registration adds the driver, creates one logical host1x device per controller, parses DT subdevices recursively from driver match tables, and registers the bus driver. Client registration tries to match the client OF node against pending subdevices; when all subdevices are active the logical device is added to the `host1x` bus and the host1x driver can probe. Device init calls each client's `early_init` then `init`, with reverse teardown on failure; exit calls `exit` then `late_exit` in reverse order. Buffer pinning reuses cache entries by BO/direction, otherwise calls BO ops and tracks mappings in BO and cache lists with krefs.

## State And Persistence Behavior

Persistent state includes global idle client/driver/controller lists, per-controller logical devices, per-device idle/active subdevice lists, per-device client lists, `registered` flag, client `host` pointer and `usecount`, and BO mapping cache entries. Device release removes subdevices, returns clients to idle lists, and frees the logical device. Suspend/resume recursively walks parent clients and uses `usecount` to only call ops on first resume/last suspend.

## Dependencies And Integration Points

It depends on Linux driver core bus registration, OF matching and uevents, debugfs/seq_file, DMA mask/segment helpers, host1x public headers, and BO ops supplied by host1x clients. It integrates host1x controller drivers, logical subsystem drivers such as Tegra DRM, and individual engine clients.

## Risks And Test Signals

Risks include complex list movement under multiple locks, partial DT recursion cleanup FIXME, adding logical devices with no subdevices, lifecycle races between client unregister and device deletion, suspend/resume underflow if callers mismatch references, and BO mapping cache stale entries if krefs are wrong. Test registration ordering permutations, missing/disabled DT subdevices, probe failure teardown, client unregister while bound, debugfs output, recursive parent suspend/resume, BO pin cache reuse, and unpin last-reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.c -->
