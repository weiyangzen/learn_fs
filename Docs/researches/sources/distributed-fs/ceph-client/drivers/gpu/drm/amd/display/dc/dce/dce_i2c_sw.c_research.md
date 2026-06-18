# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.c

Purpose: implements the software I2C fallback engine by bit-banging DDC GPIO clock/data pins. It supports multi-payload I2C commands, repeated starts for MOT transactions, ACK/NACK handling, clock-stretch waits, stop/start generation, and DDC acquisition/release.

Important APIs and functions: `dce_i2c_sw_construct()` stores context; `dce_i2c_engine_acquire_sw()` retries opening the DDC in fast-output I2C GPIO mode; `dce_i2c_submit_command_sw()` sets speed, submits each payload, and releases. Static helpers read/write SDA/SCL, wait for SCL high, write/read bytes MSB-first, generate start/stop, submit a channel request, and map `struct i2c_payload` to `i2c_request_transaction_data`.

Control flow: acquisition opens GPIO pins; command submission computes `clock_delay = max(1000/speed, 12)` and loops payloads with MOT true except the last. Each payload generates start/repeated-start, writes address and data or address then reads bytes, ACKs all but the last read byte, and sends stop on non-MOT or failure. Status becomes succeeded or failed in the request descriptor, and any failed payload aborts the command.

State and persistence: state is transient in `struct dce_i2c_sw`: active `ddc`, context, speed, and clock delay. GPIO pin electrical state is modified during transactions, then `dal_ddc_close()` releases ownership and clears `engine->ddc`.

Dependencies and integration: depends on GPIO service DDC APIs, I2C command/payload structures, and the action/status enums from the hardware header. It is used by the top-level DCE I2C dispatcher when hardware acquisition fails.

Risks and test signals: risks include timing accuracy under `udelay`, clock-stretch timeout scaling by `clock_delay_div_4`, minimum delay behavior for high requested speeds, SDA stuck-low start retries, stop failure handling, and ensuring release after all failure paths. Test with EDID reads, write-then-read repeated starts, slow clock-stretching sinks, NACKing addresses, hardware-busy fallback, and high CPU load where bit-bang timing is stressed.
