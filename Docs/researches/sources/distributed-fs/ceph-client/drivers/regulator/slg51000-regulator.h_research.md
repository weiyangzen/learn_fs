<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h

Purpose: defines the SLG51000 register map and bitfield masks consumed by `slg51000-regulator.c`. It is a hardware contract header rather than executable driver logic.

Important APIs/types/functions: the header exports register addresses for system control, GPIO configuration/status, LUT and mux arrays, power sequencer settings, LDO1-LDO7 voltage/control/event/status/IRQ registers, OTP event/mask/lock registers, and global lock control. It also defines bit shift/mask pairs for pattern IDs, matrix/resource control, fault logs, high-temperature events, GPIO status, power-sequencer timing, voltage selector/min/max fields, LDO event/status flags, bypass mode bits, OTP CRC, and global LDO lock bits.

Control flow: there is no runtime control flow. The C file uses these constants to construct regmap access tables, read OTP-configured voltage windows, detect LDO5/6 bypass mode, clear/log fault state, and decode IRQ events into regulator notifications.

State and persistence: the header itself has no state. The named registers correspond to hardware state, some of which is volatile event/status state and some of which is OTP or configuration-backed.

Dependencies and integration: guarded by `__SLG51000_REGISTERS_H__` and included only by the SLG51000 regulator driver. It integrates with the Linux regmap and regulator code indirectly by providing stable addresses/masks for descriptor construction and event handling.

Risks and test signals: any incorrect address or mask silently corrupts voltage programming, IRQ decoding, or regmap access permissions. The readable/writable/volatile tables in the C file must stay aligned with this header. Test signals include compile coverage, regmap reads/writes to every descriptor field, fault and event decoding against datasheet traces, and review of lock/OTP masks before enabling future write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h -->
