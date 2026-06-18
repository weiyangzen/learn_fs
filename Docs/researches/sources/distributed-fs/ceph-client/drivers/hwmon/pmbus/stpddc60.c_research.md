## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stpddc60.c

Purpose: supports STPDDC60/BMR481 controllers with custom handling for mixed VID and LINEAR VOUT encodings and relative VOUT fault-offset registers.

Important APIs, types, and functions: `stpddc60_get_offset()` converts absolute VOUT limit requests into 50 mV offset codes relative to VID VOUT_COMMAND. `stpddc60_adjust_linear()` rewrites linear11 values to a fixed exponent. `stpddc60_read_byte_data()` forces VOUT_MODE to linear. `stpddc60_read_word_data()` maps READ_VOUT to manufacturer register and masks linear11 mantissas. `stpddc60_write_word_data()` handles VOUT fault offsets and fixed-exponent limit writes. Probe validates MFR_MODEL, assigns callbacks, calls core, then marks VOUT fault limits update-on-read.

Control flow: probe verifies SMBus support and model, assigns custom callbacks into static info, registers with PMBus core, and updates core sensor flags for VOUT OV/UV fault limits. Runtime reads/writes intercept VOUT and selected limit registers; other accesses fall back to core.

State and persistence behavior: no private allocation. Writes to VOUT OV/UV limits persist as vendor offset bytes, not absolute PMBus values. `pmbus_set_update()` forces limit attributes to be reread because the hardware stores limits relative to current VOUT_COMMAND.

Dependencies and integration points: depends on PMBus core, virtual update flags, and I2C SMBus block/model validation. Integrates with standard hwmon attributes for VIN/VOUT/IOUT/POUT/temp/status.

Risks and test signals: VOUT limit conversion can be surprising when requested limits cross the current VOUT. Test VOUT read scaling, OV/UV limit write/read round-trips, fixed-exponent rewriting for other limits, model validation for `stpddc60` and `bmr481`, and update-on-read after changing VOUT_COMMAND.
