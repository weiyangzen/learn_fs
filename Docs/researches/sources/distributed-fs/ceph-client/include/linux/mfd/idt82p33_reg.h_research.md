# sources/distributed-fs/ceph-client/include/linux/mfd/idt82p33_reg.h

Purpose: This header maps selected Renesas/IDT 82P33xxx Synchronization Management Unit registers used for DPLL, time-of-day, phase offset, holdover frequency, input mode, output muxing, and soft reset.

Important APIs, types, and constants: `REG_ADDR(page, offset)` composes paged register addresses. Register macros identify DPLL1/DPLL2 TOD config/status/trigger, operating mode/status, current frequency, phase offset, sync edge, input mode, holdover frequency, output mux config, and soft reset. Bit macros include `SYNC_TOD`, `PH_OFFSET_EN`, `SQUELCH_ENABLE`, PLL mode/combo fields, operating status fields, TOD trigger masks, and soft reset enable. Enums define PLL operating modes, hardware TOD trigger selections, and DPLL runtime states.

Control flow, state, and persistence: There are no functions. Consumers program DPLL mode, TOD trigger selection, phase/holdover data, and output squelch through lower-level I2C/SPI/regmap access. DPLL lock/holdover/freerun and TOD values are persistent hardware state while the device is powered.

Dependencies and integration points: It relies on `BIT()` from included context or other headers and integrates with PTP/timecard DPLL drivers that translate Linux PTP operations into register transactions.

Risks and test signals: Risks include paged-address composition errors, wrong read versus write TOD trigger nibble, mode values outside the enum range, and assuming DPLL1/DPLL2 symmetry where hardware differs. Test signals include TOD read/write trigger validation, PLL mode transition tests, DPLL state polling, output mux checks, and soft-reset recovery.
