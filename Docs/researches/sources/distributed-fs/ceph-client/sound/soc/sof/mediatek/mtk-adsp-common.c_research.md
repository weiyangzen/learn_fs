# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.c

Purpose: Provides shared MediaTek ADSP SOF helpers for panic dumps, mailbox IPC send/reply/request handling, BAR mapping, and PCM stream pointer behavior.

Important APIs: `mtk_adsp_dump()` reads Xtensa oops, panic info, and stack from mailbox/debug offsets and prints with `sof_print_oops_and_stack()`. `mtk_adsp_send_msg()` writes a SOF IPC message to `host_box.offset` then rings `mtk_adsp_ipc_send()`. `mtk_adsp_handle_reply()` processes replies under `sdev->ipc_lock`. `mtk_adsp_handle_request()` distinguishes panic magic from normal RX, invokes `snd_sof_ipc_msgs_rx()`, and sends a response doorbell. `mtk_adsp_get_bar_index()` maps firmware block type to BAR index. `mtk_adsp_stream_pcm_hw_params()` enables continuous position updates; `mtk_adsp_stream_pcm_pointer()` reads `sof_ipc_stream_posn` through IPC message data and converts host bytes to frames.

Control flow: IPC send is mailbox write then AP-to-ADSP request. Reply interrupt enters SOF reply processing. Request interrupt reads panic code from debug box, handles fatal panic or normal RX, then acknowledges DSP. Pointer lookup finds the SOF PCM by DAI ID, reads stream position for the stream, caches it, and returns frames.

Dependencies and integration: Consumed by MT8186/MT8195 `snd_sof_dsp_ops`; depends on `mtk-adsp-ipc`, SOF mailbox helpers, Xtensa oops structures, SOF client audio lists, and ALSA PCM conversion.

Risks: Panic detection assumes debug box offset +4 contains a panic code. `mtk_adsp_get_registers()` rejects oversized architecture headers but does not zero partial outputs. Pointer lookup returns 0 on missing PCM or read failure, which can hide hardware stalls. IPC response send failure only logs.

Test signals: Panic magic and normal request interrupts, reply completion, mailbox write ordering, malformed oops header, PCM pointer with valid/missing DAI, and continuous position update validation.
