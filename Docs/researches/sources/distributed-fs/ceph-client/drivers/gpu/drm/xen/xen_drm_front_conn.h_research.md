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
