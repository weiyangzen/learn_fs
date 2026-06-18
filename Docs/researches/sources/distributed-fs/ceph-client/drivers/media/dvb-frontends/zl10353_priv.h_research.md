# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zl10353_priv.h

Purpose: Private register-map header for the ZL10353-family DVB-T demodulator implementation.

Important APIs/types/functions: Defines supported chip IDs `ID_ZL10353`, `ID_CE6230`, and `ID_CE6231`, byte extraction macros `msb()` and `lsb()`, and `enum zl10353_reg_addr` for interrupt/status/statistics, TPS, clock, reset, AGC, acquisition, TRL, input-frequency, tuner/FSM start, chip ID, and timing registers.

Control flow: This file has no executable logic. `zl10353.c` uses the enum names to address hardware registers during attach, init, tuning, status reads, and statistics reads.

State and persistence: No runtime state. It encodes the stable hardware ABI expected by `zl10353.c`.

Dependencies/integration: Included by the ZL10353 implementation before the public config header. Consumers outside the implementation should not depend on it.

Risks and test signals: Register-address drift causes silent hardware misprogramming. Tests should cover attach ID reads, each status/statistic register path, TPS register encoding/decoding, and clock/reset register overrides so enum changes are caught quickly.
