# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.h

Purpose: this header exposes the VDEC_1 hardware backend operations table.

Important API: it includes `vdec.h` and declares `extern struct amvdec_ops vdec_1_ops;`. The implementation supplies start, stop, ESPARSER configuration, and VIFIFO level callbacks.

Control flow and integration: platform format descriptors use `vdec_1_ops` for codecs that run on the VDEC_1 hardware block. Generic `vdec.c` invokes these callbacks during power-on, power-off, parser setup, and VIFIFO free-space accounting.

State and persistence behavior: no state is declared here. Runtime hardware state is stored in registers and per-session VIFIFO fields defined in `vdec.h`.

Dependencies: depends on `struct amvdec_ops` from `vdec.h` and the `vdec_1.o` object being linked into the composite driver.

Risks: adding callbacks to `struct amvdec_ops` requires updating this implementation. The global ops object should be treated as immutable after initialization.

Test signals: compile/link symbol resolution and runtime format selection for MPEG/H.264 should show the generic core calling VDEC_1 start/stop and parser methods.
