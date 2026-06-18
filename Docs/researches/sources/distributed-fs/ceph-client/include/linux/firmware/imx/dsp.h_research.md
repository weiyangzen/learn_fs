# sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h` declares the NXP i.MX DSP mailbox IPC interface. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

Important exports are `DSP_MU_CHAN_NUM`, `struct imx_dsp_chan`, `struct imx_dsp_ops`, `struct imx_dsp_ipc`, `imx_dsp_set_data`, `imx_dsp_get_data`, `imx_dsp_ring_doorbell`, `imx_dsp_request_channel`, and `imx_dsp_free_channel`. Disabled `CONFIG_IMX_DSP` builds return `-ENOTSUPP`, `ERR_PTR(-EOPNOTSUPP)`, or no-op.

## Control Flow

Client drivers set private data, request mailbox channels, ring doorbells to notify DSP firmware, and receive reply/request callbacks through `imx_dsp_ops`.

## State and Persistence Behavior

`struct imx_dsp_ipc` stores four host/DSP channels, the device, callback ops, and private data. Runtime state is mailbox and firmware communication state only.

## Dependencies and Integration Points

It depends on device, types, and mailbox client APIs. It integrates with i.MX DSP firmware, MU/mailbox hardware, audio/remoteproc-style clients, and platform drivers.

## Risks and Edge Cases

Channel index validation is critical. Disabled stubs return two different unsupported errno values. Callback concurrency depends on mailbox context.

## Test Signals

i.MX DSP driver probe tests, mailbox loopback tests, invalid channel tests, callback ordering tests, and disabled-config build coverage.
