# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk20a.c

Purpose: defines the GK20A FIFO function table, largely reusing GK208/GK110/GK104 code for the Tegra Kepler variant.

Important APIs and data: `gk20a_fifo` selects `nv50_fifo_chid_nr`, GK110 CHID/CGID construction, GF100 runqueue counting, GK104 runlist construction/init/interrupt handling, GK110 runlist/group/channel functions, GK208 runqueue behavior, and `KEPLER_CHANNEL_GPFIFO_A`. `gk20a_fifo_new()` passes this table to `nvkm_fifo_new_()`.

Control flow: no local runtime logic exists beyond function-table selection. All channel lifecycle, runlist updates, interrupts, and recovery are delegated to inherited helpers.

State and persistence: all state is inherited runtime FIFO state. The table does not enable a user-visible channel-group class, but uses `gk110_cgrp` internally.

Dependencies and integration: depends on the Kepler helper stack and NVIF Kepler channel class. It integrates through the common FIFO constructor.

Risks: being purely declarative makes correctness dependent on selecting helpers that match GK20A hardware; using `nv50_fifo_chid_nr` limits channels to 128, which must match the target integration; absent local comments make hardware rationale external.

Test signals: probe GK20A, create GPFIFO channels, verify inherited interrupts do not report unsupported bits, and confirm runlist/channel allocation limits match hardware.
