# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.h

Purpose: declares the shared HSI/HST transform entity wrapper.

Important APIs and types: defines `HSIT_PAD_SINK`, `HSIT_PAD_SOURCE`, `struct vsp1_hsit` with embedded common entity and `inverse` direction flag, `to_hsit()`, and `vsp1_hsit_create()`.

Control flow role: `vsp1_drv.c` creates one inverse HSI and one non-inverse HST entity. `vsp1_hsit.c` uses `inverse` to select media-bus code direction and control register.

State and persistence: `inverse` is immutable after construction. All mutable format and graph state is stored by the embedded `vsp1_entity`.

Dependencies and integration: includes media entity/V4L2 subdev and common entity declarations.

Risks and test signals: callers must pass the correct direction flag. Test both generated entity names/types and pad format behavior.
