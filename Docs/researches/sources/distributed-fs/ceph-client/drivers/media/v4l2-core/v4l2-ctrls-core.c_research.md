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
