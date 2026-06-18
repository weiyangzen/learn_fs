# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.c

Purpose: Shared AUX transaction helper for Analogix I2C-addressed DP transmitters. It converts DRM DP AUX messages into register writes on the DPTX I2C page.

Important APIs/types/functions: The exported API is `anx_dp_aux_transfer(struct regmap *map_dptx, struct drm_dp_aux_msg *msg)`. Internal helpers are `anx_dp_aux_address`, `anx_dp_aux_wait`, `anx_dp_aux_op_finished`, and `anx_i2c_dp_clear_bits`.

Control flow: `anx_dp_aux_transfer` validates the 16-byte AUX buffer limit, sets address-only or length fields, writes payload bytes for non-read operations, writes the 20-bit AUX address, programs AUX control register 1 with the request, starts the transaction via `SP_AUX_EN`, waits until hardware clears the enable bit, reads status, assigns ACK, bulk-reads data for read operations, clears address-only state, and returns the transferred byte count.

State and persistence: No persistent state is stored in the helper. It mutates only the chip's AUX address/control/data registers through the supplied regmap and modifies `msg->reply` and `msg->buffer`. Timeout state is local jiffies polling.

Dependencies and integration: Depends on regmap and DRM DP AUX request/reply definitions. It is used by `analogix-anx78xx.c` and any other I2C Analogix DPTX user that supplies a TX_P0 regmap.

Risks: All hardware failures collapse mostly to `-ETIMEDOUT` or raw regmap errors. The helper always reports I2C ACK after a clean status; it does not distinguish native AUX ACK from I2C ACK. It uses polling and `usleep_range`, so callers must be sleepable.

Test signals: Exercise native/I2C reads and writes, zero-length address-only transfers, maximum 16-byte payloads, oversized `-E2BIG`, timeout when `SP_AUX_EN` never clears, AUX status error handling, and data-buffer readback.
