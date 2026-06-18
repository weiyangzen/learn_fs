# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.h

Purpose: declares the HEVC-engine VDEC operations exported by `vdec_hevc.c`.

Important APIs/types: includes `vdec.h` for `struct amvdec_ops` and declares `extern struct amvdec_ops vdec_hevc_ops`.

Control flow: none directly; consumers include the header to assign `&vdec_hevc_ops` in platform format tables.

State and persistence: no state.

Dependencies/integration: couples the HEVC hardware backend to `vdec_platform.c` and any future platform tables without exposing private register routines.

Risks: the exported object is non-const, so accidental mutation by another compilation unit would be possible though not expected by driver style.

Test signals: build coverage that includes both `vdec_hevc.c` and platform table users is sufficient; runtime coverage comes through formats that select `vdec_hevc_ops`.
