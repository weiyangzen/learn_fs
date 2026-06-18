# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfbuffer.h

Purpose: Defines ath5k RF buffer data structures, RF analog-register field maps, register indexes, and static RF bank initialization tables for supported RF chips.

Important APIs and types: `struct ath5k_ini_rfbuffer` describes one RF bank/control-register tuple with mode-specific values for A/XR, B, and G. `struct ath5k_rfb_field` describes bit length, position, and column shift in the packed RF bank stream. `struct ath5k_rf_reg` maps a logical RF register index to a bank and packed field. `enum ath5k_rf_regs_idx` names logical RF fields such as turbo, OB/DB bias, XPD, PWD bits, gain, wait, and delay controls. Static tables include `rf_regs_5111`, `rf_regs_5112`, `rf_regs_5112a`, `rf_regs_2413`, `rf_regs_2316`, `rf_regs_5413`, `rf_regs_2425`, and RF buffer defaults `rfb_5111`, `rfb_5112`, `rfb_5112a`, `rfb_2413`, `rfb_2316`, `rfb_5413`, `rfb_2425`, `rfb_2317`, and `rfb_2417`.

Control flow: This header has no executable control flow. Runtime RF initialization code selects a table by radio revision, copies the mode-specific RF bank words, edits selected packed fields using the register maps, writes bank data through RF buffer registers, and triggers hardware apply through the corresponding control register.

State and persistence: Owns immutable static calibration defaults and packed-field metadata. It does not mutate state directly, but consumers use these values to populate `ah->ah_rf_banks` and hardware RF buffer registers. The constants encode a hardware ABI for analog front-end programming.

Dependencies and integration points: Consumed by ath5k PHY/RF register initialization code and tied to register definitions in `reg.h`, EEPROM calibration values, channel mode selection, RF gain optimization, and reset/PHY initialization. It bridges logical driver concepts to packed RF bank layouts that differ by RF5111, RF5112, RF2413, RF2316/2317, RF5413, RF2425/2417 families.

Risks: Bit positions and bank layouts are extremely hardware-specific; a one-bit error can corrupt radio analog programming. Several tables intentionally share defaults with comments noting TODOs for 2317/2417 differences, so later edits must preserve known variant quirks. Static header definitions increase compile-time coupling and can produce duplicate-data bloat if included outside intended C files.

Test signals: Verify RF bank programming on every supported radio family, band and mode transitions, turbo/half/quarter-rate behavior, EEPROM overrides of OB/DB/XPD/gain fields, RF gain calibration interaction, and regression tests for hardware that uses the 2317/2417 alternate tables.
