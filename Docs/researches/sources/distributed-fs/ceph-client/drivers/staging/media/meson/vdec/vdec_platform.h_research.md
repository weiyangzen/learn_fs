# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.h

Purpose: declares the platform contract for Amlogic Meson VDEC SoC variants.

Important APIs/types: `enum vdec_revision` identifies GXBB, GXL, GXLX, GXM, G12A, and SM1. `struct vdec_platform` stores a pointer to a format array, its count, and the revision. Extern declarations expose one platform descriptor per supported revision.

Control flow: none. Runtime users dereference selected descriptors to drive format enumeration and revision-specific hardware behavior.

State and persistence: immutable platform descriptors are defined in `vdec_platform.c`; no mutable state is declared here.

Dependencies/integration: includes `vdec.h` and forward-declares `struct amvdec_format`. The revision enum is consumed by engine backends such as `vdec_hevc.c` for clock and AO power differences.

Risks: appending revisions is safer than reordering because table initializers use enum values semantically. `num_formats` is `const u32` inside the struct, so descriptors are intended immutable.

Test signals: compile/link checks for all exported platform descriptors and runtime OF matching that picks the correct revision-specific table.
