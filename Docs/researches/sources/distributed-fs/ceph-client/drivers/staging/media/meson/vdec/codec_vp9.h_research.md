# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.h

Purpose: this header exports the VP9 codec operations object used by the Meson VDEC platform format tables.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_vp9_ops;`. The implementation provides callbacks for start, stop, ISR, threaded ISR, pending-buffer accounting, drain, and resume.

Control flow and integration: generic VDEC session code invokes `codec_vp9_ops` to start the HEVC-family hardware path, account for VP9-held reference frames during ESPARSER queuing, flush output on drain, resume after source changes, and dispatch decode IRQs.

State and persistence behavior: no state is defined here, but the ops table implies that VP9 private state is stored in `amvdec_session.priv` and remains active across frames and source-change resumes until stop.

Dependencies: depends on `struct amvdec_codec_ops` from `vdec.h` and on linking `codec_vp9.o` into `meson-vdec`.

Risks: a missing or mismatched ops declaration breaks platform format linkage. Since VP9 uses optional callbacks that generic code treats specially (`num_pending_bufs`, `drain`, `resume`), future ops changes must preserve these entries.

Test signals: compile/link tests for `codec_vp9_ops`; runtime VP9 format selection should exercise pending-buffer accounting, drain, resume, and IRQ callbacks.
