# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb.c

## Purpose

`drm_sysfb.c` provides shared validation and format lookup helpers for DRM system framebuffer drivers.

## Important APIs, Types, and Functions

- `drm_sysfb_get_validated_int()`: validates a `u64` value against a caller maximum and `INT_MAX`.
- `drm_sysfb_get_validated_int0()`: additionally rejects zero values.
- `drm_sysfb_get_format()`: matches a generic `pixel_format` against a table of supported `drm_sysfb_format` entries and returns DRM format info.

## Control Flow

Concrete drivers call validation helpers while parsing firmware/platform metadata. Invalid values produce DRM warnings and `-EINVAL`. Format lookup linearly scans a table and warns when no compatible pixel layout exists.

## State and Persistence Behavior

This file is stateless. It exports helper symbols and module metadata only.

## Dependencies and Integration Points

It depends on kernel export/module/minmax/limits helpers, DRM logging, pixel-format helpers through the header, and all sysfb concrete drivers that parse firmware data.

## Risks and Edge Cases

- Return type is `int`; callers must treat negative values as errors and non-negative values as validated data.
- `max` should reflect the true destination field/resource limit; too-large maxima can still permit semantically invalid values.
- Format matching requires exact pixel mask equality.

## Test Signals

Unit-style tests should cover zero rejection, `INT_MAX` clamping, custom maxima, exact format matches, duplicate table ordering, and unsupported pixel formats.
