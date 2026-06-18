# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.c

Purpose: this file implements the `amvdec_ops` backend for the legacy VDEC_1 hardware block, used by MPEG-1/2 and H.264 style firmware. It powers/resets the block, loads microcode into IMEM, configures the VIFIFO stream buffer, integrates ESPARSER, and delegates codec-specific setup/stop to `amvdec_codec_ops`.

Important APIs and functions: `vdec_1_load_firmware()` requests the codec firmware, verifies at least 16 KiB microcode, copies it to coherent DMA memory, programs IMEM DMA registers, waits for DMA completion, and passes remaining firmware bytes to optional `load_extended_firmware()`. `vdec_1_stbuf_power_up()` initializes VLD VIFIFO registers from session DMA addresses. `vdec_1_conf_esparser()` writes VDEC_1-specific parser control. `vdec_1_start()` enables clocks, powers and de-isolates VDEC_1 using AO sysctrl and DOS registers, resets hardware, enables memories/clocks, loads firmware, runs codec start, enables mailbox IRQ, selects two-plane output for NV12M, starts firmware CPU, and settles. `vdec_1_stop()` calls an internal stop sequence and disables the clock.

Control flow: generic `vdec_poweron()` enables DOS parser/DOS clocks, then calls `vdec_1_start()`, then powers ESPARSER. Stop sets `should_stop`, waits for inactivity, optional codec drain, then calls `vdec_1_stop()`. If any start step fails, `__vdec_1_stop()` resets firmware state, masks IRQs, powers down memories and hardware, and calls codec stop if private state exists.

State and persistence: VDEC_1 state is almost entirely hardware state plus codec-private session data. Firmware microcode DMA memory is temporary during load. VIFIFO registers persist during streaming. AO power/isolation bits differ for SM1 versus older revisions. Codec private allocations are owned by codec stop.

Dependencies and integration points: depends on firmware API, clocks, AO regmap, DOS registers, VDEC helpers, ESPARSER configuration callback, and codec ops. It exports `vdec_1_ops` for platform format tables.

Risks: firmware DMA wait is a busy loop with a fixed 1000-iteration budget and no sleep, so hardware hangs become immediate errors. `static void *mc_addr` and `static dma_addr_t mc_addr_map` inside firmware load are unnecessary static state and could be confusing if concurrency were ever allowed. Power/isolation sequencing is revision-specific and should not be changed without hardware validation.

Test signals: firmware missing/too-small/DMA-hang cases, H.264 extended firmware load, MPEG startup, NV12M versus YUV420M output bit, SM1 power bits versus older bits, stop after partial start failure, and mailbox IRQ enablement.
