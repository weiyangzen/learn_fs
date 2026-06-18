# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.h

Purpose: this header declares the Meson ESPARSER interface used by the core VDEC driver and codec/hardware setup code.

Important APIs: `esparser_init()` binds IRQ/reset resources during platform probe. `esparser_power_up()` configures parser hardware for a session after VDEC power-on. `esparser_queue_eos()` writes a codec-provided EOS byte sequence into the parser. `esparser_queue_all_src()` is the work handler that drains queued OUTPUT buffers into ESPARSER when capacity allows. `ESPARSER_MIN_PACKET_SIZE` defines the 4 KiB minimum packet padding threshold required to trigger VDEC IRQs reliably.

Control flow and integration: `vdec_probe()` calls `esparser_init()`, `vdec_poweron()` calls `esparser_power_up()`, V4L2 m2m scheduling queues `esparser_queue_all_src()` as work, and decoder stop commands use `esparser_queue_eos()` when the codec provides an EOS sequence rather than a custom drain callback.

State and persistence behavior: the header does not declare state. Implementation state is split between hardware parser registers, global parser wait state, and `amvdec_session` VIFIFO/timestamp fields.

Dependencies: includes `linux/platform_device.h` and `vdec.h` for core/session types. Implementation relies on reset, IRQ, parser MMIO, and vb2 DMA APIs.

Risks: callers must ensure the session has allocated and configured VIFIFO memory before calling `esparser_power_up()` or queueing source buffers. EOS data must remain valid for the requested length.

Test signals: platform probe resource acquisition, parser power-up during stream start, workqueue scheduling on source/capture buffer events, and EOS paths for codecs that expose `eos_sequence`.
