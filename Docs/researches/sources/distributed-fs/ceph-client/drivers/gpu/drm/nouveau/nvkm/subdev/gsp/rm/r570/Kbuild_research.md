# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/Kbuild

Purpose: adds R570 GSP-RM implementation objects to the Nouveau `nvkm-y` build.

Important entries: it builds `rm.o`, `gsp.o`, `client.o`, `fbsr.o`, `disp.o`, `fifo.o`, `gr.o`, and `ofa.o` from `nvkm/subdev/gsp/rm/r570/`.

Control flow and state: no runtime logic. Build inclusion makes the R570 API implementation available to RM selection code.

Dependencies and integration: relies on the kernel Kbuild aggregation for `nvkm-y`. The listed files use R570 protocol headers and reuse many R535 helpers where compatible.

Risks and tests: missing an object here would produce unresolved symbols or silently omit a callback implementation from the final driver. Test signals are successful kernel/module build with R570 enabled and symbol presence for `r570_*` API tables.
