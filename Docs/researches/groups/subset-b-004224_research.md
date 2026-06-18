# subset-b-004224 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-compat-ioctl32.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-compat-ioctl32.c

## Purpose
This file implements the V4L2 compat32 ioctl bridge: it lets 32-bit userspace applications use V4L2 devices on a 64-bit kernel by translating ABI structures whose layout differs because of pointer size, timestamp layout, or architecture-specific alignment. It is used as the `.compat_ioctl` implementation from `v4l2-dev.c` and forwards standard V4L2 ioctls into the normal unlocked ioctl path after translating arguments.

## Important APIs, types, and functions
The file defines 32-bit mirror structs for V4L2 ABI structures with embedded pointers or alignment-sensitive fields: `v4l2_window32`, `v4l2_format32`, `v4l2_create_buffers32`, `v4l2_standard32`, `v4l2_plane32`, `v4l2_buffer32`, optional `v4l2_buffer32_time32`, `v4l2_framebuffer32`, `v4l2_input32`, `v4l2_ext_controls32`, `v4l2_ext_control32`, optional `v4l2_event32`, optional `v4l2_event32_time32`, and `v4l2_edid32`.

Core conversion helpers are `get_v4l2_*32()` for copying and expanding user-provided 32-bit structures into native kernel ABI structures, and `put_v4l2_*32()` for copying native results back to 32-bit layout. `v4l2_compat_translate_cmd()` maps compat ioctl command numbers such as `VIDIOC_G_FMT32`, `VIDIOC_QBUF32`, and `VIDIOC_G_EXT_CTRLS32` to their native commands. `v4l2_compat_get_user()` and `v4l2_compat_put_user()` dispatch the per-ioctl fixed-argument conversions. `v4l2_compat_get_array_args()` and `v4l2_compat_put_array_args()` handle nested arrays such as multi-planar buffers and extended controls. `v4l2_compat_ioctl32()` is the exported entry point.

## Control flow
For a compat V4L2 ioctl, `v4l2_compat_ioctl32()` first checks that an unlocked ioctl implementation exists and that the `video_device` is still registered. For standard V4L2 ioctl numbers below `BASE_VIDIOC_PRIVATE`, it forwards to `file->f_op->unlocked_ioctl(file, cmd, compat_ptr(arg))`; private ioctls are delegated to the driver's `vdev->fops->compat_ioctl32` if available. Standard ioctl dispatch then uses the conversion callbacks in this file through the V4L2 ioctl layer.

The fixed-argument conversion path is command-driven. Format ioctls copy `type` first, then switch by `V4L2_BUF_TYPE_*` to copy only the union arm that applies. Buffer ioctls convert memory-specific union fields: MMAP/OVERLAY preserve offsets, USERPTR uses `compat_ptr()`, DMABUF preserves file descriptors, and multi-planar buffers preserve a compat pointer to the plane array for later array conversion. Extended controls copy the outer array descriptor and then convert each `struct v4l2_ext_control32`; pointer payload controls are detected via `ctrl_is_pointer()` so the nested payload pointer is not confused with scalar `value64`.

## State and persistence behavior
This file does not own long-lived device state. It is a transient ABI adapter that reads from and writes to userspace buffers and fills native temporary ioctl argument structures. The only persistent effects are the effects of the native ioctl it forwards to. Conversion routines intentionally zero native or compat structures before filling selected fields to avoid leaking uninitialized padding back to userspace. Time32 support and x86_64 event alignment support are compile-time conditional.

## Dependencies and integration points
It depends on `linux/compat.h`, `linux/videodev2.h`, `media/v4l2-dev.h`, `media/v4l2-fh.h`, `media/v4l2-ctrls.h`, and `media/v4l2-ioctl.h`. `ctrl_is_pointer()` integrates with `video_devdata()`, `file_to_v4l2_fh()`, control handlers, `v4l2_ctrl_find()`, and optionally the driver's `vidioc_query_ext_ctrl` operation. The exported `v4l2_compat_ioctl32()` is wired into the global V4L2 file operations in `v4l2-dev.c` under `CONFIG_COMPAT`.

## Risks
The major risk is ABI drift: every layout-sensitive userspace structure and ioctl command must remain in sync with `videodev2.h`. Multi-planar buffer conversion trusts the validated plane count passed through the native buffer structure and must keep array-size limits aligned with the caller. Extended control conversion is subtle because pointer controls are layout-compatible except for the payload pointer; changing payload semantics or `V4L2_CTRL_FLAG_HAS_PAYLOAD` handling can corrupt scalar values or leak stale pointers. Time32 and x86_64-specific layouts need architecture coverage. Any missed zeroing of padding or reserved fields could leak kernel stack contents.

## Test signals
Useful signals are compat ioctl tests from 32-bit userspace on a 64-bit kernel: format get/set/try across all buffer types, buffer query/qbuf/dqbuf/prepare for MMAP, USERPTR, DMABUF, and multi-planar modes, extended controls with scalar, string, compound, and dynamic-array payloads, EDID get/set, event dequeue under x86_64 and time32 configurations, and private ioctl fallback. Fuzzing invalid `type`, `memory`, `count`, `size`, and nested pointer values should confirm `-EINVAL`, `-EFAULT`, or `-ENOSPC` behavior without native ioctl side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-compat-ioctl32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-api.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-api.c

## Purpose
This file implements the V4L2 controls userspace API for querying, getting, trying, setting, logging, and subscribing to controls. It is the ABI-facing layer over the lower-level control core: it validates userspace `VIDIOC_G_EXT_CTRLS`, `VIDIOC_TRY_EXT_CTRLS`, `VIDIOC_S_EXT_CTRLS`, legacy `VIDIOC_G_CTRL`/`VIDIOC_S_CTRL`, `VIDIOC_QUERY_EXT_CTRL`, `VIDIOC_QUERYCTRL`, `VIDIOC_QUERYMENU`, control events, and control polling.

## Important APIs, types, and functions
`struct v4l2_ctrl_helper` ties each userspace `v4l2_ext_control` to its found `v4l2_ctrl_ref`, its cluster master reference, and the next control index in the same cluster. `prepare_ext_ctrls()` resolves control IDs, checks `which`, rejects old-style private controls for extended APIs, enforces disabled and min/max rules, normalizes pointer sizes, and builds cluster chains. `v4l2_g_ext_ctrls_common()` copies default, request, min, max, volatile, or current values to userspace. `try_set_ext_ctrls_common()` validates and optionally commits extended control changes.

Legacy helpers include `get_ctrl()`, `v4l2_g_ctrl()`, `set_ctrl()`, `set_ctrl_lock()`, and `v4l2_s_ctrl()`. Driver-facing helpers include `v4l2_ctrl_g_ctrl()`, `v4l2_ctrl_g_ctrl_int64()`, `__v4l2_ctrl_s_ctrl()`, `__v4l2_ctrl_s_ctrl_int64()`, `__v4l2_ctrl_s_ctrl_string()`, and `__v4l2_ctrl_s_ctrl_compound()`. Query and metadata functions are `v4l2_query_ext_ctrl()`, `v4l2_query_ext_ctrl_to_v4l2_queryctrl()`, `v4l2_queryctrl()`, and `v4l2_querymenu()`. Event helpers include `v4l2_ctrl_subscribe_event()`, `v4l2_ctrl_subdev_subscribe_event()`, `v4l2_ctrl_replace()`, `v4l2_ctrl_merge()`, and `v4l2_ctrl_poll()`.

## Control flow
Extended get/set begins by canonicalizing `cs->which` with `V4L2_CTRL_ID2WHICH()`. `prepare_ext_ctrls()` looks up each control under the handler lock, records the corresponding reference, validates availability, computes payload sizes, and links controls from the same cluster so the cluster is processed once through the master. For get, `v4l2_g_ext_ctrls_common()` rejects write-only controls, locks each master, refreshes volatile clusters through `g_volatile_ctrl` when appropriate, and copies the selected value source back to userspace.

For try/set, `try_set_ext_ctrls_common()` rejects attempts to modify default/min/max pseudo-values, prepares helpers, performs up-front validation for read-only/grabbed/scalar controls, locks each cluster master, resets `is_new`, copies userspace values through `user_to_new()`, validates pointer payloads after copy, and calls `try_or_set_cluster()`. If the handler is a request handler, successful sets copy new values into request storage through `new_to_req()` instead of immediately changing device state. Successful operations copy normalized values back to userspace.

The API explicitly documents best-effort atomicity: invalid values should fail before modifying controls, but driver or hardware errors during cluster commits can leave partial changes. `error_idx` communicates whether no controls were affected (`count`) or which index failed after earlier controls may have been processed.

## State and persistence behavior
This layer mutates `v4l2_ctrl` transient `p_new`, `is_new`, `new_elems`, and current values via core helpers when a set commits. It also mutates dynamic-array storage if a userspace payload is larger than the current allocation. It uses locks on control masters or handlers to serialize cluster operations. It can change control ranges and dimensions through `__v4l2_ctrl_modify_range()` and `__v4l2_ctrl_modify_dimensions()`, emitting events when value, range, or dimensions change. Event subscriptions are stored in each control's `ev_subs` list and are removed on unsubscribe or handler teardown.

## Dependencies and integration points
It depends on `v4l2-ctrls-priv.h` for internal helpers implemented by the core and request files. It integrates with the media request API by routing `V4L2_CTRL_WHICH_REQUEST_VAL` to `v4l2_g_ext_ctrls_request()` or `try_set_ext_ctrls_request()`. It uses `v4l2-event` for event queueing, `v4l2-dev` for debug context, and `v4l2-device`/subdev plumbing for log-status helpers. Query operations rely on names, flags, menus, and type information provided by `v4l2-ctrls-core.c` and `v4l2-ctrls-defs.c`.

## Risks
Cluster handling is subtle: controls may appear in any userspace order, and a bug in helper linking can cause duplicate commits or skipped controls. Dynamic-array resizing copies both new and current payloads into a new allocation and must preserve element counts exactly. Pointer payload validation happens after copying from userspace, so size normalization and `-ENOSPC` handling must be correct to avoid overrun or truncated ABI behavior. Volatile auto-clusters require careful transitions from auto to manual mode to avoid losing current hardware-derived values. The legacy single-control helpers only support integer-like controls, so using them with compound controls is intentionally rejected.

## Test signals
Strong tests include extended get/try/set with mixed clusters, repeated cluster members, disabled/read-only/write-only/grabbed controls, invalid `which`, zero-count class checks, string truncation, dynamic-array growth and `-ENOSPC`, pointer compound validation failures, volatile controls, auto-cluster manual transitions, request-valued controls, and error_idx behavior when driver `try_ctrl` or `s_ctrl` fails. Query tests should cover next-control iteration, compound/hidden controls, menu skip masks, empty menu entries, and event subscribe/merge/replace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-core.c

## Purpose
This file is the core implementation of the V4L2 controls framework. It owns control allocation, handler lifecycle, reference lookup, value storage, type operations, standard validation, event generation, clustering, auto-clustering, request value copying, control setup, status logging, and fwnode-derived control creation.

## Important APIs, types, and functions
Standard type operations are `v4l2_ctrl_type_op_equal()`, `v4l2_ctrl_type_op_init()`, `v4l2_ctrl_type_op_log()`, and `v4l2_ctrl_type_op_validate()`, collected in `std_type_ops`. Compound initialization and validation cover MPEG-2, FWHT, H.264, VP8, VP9, HEVC, AV1, HDR10, area, and rectangle controls. Event helpers are `send_initial_event()` and `send_event()`.

Value-copy helpers are `cur_to_new()`, `new_to_cur()`, `new_to_req()`, `cur_to_req()`, and `req_to_new()`. Handler and reference APIs include `v4l2_ctrl_handler_init_class()`, `v4l2_ctrl_handler_free()`, `find_ref()`, `find_ref_lock()`, `v4l2_ctrl_find()`, and `handler_new_ref()`. Control constructors include `v4l2_ctrl_new_custom()`, `v4l2_ctrl_new_std()`, `v4l2_ctrl_new_std_menu()`, `v4l2_ctrl_new_std_menu_items()`, `v4l2_ctrl_new_std_compound()`, and `v4l2_ctrl_new_int_menu()`. Cluster and commit APIs include `v4l2_ctrl_cluster()`, `v4l2_ctrl_auto_cluster()`, `update_from_auto_cluster()`, `try_or_set_cluster()`, `v4l2_ctrl_activate()`, `__v4l2_ctrl_grab()`, and setup/logging helpers.

## Control flow
Control creation enters through one of the public constructors. Standard constructors use `v4l2_ctrl_fill()` and menu helpers to derive name/type/range/flags, then call the internal `v4l2_ctrl_new()`. That function computes array dimensions and element size, validates ranges, allocates the control and optional payload buffers, initializes current and new values, adds a reference to the handler, and links the control into the handler-owned list. `handler_new_ref()` also auto-adds control-class controls and maintains both a sorted list and a hash bucket chain.

Set operations from the API layer eventually call `try_or_set_cluster()` with the cluster master locked. It fills missing new values from current values, rejects grabbed controls again, calls driver `try_ctrl`, checks if anything changed, calls driver `s_ctrl` if this is a real set, then commits each new value to current storage with `new_to_cur()`. Commit emits value/flag events and optional notify callbacks. Auto-clusters update inactive/volatile flags when switching between auto and manual modes.

Validation is type-specific. Scalar controls are rounded or clamped to range where appropriate, booleans are normalized, bitmasks are masked, menus enforce range and skip masks, strings enforce min/step length, and compound controls perform codec-structure semantic checks and zero reserved or padding fields so memcmp-based equality is deterministic.

## State and persistence behavior
`struct v4l2_ctrl_handler` persists a mutex, sorted reference list, hash buckets, cached lookup ref, owned control list, request lists, and error state. Each `struct v4l2_ctrl` persists metadata, flags, cluster linkage, current value (`p_cur`/`cur`), staged value (`p_new`/`val`), array allocation state, defaults/min/max payloads, event subscribers, and driver private data. Request values are stored per `struct v4l2_ctrl_ref` in `p_req`, `p_req_valid`, element counts, and allocation-error markers.

The file carefully distinguishes current, new, and request states. Current state is the live committed value. New state is a staging buffer for validation and driver callbacks. Request state is an independent per-request snapshot. Dynamic arrays can reallocate both control-owned current/new storage and request-owned payload storage.

## Dependencies and integration points
It depends on `media/v4l2-ctrls.h`, `media/v4l2-event.h`, `media/v4l2-fwnode.h`, and the private header. It is called by `v4l2-ctrls-api.c` for userspace operations and by `v4l2-ctrls-request.c` for request setup/completion. Drivers provide `struct v4l2_ctrl_ops` callbacks such as `try_ctrl`, `s_ctrl`, and `g_volatile_ctrl`. Fwnode integration creates camera orientation and sensor rotation controls from parsed device properties.

## Risks
This is high-risk shared infrastructure. Incorrect reserved-field normalization can break unchanged detection or userspace ABI expectations for stateless codec controls. Dynamic-array allocation paths must maintain matching `p_new`, `p_cur`, `elems`, `new_elems`, and allocation counts; mistakes can lead to stale copies or out-of-bounds accesses. Locking is split across handler locks and control/master locks, so request, event, and cluster paths must avoid deadlocks and races. `handler_new_ref()` duplicate handling and class-control auto-creation are subtle. `try_or_set_cluster()` best-effort semantics mean driver `s_ctrl` failures can leave hardware and software state inconsistent if a driver partially applies settings before failing.

## Test signals
Tests should cover constructor validation, automatic class controls, sorted lookup and cached lookup, duplicate references, handler merge filtering, scalar rounding, menu skip masks, string length rules, every compound validator family, default/min/max generation, event delivery and feedback suppression, notifications, auto-cluster flag transitions, volatile controls, dynamic-array growth/shrink cases, request copy allocation failures, handler teardown with event subscribers and request objects, and fwnode orientation/rotation creation. Compile coverage across codec control types is important because many validators are only exercised by stateless decoder drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-defs.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-defs.c

## Purpose
This file centralizes standard V4L2 control metadata. It maps control IDs to menu label tables, integer-menu value tables, human-readable names, default type/range/step/default values, and standard control flags. The constructors in `v4l2-ctrls-core.c` use it to build standard controls without each driver duplicating metadata.

## Important APIs, types, and functions
`v4l2_ctrl_get_menu(u32 id)` returns a static NULL-terminated string table for menu controls such as MPEG audio/video options, camera exposure modes, color effects, H.264/HEVC/AV1 profiles and levels, flash modes, digital-video ranges, detection modes, and camera orientation. Empty strings in returned menus represent unsupported entries that query/validation code must skip.

`v4l2_ctrl_get_int_menu(u32 id, u32 *len)` returns static `s64` value arrays for integer-menu controls, currently VPX partition and reference-frame counts, and reports the table length. `v4l2_ctrl_get_name(u32 id)` maps a broad set of user, codec, camera, FM radio, flash, JPEG, image source/processing, DV, tuner, detection, stateless codec, and colorimetry control IDs to stable display names. `v4l2_ctrl_fill()` derives the default `enum v4l2_ctrl_type`, range, step, default value, and flags for a control ID.

## Control flow
All exported functions are switch-based metadata lookups. Standard control construction typically calls `v4l2_ctrl_fill()` first. That function initializes `name` from `v4l2_ctrl_get_name()`, clears flags, classifies IDs by type, applies special ranges/defaults for controls that need them, then applies secondary flag classifications such as `UPDATE`, `SLIDER`, `READ_ONLY`, `WRITE_ONLY`, `EXECUTE_ON_WRITE`, `VOLATILE`, `MODIFY_LAYOUT`, and `DYNAMIC_ARRAY`.

Menu constructors then call `v4l2_ctrl_get_menu()` or `v4l2_ctrl_get_int_menu()` to obtain the legal options. Query-menu and validation paths in the API/core files later use the returned tables, skip masks, and default range information to accept or reject userspace indices.

## State and persistence behavior
This file stores no mutable runtime state. All menus and integer menus are function-local static constant arrays. The outputs are metadata pointers and scalar values consumed by control allocation. Because the returned pointers refer to static storage, callers must not modify them and do not own their lifetime.

## Dependencies and integration points
It depends on `media/v4l2-ctrls.h` for all control IDs, types, flags, and constants. It is used by `v4l2-ctrls-core.c` constructors and indirectly by `v4l2-ctrls-api.c` query and validation paths. It must stay aligned with public UAPI definitions in `videodev2.h` and `v4l2-controls.h`; comments explicitly require case ordering to match those headers in several switch blocks.

## Risks
The main risk is metadata drift. If a new UAPI control is added without a matching name/type/range/menu entry, standard constructors may create an integer control by default or fail later. Wrong type classification can expose the wrong ABI shape. Wrong ranges or defaults can reject valid applications or permit invalid hardware settings. Menu arrays must remain ordered to match enum values; inserting or reordering labels breaks userspace-visible meaning. Dynamic-array flags for stateless codec controls must match the payload semantics expected by request and validation code.

## Test signals
Coverage should verify that every standard control ID in the supported headers has the expected name, type, min/max/step/default, flags, and menu table where applicable. Menu tests should check NULL termination, skipped or empty entries, integer-menu lengths, and constructor rejection when a standard menu is missing. ABI regression tests should compare known control metadata for representative user, camera, codec, stateless codec, and DV controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-defs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-priv.h

## Purpose
This private header defines internal helpers and cross-file prototypes for the V4L2 controls framework implementation. It is shared by the controls API, core, and request files, but is not a public driver-facing header.

## Important APIs, types, and functions
The `dprintk(vdev, fmt, ...)` macro emits control debug messages when the target `video_device` has `V4L2_DEV_DEBUG_CTRL` enabled. `has_op(master, op)` and `call_op(master, op)` safely test and invoke optional `struct v4l2_ctrl_ops` callbacks on a cluster master. `node2id()` maps a list node in a handler's sorted reference list to its control ID.

Small inline helpers encode common control-state tests: `is_cur_manual()` checks whether an auto-cluster master is currently in manual mode, `is_new_manual()` checks whether the staged value would switch to manual mode, and `user_flags()` exposes kernel flags to userspace while adding `V4L2_CTRL_FLAG_HAS_PAYLOAD` for pointer controls.

The prototype block declares internal functions implemented by `v4l2-ctrls-core.c`, `v4l2-ctrls-api.c`, and `v4l2-ctrls-request.c`: value-copy helpers, event helpers, reference lookup, range checking, cluster update/commit, common get/set API paths, and request API paths.

## Control flow
There is no standalone runtime flow in this header. It shapes control flow by making the same helper semantics available across the three implementation files. For example, the API file uses `is_cur_manual()` and `update_from_auto_cluster()` before setting volatile auto-clusters; the core file uses `user_flags()` when filling control events; the request file uses `req_to_new()`, `cur_to_req()`, `new_to_req()`, and `try_or_set_cluster()` to apply queued request controls.

## State and persistence behavior
The header owns no storage. Its helpers inspect existing `struct v4l2_ctrl`, `struct v4l2_ctrl_ref`, and `struct video_device` fields. It is part of the internal consistency contract for current/new/request values, control flags, manual-mode detection, and callback invocation.

## Dependencies and integration points
It expects the including C files to have the V4L2 control, file-handle, and video-device types available via public media headers. It links the internal implementation units together without exposing these helpers to external modules. Changes here can affect all control paths: normal ioctl get/set, request setup/completion, event delivery, and handler lifecycle.

## Risks
Because this header defines shared internal semantics, small changes have broad impact. `call_op()` assumes callbacks take the master control as their argument and return zero when missing; changing that convention would affect volatile, try, and set paths. `user_flags()` determines userspace-visible `HAS_PAYLOAD`; missing it would break pointer control queries. Manual-mode helpers assume auto-cluster masters store integer current/staged values in `cur.val` and `val`. Prototypes must remain synchronized with definitions to avoid accidental ABI or locking contract mismatches inside the controls framework.

## Test signals
There are no direct tests for the header, but good indirect signals are successful compilation of `v4l2-ctrls-api.c`, `v4l2-ctrls-core.c`, and `v4l2-ctrls-request.c`, plus behavioral tests for control debug logging, pointer-control query flags, auto-cluster manual transitions, request setup/completion, and callback invocation when optional ops are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-request.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-request.c

## Purpose
This file implements V4L2 control integration with the media request API. It lets applications stage control values into a `media_request`, apply those controls when the request is queued, and later read completed request control values. It also manages per-request cloned control handlers and their lifecycle as media request objects.

## Important APIs, types, and functions
Initialization and cleanup helpers are `v4l2_ctrl_handler_init_request()` and `v4l2_ctrl_handler_free_request()`. Request object callbacks are `v4l2_ctrl_request_queue()`, `v4l2_ctrl_request_unbind()`, `v4l2_ctrl_request_release()`, collected in `req_ops`. `v4l2_ctrl_request_clone()` clones references from a main handler into a request handler, skipping references inherited from other devices. Lookup helpers are `v4l2_ctrl_request_hdl_find()` and `v4l2_ctrl_request_hdl_ctrl_find()`.

Binding and object lookup are handled by `v4l2_ctrl_request_bind()` and `v4l2_ctrls_find_req_obj()`. Userspace request get/set paths are `v4l2_g_ext_ctrls_request()` and `try_set_ext_ctrls_request()`. Driver-facing lifecycle functions are `v4l2_ctrl_request_setup()` for applying queued request controls to hardware/software state and `v4l2_ctrl_request_complete()` for storing completed control state back into the request.

## Control flow
When a userspace set/try call uses `V4L2_CTRL_WHICH_REQUEST_VAL`, `try_set_ext_ctrls_request()` validates the media device and request fd, obtains and locks the request for update, finds or creates a request control-handler object, then delegates to `try_set_ext_ctrls_common()`. The common path writes staged values into the request handler's per-reference `p_req` storage through `new_to_req()` instead of immediately committing to the main handler.

When a driver queues a request, `v4l2_ctrl_request_setup()` requires `MEDIA_REQUEST_STATE_QUEUED`, finds the request object, skips completed objects, then walks request refs by cluster. If any control in a cluster has new request data, it copies request values to each control's new buffer with `req_to_new()`, handles volatile auto-cluster manual transitions, and calls `try_or_set_cluster()` to apply the cluster.

On completion, `v4l2_ctrl_request_complete()` finds or creates a request handler so completed state can be queried even for requests that did not originally set controls. It snapshots volatile controls through `g_volatile_ctrl` and `new_to_req()`, snapshots unset controls from current values through `cur_to_req()`, removes the handler from the queued list, marks the request object complete, and drops its object reference.

## State and persistence behavior
The main control handler tracks all bound request handlers in `requests` and queued request handlers in `requests_queued`; `request_is_queued` records list membership. Each request handler is a separate `v4l2_ctrl_handler` bound as a `media_request_object` whose `priv` points to the main handler. Request refs store per-control request payloads and validity flags. Object bind/get/put and request lock calls coordinate lifetime with the media request core.

## Dependencies and integration points
It depends on `media/v4l2-ctrls.h`, `media/v4l2-dev.h`, `media/v4l2-ioctl.h`, the media request object API, and private control helpers. It integrates tightly with `v4l2-ctrls-api.c` for request-valued extended controls and with `v4l2-ctrls-core.c` for cloning refs, copying request/current/new values, auto-cluster updates, and cluster commits. Device drivers call setup before processing a request and complete after hardware processing.

## Risks
Request state and object lifetime are subtle. `v4l2_ctrls_find_req_obj()` returns `-ENOMEM` for completed requests that lack a stored control object, because that means completion failed to allocate a snapshot handler; callers must surface that accurately. Dynamic-array request allocation can fail and is tracked per-ref, so completed request reads may return `-ENOMEM`. Setup walks clusters and uses `find_ref()` for each member; missing refs or inconsistent cloned handlers would break request application. Lock ordering between media request locks, main handler locks, and control locks must remain consistent. Release serialization in `v4l2-dev.c` is important because request queueing and stream cancellation can otherwise race.

## Test signals
Tests should cover setting controls into an updating request, trying request controls, setup on queued requests, no-control requests, completed request reads, volatile control snapshots at completion, auto-cluster transitions inside requests, dynamic-array request payloads, invalid/missing request fds, media-device absence, completed-object `-EBUSY`, allocation-failure paths, unbind/release cleanup, and freeing a main handler while outstanding request handlers are bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dev.c

## Purpose
This file implements the core Video4Linux2 character-device layer. It registers the global V4L2 char-device region and class, allocates and releases `struct video_device`, manages minor/device-node allocation, exposes sysfs/debugfs state, wraps file operations, computes valid ioctl bitmaps, registers media-controller entities/interfaces, unregisters devices, tracks V4L2 priority state, and provides media-pipeline convenience helpers.

## Important APIs, types, and functions
Device allocation/lifetime APIs are `video_device_alloc()`, `video_device_release()`, `video_device_release_empty()`, `__video_register_device()`, and `video_unregister_device()`. `video_devdata()` maps an open file to `video_devices[iminor(file_inode(file))]`. Global state includes `video_devices[VIDEO_NUM_DEVICES]`, `videodev_lock`, and `devnode_nums[]` bitmaps.

File-operation wrappers are `v4l2_open()`, `v4l2_release()`, `v4l2_read()`, `v4l2_write()`, `v4l2_poll()`, `v4l2_ioctl()`, `v4l2_mmap()`, optional `v4l2_get_unmapped_area()`, and the `v4l2_fops` table, with compat ioctl support wired to `v4l2_compat_ioctl32()`. Priority helpers are `v4l2_prio_init()`, `v4l2_prio_change()`, `v4l2_prio_open()`, `v4l2_prio_close()`, `v4l2_prio_max()`, and `v4l2_prio_check()`. `determine_valid_ioctls()` precomputes which standard ioctl numbers are supported by a device.

Media-controller and pipeline helpers include `video_register_media_controller()`, `video_device_pipeline_start()`, `__video_device_pipeline_start()`, `video_device_pipeline_stop()`, `__video_device_pipeline_stop()`, `video_device_pipeline_alloc_start()`, and `video_device_pipeline()`. Module lifecycle is `videodev_init()` and `videodev_exit()`.

## Control flow
`__video_register_device()` validates required callbacks and fields, initializes file-handle tracking, chooses a device-name base from `vfl_devnode_type`, inherits parent, control handler, and priority state from `v4l2_device` when unset, then allocates a free device-node number and minor under `videodev_lock`. It computes valid ioctl bits, allocates and adds a `cdev`, initializes and registers the sysfs device, increments the parent `v4l2_device` refcount, optionally registers media-controller entities/interfaces, and finally sets `V4L2_FL_REGISTERED` to allow opens.

Open is serialized with unregister by `videodev_lock`: it checks the registered bit, gets a device reference, calls the driver's open, and verifies the driver uses `v4l2_fh`. Release optionally serializes with the media request queue mutex before calling the driver release, then drops the device reference. Read/write/poll/ioctl/mmap wrappers reject unregistered devices and otherwise delegate to driver fops with debug logging. Unregister clears `V4L2_FL_REGISTERED`, wakes events, and calls `device_unregister()`. The final device release removes global lookup state, deletes the cdev, clears the node bitmap, unregisters media-controller objects, calls the driver release callback for `video_device`, and drops the `v4l2_device` reference when safe.

`determine_valid_ioctls()` builds a bitmap from device capabilities, direction, type, ioctl ops, streaming support, media-controller mode, EDID support, and control-handler availability. The final bitmap subtracts driver-specified overrides so drivers can mark auto-detected ioctls as invalid.

## State and persistence behavior
Persistent global state is the registered major range, class, debugfs root, global minor table, and node bitmaps. Each registered `video_device` persists its minor, node number, index, flags, cdev, sysfs device, inherited handlers, media-controller objects, and file-handle list. `V4L2_FL_REGISTERED` gates new operations. Reference counting through `get_device()`/`put_device()` keeps devices alive while files are open even after unregister starts. Priority state is persisted in atomics per priority level.

## Dependencies and integration points
It depends on Linux char-device, sysfs, debugfs, module, uaccess, and media headers. It integrates with `v4l2-ioctl.c` through valid ioctl bitmaps and driver `v4l2_ioctl_ops`; with `v4l2-fh` by requiring drivers to use file handles; with the compat layer through `.compat_ioctl`; with `v4l2-event` on unregister and poll; with the media request API through release serialization; and with the media controller framework through entity/interface registration and pipeline helpers.

## Risks
Registration and teardown are race-sensitive. The registered bit, global table, cdev lifetime, sysfs lifetime, and device references must remain ordered so open cannot race use-after-free. Error cleanup after partial registration must undo node allocation and cdev state correctly. `determine_valid_ioctls()` is large and capability-sensitive; missing a bit can hide valid ioctls, while setting an unsupported bit exposes dead operations to userspace. Media-controller registration failure is computed but registration still sets the device registered bit after calling it, so callers rely on return handling inside the function path. Request release serialization depends on `v4l2_device_supports_requests()` and a valid media-device request mutex. Fixed minor ranges and non-fixed minor allocation have different assumptions and need both configuration paths covered.

## Test signals
Useful tests include register/unregister/open races, failed registration cleanup at cdev and device-register stages, fixed and dynamic minor allocation, repeated unregister, sysfs attribute reads/writes, debugfs root creation/removal, fop delegation on registered/unregistered devices, request-aware release locking, compat ioctl availability under `CONFIG_COMPAT`, valid ioctl bitmap generation for video, VBI, radio, SDR, touch, metadata, EDID, streaming, and media-controller devices, priority open/change/close behavior, and media pipeline helpers with one-pad and invalid-pad entities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dev.c -->
