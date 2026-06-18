# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.h

Purpose: this header exports the H.264 codec operations object to the Meson VDEC platform/format tables.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_h264_ops;`. The implementation fills this ops table with `start`, `stop`, `load_extended_firmware`, `isr`, `threaded_isr`, `can_recycle`, `recycle`, `eos_sequence`, and `resume`.

Control flow and integration: platform format descriptors reference `codec_h264_ops` when an OUTPUT pixel format is H.264. Generic `vdec.c` calls these callbacks during stream start, IRQ handling, source-change resume, recycle-thread processing, drain/EOS, and stop.

State and persistence behavior: the header does not define state, but the ops table creates the contract that H.264 private state will be attached to `amvdec_session.priv` by the codec implementation and released through the stop callback.

Dependencies: depends on `struct amvdec_codec_ops` from `vdec.h`; it must be linked with `codec_h264.o` in the same composite module.

Risks: because the exported object is mutable, accidental writes by other code would affect all sessions. Signature drift in `struct amvdec_codec_ops` requires updating both this declaration and the implementation initializer.

Test signals: compile/link tests should catch missing `codec_h264_ops`. Runtime tests should select the H.264 format and verify generic VDEC code reaches all implemented callbacks.
