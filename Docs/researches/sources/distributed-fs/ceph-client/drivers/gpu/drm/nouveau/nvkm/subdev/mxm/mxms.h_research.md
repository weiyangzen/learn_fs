# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.h

## Purpose
Declares the MXMS parser interface and output-device descriptor structure used by MXM base and NV50 sanitization code.

## Important APIs, Types, And Functions
Defines `struct mxms_odev` with `outp_type`, `conn_type`, `ddc_port`, and `dig_conn`. Declares all exported parser helpers: `mxms_output_device`, `mxms_version`, `mxms_headerlen`, `mxms_structlen`, `mxms_checksum`, `mxms_valid`, and `mxms_foreach`.

## Control Flow
No executable control flow exists in this header.

## State And Persistence
No state is stored. The struct layout is the cross-file data contract for decoded MXMS ODS records.

## Dependencies And Integration Points
Includes `priv.h` for `struct nvkm_mxm`. Used by `base.c`, `mxms.c`, and `nv50.c`.

## Risks And Test Signals
Risk is interface drift between parser implementation and callers. Build tests catch signature mismatches; runtime DCB sanitization tests catch semantic mismatches in `mxms_odev` fields.
