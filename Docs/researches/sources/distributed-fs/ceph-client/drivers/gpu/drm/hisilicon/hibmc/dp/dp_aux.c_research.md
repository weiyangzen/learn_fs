
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_aux.c

## Purpose
`dp_aux.c` implements the DisplayPort AUX transfer backend for the Hisilicon HIBMC DRM driver. It programs HIBMC DP AUX registers, marshals AUX request data, waits for transfer completion, parses hardware status, exposes a `drm_dp_aux` transfer callback, and initializes AUX timing fields.

## Important APIs, Types, And Functions
The public function is `hibmc_dp_aux_init(struct hibmc_dp *dp)`. Internal helpers include `hibmc_dp_aux_reset()`, `hibmc_dp_aux_read_data()`, `hibmc_dp_aux_write_data()`, `hibmc_dp_aux_build_cmd()`, `hibmc_dp_aux_parse_xfer()`, and `hibmc_dp_aux_xfer()`.

Important bitfields are `HIBMC_AUX_CMD_REQ_LEN`, `HIBMC_AUX_CMD_ADDR`, `HIBMC_AUX_CMD_I2C_ADDR_ONLY`, `HIBMC_AUX_I2C_WRITE_SUCCESS`, and `HIBMC_DP_MIN_PULSE_NUM`. The code uses DP core request/reply constants such as `DP_AUX_NATIVE_WRITE`, `DP_AUX_NATIVE_READ`, `DP_AUX_I2C_WRITE | DP_AUX_I2C_MOT`, `DP_AUX_I2C_READ | DP_AUX_I2C_MOT`, and `DP_AUX_NATIVE_REPLY_ACK`.

## Control Flow
For each transfer, `hibmc_dp_aux_xfer()` clears the four AUX write-data registers, writes request bytes into little-endian 32-bit write-data registers, builds the command word from request type, payload length or address-only flag, and AUX address, writes it to `HIBMC_DP_AUX_CMD_ADDR`, asserts `HIBMC_DP_CFG_AUX_REQ`, and polls the request bit for completion at 50 microsecond intervals up to 5 milliseconds. On timeout it resets the AUX block and returns the poll error. On completion it calls `hibmc_dp_aux_parse_xfer()`.

Parsing reads `HIBMC_DP_AUX_STATUS`, stores the hardware reply in `msg->reply`, reports `-ETIMEDOUT` for hardware timeout, returns 0 for address-only requests, rejects non-ACK replies for data transfers, returns full size for native writes, validates I2C write success through the ready-byte count, validates read byte count, copies read registers into the caller buffer for successful reads, and returns `-EINVAL` for unsupported request types.

Initialization programs AUX sync length, timer timeout, and minimum pulse count fields, assigns the transfer callback, name, DRM device, calls `drm_dp_aux_init()`, and stores the AUX pointer in `dp_dev`.

## State And Persistence
Hardware state includes AUX reset, request, command/address, write-data, read-data, status, timing, and pulse-width registers. Software state is stored in `struct hibmc_dp`'s `drm_dp_aux` and `struct hibmc_dp_dev`'s `aux` pointer. AUX register writes persist until reconfigured or hardware reset.

## Dependencies And Integration Points
The file depends on `dp_comm.h` for `struct hibmc_dp_dev` and the register-field write macro, `dp_reg.h` for HIBMC DP register offsets and masks, `dp_hw.h` for the enclosing `struct hibmc_dp`, Linux MMIO and polling helpers, and DRM DP AUX helpers. It feeds DPCD, EDID-over-AUX, link training, and downstream port discovery in the rest of the HIBMC DP stack.

## Risks
Only a subset of AUX request encodings is accepted; callers using non-MOT I2C requests or other variants may get `-EINVAL`. The read path decrements the ready-byte count before comparing with `msg->size`, so hardware status semantics must match that expectation. AUX write-data and read-data are packed little-endian into 32-bit registers. Poll timeout triggers an AUX reset, which can disrupt concurrent or immediately following transactions. The register-field macro uses a mutex, but raw data register writes in this file are not individually locked.

## Test Signals
Useful tests include DPCD native reads/writes during link training, EDID reads over AUX I2C with MOT, address-only I2C probes, hardware timeout recovery and subsequent successful transfer, malformed reply handling, partial read count returning `-EBUSY`, and successful `drm_dp_aux` registration visible to DRM DP helper users.
