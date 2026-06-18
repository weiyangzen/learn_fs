# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/priv.h

Purpose: private FIFO interface header tying chip-specific FIFO implementations to the common FIFO engine. It defines `struct nvkm_fifo_func`, nested MMU fault, channel-group, and channel descriptors, and exports cross-generation helper declarations.

Important APIs and data: `struct nvkm_fifo_func` contains callbacks for destruction, CHID/runqueue/runlist creation, init, PBDMA init, interrupt handling, MMU fault parsing/recovery, pause/start, non-stall events, and selected runlist/runqueue/engine/channel/group function tables. It declares constructors including `nvkm_fifo_new_()` and `r535_fifo_new()`, plus exported helpers from NV04, NV50, GF100, GK104, GK110, GK208, GM107, GM200, GV100, TU102, GA100, and GB202 paths.

Control flow: chip files fill an `nvkm_fifo_func` table, then pass it to the common constructor. The common FIFO layer invokes callbacks to size allocators, create runqueues/runlists, initialize hardware, route interrupts, expose NVIF channel/group classes, and bind engine/channel behavior.

State and persistence: the header defines no storage itself. It specifies the callback contract that controls runtime state in `struct nvkm_fifo`, `nvkm_runl`, `nvkm_runq`, `nvkm_cgrp`, and `nvkm_chan`.

Dependencies and integration: includes public FIFO engine and enum definitions, and references fault, event, object, memory, runlist, runqueue, channel, group, and engine structures. It is the integration point for both nouveau-managed and R535/GSP-managed FIFO construction.

Risks: callback tables must be internally consistent; missing callbacks can be valid for old hardware but fatal for newer helpers expecting them; declarations couple many generations, so signature changes have broad blast radius.

Test signals: full driver build is the main signal. Runtime signals include each chip constructor resolving all symbols, correct NVIF class exposure from `.cgrp` and `.chan`, and expected interrupt/fault callbacks invoked for each device generation.
