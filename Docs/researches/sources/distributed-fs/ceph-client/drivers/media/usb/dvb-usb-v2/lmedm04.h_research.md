# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.h

Purpose: private command/data header for the LME2510 DM04/QQBOX driver. It documents vendor command formats for streaming/PID filtering and LNB voltage/power, and provides the STV0288 initialization table used by the SHARP BS2F7HZ7395 frontend path.

Important APIs/types/functions: this file exports macros rather than callable APIs. `LME_ST_ON_W`, `LME_CLEAR_PID`, `LME_ZERO_PID`, and `LME_ALL_PIDS` define byte sequences consumed by `lmedm04.c` stream and PID paths. `LME_VOLTAGE_L`, `LME_VOLTAGE_H`, `LNB_ON`, and `LNB_OFF` define LNB command payloads. `s7395_inittab[]` is a static register/value terminator table wired into `struct stv0288_config lme_config`.

Control flow: `dm04_lme2510_frontend_attach()` selects the STV0288 path for SHARP 7395 hardware and passes `s7395_inittab` to the frontend attach routine. Runtime stream, PID, power, and voltage callbacks instantiate these macros as local command arrays, then send them through `lme2510_usb_talk()`.

State and persistence: no mutable state is held here, although `s7395_inittab` is defined as a non-const static array in the header, so every translation unit including it would get a private writable copy. In practice this header is consumed by the LME driver source.

Dependencies and integration: integrates with `lmedm04.c`, STV0288 frontend configuration, and the LME2510 vendor firmware command ABI. The command comments are part of the local contract for offset and checksum-like command bytes.

Risks: defining `s7395_inittab` in a header as `static u8` rather than `static const` is easy to duplicate accidentally and permits unintended modification. The raw command arrays encode protocol semantics without type checking; any later change to payload length or byte meaning must be synchronized with PID length logic in `lmedm04.c`.

Test signals: compile the LME driver with this header; attach the 7395 frontend and observe STV0288 initialization success; exercise PID filter clear/all/zero commands; confirm LNB high/low/off command effects on supported hardware.
