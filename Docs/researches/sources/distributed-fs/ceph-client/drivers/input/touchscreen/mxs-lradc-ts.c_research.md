<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c

Purpose: platform driver for Freescale MXS LRADC resistive touchscreen support. It reserves two virtual LRADC channels, programs plate switches and delay units, runs an IRQ-driven state machine for Y, X, pressure, and validation samples, then reports single-touch coordinates and pressure.

Important APIs/types/functions: `struct mxs_lradc_ts` tracks parent LRADC, MMIO base, input, current plate state, latest sample values, oversampling/delay settings, and spinlock. `struct state_info info[]` abstracts MX23/MX28 plate bits. Core functions include `mxs_lradc_setup_touch_detection()`, `mxs_lradc_prepare_y_pos()`, `mxs_lradc_prepare_x_pos()`, `mxs_lradc_prepare_pressure()`, `mxs_lradc_handle_touch()`, `mxs_lradc_ts_handle_irq()`, `mxs_lradc_ts_open()`, `mxs_lradc_ts_stop()`, and `mxs_lradc_ts_probe()`.

Control flow: probe reads parent LRADC data and OF properties for touchscreen wires, averaging count, averaging delay, and settling delay; resets the block; configures touchscreen type; requests three named IRQs; and registers input. Open enables touch-detect circuitry. A touch-detect IRQ disables touch detection, enables LRADC channel IRQ, and starts Y sampling. Subsequent channel IRQs read Y, read X, perform paired pressure conversion on channels 6/7, run a dummy validation delay, and only report if touch is still detected. If the pen remains down, the state machine loops to Y sampling; otherwise it emits release and re-enables touch detect.

State and persistence: runtime state is entirely in MMIO registers and the state-machine fields (`cur_plate`, `ts_valid`, coordinates, pressure). Hardware is reinitialized at probe/open and stopped on close; no nonvolatile state is used.

Dependencies/integration: depends on the MXS LRADC MFD parent, `linux/mfd/mxs-lradc.h` register definitions, OF properties (`fsl,lradc-touchscreen-wires`, `fsl,ave-ctrl`, `fsl,ave-delay`, `fsl,settling`), platform IRQ names, STMP reset helper, input core, and spinlock-protected IRQ handling.

Risks and test signals: pressure reading busy-waits until both channel IRQ bits are set, so hardware stalls can hang in IRQ context. Test MX23 and MX28 plate maps, 4-wire/5-wire setup, property bounds, IRQ mapping through `irq_of_parse_and_map()`, stop while state machine is mid-conversion, release validation on noisy panels, pressure divide-by-zero fallback, and interaction with buffered LRADC channels reduced by touchscreen use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c -->
