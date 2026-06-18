<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c

## Purpose
`stmpe-ts.c` is the touchscreen child driver for STMPE MFD devices with an integrated resistive touchscreen controller, especially STMPE811-compatible layouts. It configures the MFD ADC/touchscreen block, handles FIFO threshold interrupts, reports single-touch X/Y/pressure, and works around known FIFO/touch-detect quirks with delayed release polling.

## Important APIs, Types, And Functions
`struct stmpe_touch` stores the parent `struct stmpe`, input device, delayed work for release detection, device pointer, touchscreen properties, and ADC/touchscreen timing parameters. `stmpe_ts_get_platform_info()` reads DT properties such as sample time, ADC frequency, averaging, touch-detect delay, settling, Z fraction, and drive current. `stmpe_init_hw()` enables MFD touchscreen/ADC blocks, initializes common ADC state, configures TSC timing, FIFO threshold, and XYZ mode. `stmpe_ts_handler()` is the threaded IRQ path, and `stmpe_work()` emits release events after touch-detect settles.

## Control Flow
Probe obtains the parent MFD state, finds the named `FIFO_TH` IRQ, allocates state/input, reads platform tuning, initializes delayed work, requests the threaded IRQ, initializes hardware, configures `BTN_TOUCH`, ABS_X/ABS_Y/ABS_PRESSURE, parses touchscreen properties, and registers input. Opening the input device resets FIFO and enables TSC; closing cancels delayed work and disables TSC. The IRQ handler cancels pending release work, disables TSC, reads one XYZ sample, reports transformed position/pressure/down, resets FIFO, re-enables TSC, and schedules release polling 50 ms later.

## State And Persistence
State is volatile and bound to the MFD child. Platform tuning comes from DT and is applied at probe. The delayed work item is the main transient state used to convert touch-detect behavior into release events. Remove disables the touchscreen block.

## Dependencies And Integration Points
The driver depends on the STMPE MFD API (`stmpe_enable`, `stmpe_set_bits`, `stmpe_block_read`, ADC common init), platform IRQ resources, input core, touchscreen properties, delayed work, and platform driver binding.

## Risks
The driver explicitly works around silicon issues: FIFO may stop interrupting, touch-detect may deassert or stick. Release timing is heuristic. IRQ handler does not check all register-read return values before reporting. Remove disables only `STMPE_BLOCK_TOUCHSCREEN`, while probe enabled touchscreen and ADC blocks, so parent MFD lifetime assumptions matter.

## Test Signals
Validate DT tuning properties, open/close enable bits, FIFO reset on each IRQ, release generation after lift, behavior when FIFO contains no data, pressure range reporting, and MFD block enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c -->
