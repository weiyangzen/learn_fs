# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/conn.c

## Purpose
This file wraps NVIF display connector objects and hotplug event creation.

## Important APIs, Types, and Functions
Public functions are `nvif_conn_ctor`, `nvif_conn_dtor`, and `nvif_conn_event_ctor`.

## Control Flow
Connector construction sends an `NVIF_CLASS_CONN` new request with an ID, stores the ID, and translates firmware/kernel connector type values into NVIF connector info enums. Event construction builds an event argument with requested HPD types and creates an event object tied to the connector ID.

## State and Persistence Behavior
State lives in the `nvif_conn` object, connector ID, translated connector type, and optional event object.

## Dependencies and Integration Points
It depends on NVIF display objects, event construction, connector class ABI, and display hotplug handling.

## Risks
Unknown connector types are silently left at default values. Event type masks must match backend-supported HPD bits.

## Test Signals
Signals include connector enumeration, type translation, HPD event creation/block/allow, and destructor cleanup.
