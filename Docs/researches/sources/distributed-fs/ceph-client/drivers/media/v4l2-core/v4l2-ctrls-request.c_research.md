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
