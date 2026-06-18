# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-dsp.c

Purpose: Implements host-side mailbox doorbell IPC for i.MX DSP firmware. It provides exported helpers for DSP clients to request/free channels and ring DSP doorbells.

Important APIs/types/functions: `imx_dsp_ring_doorbell()` sends a mailbox message on a channel. `imx_dsp_request_channel()` and `imx_dsp_free_channel()` manage channels by generated names. `imx_dsp_handle_rx()` dispatches replies or requests to client callbacks. `imx_dsp_setup_channels()` initializes `txdb0`, `txdb1`, `rxdb0`, and `rxdb1`.

Control flow: Probe inherits the parent OF node, allocates `imx_dsp_ipc`, sets up mailbox clients with nonblocking sends and RX callback, requests all channels, and stores drvdata. RX channel index 0 calls `handle_reply`; index 1 calls `handle_request` and rings doorbell 1 as acknowledgement. Remove frees channels and names.

State and persistence behavior: State is per-device `imx_dsp_ipc` with channel descriptors. No persistent storage; mailbox messages coordinate with DSP firmware and external shared memory owned by clients.

Dependencies and integration points: Depends on Linux mailbox framework and `linux/firmware/imx/dsp.h` callback contracts. Built as a platform driver named `imx-dsp`.

Risks and test signals: The driver assumes client `ops` callbacks are installed before RX arrives. Error unwind must free names/channels. Test mailbox probe deferral, request/free exported helpers, RX reply/request callbacks, and remove cleanup.
