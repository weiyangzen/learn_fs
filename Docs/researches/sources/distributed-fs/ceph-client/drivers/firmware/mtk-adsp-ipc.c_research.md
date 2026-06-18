# sources/distributed-fs/ceph-client/drivers/firmware/mtk-adsp-ipc.c

Purpose: Implements MediaTek ADSP mailbox IPC plumbing for clients that exchange requests and replies with audio DSP firmware.

Important APIs/types/functions: `mtk_adsp_ipc_send()` sends a 32-bit mailbox message on a selected channel and is exported GPL. `mtk_adsp_ipc_recv()` dispatches mailbox RX callbacks to client `handle_reply` or `handle_request`. Probe requests named channels `rx` and `tx`.

Control flow: Built-in platform probe inherits the parent OF node, allocates `mtk_adsp_ipc`, initializes two mailbox clients, requests channels by name, stores drvdata, and logs debug initialization. RX callbacks switch on channel index and call client ops. Remove frees all mailbox channels.

State and persistence behavior: Per-device state stores channel descriptors and client ops pointer. No persistent storage; mailbox messages coordinate with DSP runtime state.

Dependencies and integration points: Depends on mailbox framework and `linux/firmware/mediatek/mtk-adsp-ipc.h`. Higher-level ADSP clients install ops and use the exported send helper.

Risks and test signals: Like the i.MX DSP path, RX assumes `ipc->ops` callbacks are valid. Error unwind frees earlier channels. Test probe deferral, send invalid index, reply/request dispatch, absent client ops handling, and remove cleanup.
