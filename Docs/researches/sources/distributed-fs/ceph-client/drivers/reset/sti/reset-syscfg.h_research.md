# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.h

Purpose: shared declarations and macros for ST syscfg reset channel descriptions.

Important APIs/types/functions: `syscfg_reset_channel_data` describes syscon compatible plus reset/ack reg fields. `_SYSCFG_RST_CH()` and `_SYSCFG_RST_CH_NO_ACK()` build entries. `syscfg_reset_controller_data` configures ack waiting, active-low polarity, channel count, and channel array. Declares `syscfg_reset_probe()`.

Control flow: no runtime flow, but macro-generated tables drive `reset-syscfg.c`.

State and persistence: no independent state; structures become static SoC data.

Dependencies and integration: device, regmap, reset-controller headers; used by `reset-stih407.c` and generic syscfg implementation.

Risks and test signals: macro arguments are raw offsets/bits, so binding mistakes compile cleanly. Compile tests plus hardware reset/ack validation are required.
