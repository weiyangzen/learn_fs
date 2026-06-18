# sources/distributed-fs/ceph-client/drivers/block/rbd_types.h

## Purpose
Defines shared RBD on-disk object naming constants, lock/notify constants, object-map states, image flags, default object sizing, and packed v1 image header structures used by the kernel RBD driver.

## Important APIs, Types, And Functions
Format v2 constants include `RBD_HEADER_PREFIX`, `RBD_OBJECT_MAP_PREFIX`, `RBD_ID_PREFIX`, and `RBD_V2_DATA_FORMAT`. Locking constants are `RBD_LOCK_NAME`, `RBD_LOCK_TAG`, and `RBD_LOCK_COOKIE_PREFIX`. `enum rbd_notify_op` defines watch/notify operations for acquired lock, released lock, request lock, and header update.

Object-map states are `OBJECT_NONEXISTENT`, `OBJECT_EXISTS`, `OBJECT_PENDING`, and `OBJECT_EXISTS_CLEAN`. Image flags include `RBD_FLAG_OBJECT_MAP_INVALID` and `RBD_FLAG_FAST_DIFF_INVALID`.

Format v1 constants include `RBD_SUFFIX`, `RBD_V1_DATA_FORMAT`, `RBD_DIRECTORY`, `RBD_INFO`, object-order bounds, and header magic/version strings. `struct rbd_image_snap_ondisk` and `struct rbd_image_header_ondisk` are packed little-endian representations of v1 snapshot and header metadata.

## Control Flow
This header has no executable control flow. `rbd.c` includes it to generate object names, decode v1 headers, validate image format fields, identify lock and notify payloads, and interpret object-map states and invalid flags.

## State And Persistence Behavior
The constants describe persistent RADOS object layout and encoded metadata. v2 images use id, header, object-map, and data object prefixes. v1 images use a single `<name>.rbd` header and data object format. The packed structures are persisted in RADOS for v1 images and must remain ABI-compatible.

## Dependencies And Integration Points
Depends only on Linux fixed-width types. It is an integration contract between kernel RBD code, Ceph OSD class methods, userspace RBD tooling, and persisted RADOS metadata. Layout or value changes would affect compatibility with existing images.

## Risks
The packed v1 structures contain flexible snapshot arrays and little-endian fields; readers must validate lengths and counts before decoding. Changing any prefix, lock name, notify op value, object-map state, or header magic would break interoperability. Object order bounds affect assumptions about sector-sized I/O and memory sizing in the driver.

## Test Signals
Signals are indirect: successful mapping of v1 and v2 images, snapshot enumeration, object-map load/update, lock handoff notifications, and compatibility tests against images created by userspace `rbd` tools. Static ABI review is important for this header.
