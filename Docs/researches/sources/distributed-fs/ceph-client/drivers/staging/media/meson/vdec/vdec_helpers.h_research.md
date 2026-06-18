# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.h

Purpose: this header declares shared helper functions used across the Meson VDEC core, ESPARSER, hardware back ends, and codecs.

Important APIs: declarations cover canvas mapping (`amvdec_set_canvases()`), DOS/PARSER MMIO accessors and bit helpers, AM21C compressed-size helpers, destination-buffer completion by firmware index, direct buffer, or VIFIFO offset, timestamp add/remove, display-aspect-ratio to pixel-aspect conversion, source-change notification, and session abort.

Control flow and integration: codec start/resume uses canvas and AM21C helpers, ESPARSER uses timestamp helpers and parser MMIO accessors, codec IRQ handlers use destination completion helpers, and parsed metadata paths use PAR/source-change helpers. `amvdec_abort()` is the common fatal-error escape hatch for firmware or allocation failures.

State and persistence behavior: the header itself has no state, but its functions mutate central `amvdec_session` fields: canvas allocation arrays, timestamp list, sequence counters, pixel aspect, dimensions, min-buffer control, status, and VB2 queue error state.

Dependencies: includes `vdec.h`, which supplies core/session types and V4L2/vb2 dependencies. Implementation additionally requires Meson canvas, V4L2 events, and DMA-contig helpers.

Risks: helper signatures form a broad internal ABI; changing them requires edits across most driver files. Completion helpers assume caller-provided firmware indices and offsets are valid for current session mappings. Exported helper availability must stay aligned with the composite object list.

Test signals: build all codec files after signature changes; runtime tests should cover every helper family through MPEG/H.264/VP9 decode, source changes, EOS, and abort.
