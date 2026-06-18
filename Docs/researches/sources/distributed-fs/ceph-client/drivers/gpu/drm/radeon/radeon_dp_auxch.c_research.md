# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_dp_auxch.c

## Purpose

`radeon_dp_auxch.c` implements the native DisplayPort AUX channel transfer hook for Radeon DCE hardware. It translates DRM DP AUX messages into writes and reads of the Radeon AUX software-control registers, handling native AUX and AUX-I2C read/write requests for up to 16 payload bytes.

## Important APIs, Types, and Functions

- `radeon_dp_aux_transfer_native(struct drm_dp_aux *aux, struct drm_dp_aux_msg *msg)` is the sole exported implementation. It is installed as `aux.transfer` by DisplayPort setup code.
- `AUX_RX_ERROR_FLAGS` groups hardware status bits that mean the AUX transaction failed.
- `aux_offset[]` maps AUX engine instances to register offsets.
- `BARE_ADDRESS_SIZE` documents the three-byte DP AUX address header.

## Control Flow

The transfer function validates message size and request type, derives write/read direction, computes the number of bytes to push into the hardware FIFO, and locks the owning `radeon_i2c_chan` mutex. It switches the pad into AUX mode through the DDC mask clock register, programs `AUX_CONTROL` with HPD selection and enable bits, writes the request/address/size header and optional payload into `AUX_SW_DATA`, clears pending completion, starts the transaction with `AUX_SW_GO`, and polls `AUX_SW_STATUS` up to about 100-200 ms total. On success it reads the reply byte and any returned payload bytes, acknowledges completion, sets `msg->reply`, and returns the transferred byte count.

## State and Persistence Behavior

The function does not own persistent state, but it mutates AUX engine registers and the pad mode for the selected I2C/AUX channel. Per-channel serialization is via `chan->mutex`. The caller-provided `msg->buffer` is filled for reads, and `msg->reply` is updated when the hardware transaction succeeds.

## Dependencies and Integration Points

This file depends on DRM DP AUX definitions, `struct radeon_i2c_chan`, Radeon MMIO helpers, HPD/DDC records, and DCE register definitions from `nid.h`. `atombios_dp.c` selects this native path when configured; otherwise AUX may use AtomBIOS paths. The transfer result feeds DRM DP link training, DPCD reads, EDID-over-AUX, and AUX-I2C operations.

## Risks and Edge Cases

- Only payloads up to 16 bytes are accepted; callers must split larger AUX operations.
- Polling is used instead of IRQ completion, so hung hardware can block for the full retry window.
- `instance = chan->rec.i2c_id & 0xf` assumes the low nibble indexes `aux_offset[]`; invalid firmware records could index past the six-entry table.
- The register mask update `tmp &= AUX_HPD_SEL(0x7)` is unusual because it preserves only selected bits before ORing new control bits; changes need hardware validation.
- Returned byte count includes the ACK byte, so read payload length is `bytes - 1`.

## Test Signals

Test DPCD reads/writes, EDID reads over AUX-I2C, timeout/error status handling, disconnect during AUX, each AUX engine instance, HPD selection, invalid request rejection, maximum-size payloads, and concurrent AUX/DDC access on the same channel.
