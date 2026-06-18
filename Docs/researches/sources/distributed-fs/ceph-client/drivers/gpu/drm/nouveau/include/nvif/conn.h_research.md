# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/conn.h

## Purpose
Declares the NVIF display connector object and connector event constructor.

## Important APIs, Types, And Functions
Defines `struct nvif_conn` with object handle, DCB connector id, and connector type enum; exports `nvif_conn_ctor/dtor`, `nvif_conn_id`, and `nvif_conn_event_ctor`.

## Control Flow
Display enumeration constructs connector objects from display masks. Event construction attaches hotplug or connector notifications to an NVIF event.

## State And Persistence
Connector object state persists while the DRM connector is represented and stores immutable id/type information.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/event.h`, and `struct nvif_disp`; integrates with DRM connector creation and hotplug handling.

## Risks
Wrong connector id/type mapping can create incorrect DRM connector types or miss HPD events.

## Test Signals
Connector enumeration, hotplug events, DVI/HDMI/DP/eDP classification, and teardown tests validate behavior.
