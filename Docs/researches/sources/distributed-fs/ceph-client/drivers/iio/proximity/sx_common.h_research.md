# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.h

Purpose: public internal header for Semtech SAR/proximity common support. It defines the register/default abstractions, chip description contract, driver private state, exported helper APIs, and shared event specifications used by chip-specific drivers.

Important APIs/types/functions: `SX_COMMON_REG_IRQ_SRC` and `SX_COMMON_MAX_NUM_CHANNELS` define common limits. `struct sx_common_reg_default` represents a register default with an optional firmware property. `struct sx_common_ops` is the chip callback table. `struct sx_common_chip_info` names key registers, bit offsets, channel counts, channel specs, and `iio_info`. `struct sx_common_data` stores mutex, completion, I2C client, trigger, regmap, proximity/event/read bitmaps, suspend state, and aligned scan buffer.

Control flow: the header establishes that chip drivers call `sx_common_probe()` from their I2C probe and route their `read_raw` and event callbacks to `sx_common_read_proximity()` and shared event helpers. Chip-specific callbacks fill gaps such as WHOAMI checks and sample wait behavior.

State and persistence: no state is persisted by the header itself, but the structs define persistent runtime state for enabled channels, event channels, last proximity status, and suspend control. The static assertion keeps channel bitmaps within an unsigned long.

Dependencies/integration: includes IIO types, regulators, Linux types, and forward declarations for I2C/regmap objects. The exported `sx_common_events[3]` gives rising, falling, and enable/value/hysteresis threshold ABI definitions.

Risks and test signals: ABI compatibility depends on chip drivers matching `num_channels`, channel indexes, and bitmap assumptions. Test by compiling all Semtech users, checking namespace imports, validating scan buffer alignment, and exercising chips with fewer than four channels to ensure masks and offsets are correct.
