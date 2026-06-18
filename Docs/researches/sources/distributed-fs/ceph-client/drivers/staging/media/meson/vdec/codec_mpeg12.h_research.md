# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.h

Purpose: this header exports the MPEG-1/MPEG-2 codec operations object for the Meson VDEC driver.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_mpeg12_ops;`. The implementation supplies start/stop, ISR/threaded ISR, recycle, and EOS callbacks.

Control flow and integration: platform format tables reference this object for MPEG-1/2 OUTPUT formats. Generic VDEC code invokes the callbacks during VDEC_1 firmware startup, IRQ dispatch, recycle-thread execution, decoder-command stop, and stream shutdown.

State and persistence behavior: no state is declared here. The implementation attaches `struct codec_mpeg12` to `amvdec_session.priv` and releases its DMA workspace through the stop callback.

Dependencies: depends on the `amvdec_codec_ops` definition from `vdec.h` and link inclusion of `codec_mpeg12.o`.

Risks: ops signature drift must be reflected in both declaration and implementation. A mutable global ops object can be corrupted by unintended writes, though normal code treats it as a static callback table.

Test signals: link-time symbol resolution and runtime selection of MPEG formats should demonstrate that `codec_mpeg12_ops` is reachable and all expected callbacks are non-NULL.
