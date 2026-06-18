<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c

Purpose: I2C touchscreen driver for the Renesas MIGO-R platform. It enables a simple page-based controller, reads event and coordinate bytes on a threaded IRQ, swaps axes, and reports single-touch input.

Important APIs/types/functions: `struct migor_ts_priv` stores client, input, and IRQ. `migor_ts_ena_seq` and `migor_ts_dis_seq` are controller enable/disable command pages. `migor_ts_isr()` reads one 16-byte page and reports `EVENT_PENDOWN`, `EVENT_REPEAT`, or `EVENT_PENUP`. `migor_ts_open()` and `migor_ts_close()` send enable/disable sequences. Probe/remove manually allocate/free input and IRQ resources; PM only toggles IRQ wake.

Control flow: probe allocates state/input, sets fixed axis ranges, requests a low-triggered threaded IRQ, registers input, and enables wakeup. Open sends the enable sequence. IRQ writes index zero, reads the 16-byte page, extracts X/Y from bytes 8..11 and event from byte 12, reports touch-down/repeat with X/Y swapped, or touch-up. Close disables the IRQ around the disable sequence.

State and persistence: state is only client/input/IRQ plus controller enabled state while the input device is open. No calibration or persistent device data is stored.

Dependencies/integration: depends on I2C master send/recv, threaded IRQs, input core, PM wake IRQ, and I2C ID `migor_ts`.

Risks and test signals: enable/disable sequences are hard-coded and error handling in close ignores disable failure. Test controller page format, axis swap and min/max calibration, IRQ masking during close, wake IRQ suspend/resume, I2C short transfers, and remove after input registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c -->
