# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.h

Purpose: Declares shared MediaTek ADSP helper APIs and dump-size constants.

Important definitions: `EXCEPT_MAX_HDR_SIZE` caps the firmware exception header at `0x400`; `MTK_ADSP_STACK_DUMP_SIZE` requests 32 stack words. Prototypes cover dump, IPC send/reply/request, BAR mapping, stream hw_params, and stream pointer.

Control flow and integration: MT8186/MT8195 ops tables reference these functions directly. The header relies on included users already knowing `snd_sof_dev`, `snd_sof_ipc_msg`, `mtk_adsp_ipc`, `snd_pcm_substream`, and stream parameter types.

State and persistence: No state; constants control dump parsing bounds.

Risks: Header does not include all type declarations itself, so include order matters. Changing dump sizes affects panic log completeness and mailbox read length.

Test signals: Compile with both SoC drivers and panic dump coverage.
