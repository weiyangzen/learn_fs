# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/event.h

Purpose: defines R535 RM event allocation and notification-control payloads plus the asynchronous post-event message format.

Important types: `NV0005_ALLOC_PARAMETERS` creates `NV01_EVENT_KERNEL_CALLBACK_EX` event objects, carrying parent client, source resource, event class, notify index, and callback data pointer. `NV2080_CTRL_EVENT_SET_NOTIFICATION_PARAMS` configures event actions such as repeat notification. `rpc_post_event_v17_00` is the message payload sent by GSP for posted events, including client handle, event handle, notify index, status, optional data, and notify-list flag.

Control flow and state: `gsp.c` registers `r535_gsp_msg_post_event()` for `POST_EVENT`. It looks up the low 16 bits of `hClient` in `gsp->client_id.idr`, scans the client's event list by `hEvent`, and invokes the event callback with `eventData`.

Dependencies and integration: used by RM event helpers and display/hotplug or other notification consumers. It connects firmware event delivery to Nouveau callback lists.

Risks and tests: message length validation is critical because `eventData[]` is flexible. Client/event handle mismatches produce dropped events. Tests should cover event allocation, notification enabling, hotplug/DP IRQ callbacks, and removal while events may be in flight.
