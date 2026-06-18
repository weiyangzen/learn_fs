# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-ams.c

## Purpose
This file implements the Xilinx ZynqMP AMS IIO driver. It monitors PS, PL, and controller voltage/temperature channels, provides labels, direct raw reads, scaling and temperature offsets, threshold-event configuration, IRQ-driven event delivery, and power-management clock control.

## Important APIs, Types, And Functions
`struct ams` stores the shared AMS register base, optional PS and PL SysMon bases, clock, locks, enabled alarm mask, currently masked level-triggered alarms, interrupt mask, and delayed unmask work. Channel construction uses `AMS_*_CHAN_*` macros and three static channel arrays: PS, PL, and controller channels. Firmware parsing uses `ams_parse_firmware()`, `ams_init_module()`, and `ams_get_ext_chan()` to compose the IIO channel list from the main device and child fwnodes.

Important runtime functions include `ams_init_device()` for reset, readiness polling, default sequencer mode, alarm disable, interrupt masking, and pending-interrupt clearing; `ams_enable_channel_sequence()` for programming PS/PL sequencer registers from the exposed channel set; `ams_read_raw()` for direct samples and scale/offset reporting; `ams_read_vcc_reg()` and `ams_enable_single_channel()` for controller VCC channels that require single-channel PS sequencing; `ams_write_event_config()` and `ams_update_alarm()` for alarm enable/disable; `ams_read_event_value()` and `ams_write_event_value()` for threshold registers; `ams_irq()` and `ams_unmask_worker()` for level-sensitive alarm delivery.

## Control Flow
Probe allocates an IIO device, initializes mutex/spinlock state, maps the top-level AMS MMIO region, enables the clock, registers delayed-work autocancel, parses firmware to map PS/PL/controller submodules and build channels, initializes hardware, programs continuous channel sequences, requests the IRQ, stores driver data, and registers the IIO device. Direct raw reads lock `ams->lock`; PS and PL sequence channels read directly from their MMIO bases, while controller channels temporarily switch PS SysMon into single-channel mode, wait for end-of-conversion, read the controller offset, then restore the full channel sequence.

Event enable updates both PS and PL hardware alarm-mask bits and the top-level interrupt mask. The IRQ handler reads `AMS_ISR_0`, filters disabled and temporarily masked alarm bits, clears the active bits, marks them as currently masked, pushes IIO threshold events, schedules delayed unmask work, and returns handled. The delayed work polls active status and only unmasks alarms whose level condition has disappeared.

## State And Persistence
The driver persists configuration in runtime hardware registers and in-memory masks. It initializes thresholds for each alarm-capable parsed channel to min/max defaults during firmware parsing. Alarm state is split across `alarm_mask`, `intr_mask`, and `current_masked_alarm`, with spinlock protection for interrupt state and mutex protection for user configuration and raw reads. Suspend and resume only gate the clock; full hardware register persistence is expected from the platform or remains in hardware.

## Dependencies And Integration Points
It depends on platform firmware with `xlnx,zynqmp-ams` and optional PS/PL child nodes, fwnode MMIO mapping, clocks, IRQs, delayed work, IIO events, and IIO direct mode. Userspace sees labeled channels (`read_label` returns `datasheet_name`), raw values, scale/offset for voltage/temp, and threshold event attributes for alarm-capable channels. It integrates with `readl_poll_timeout()` for PS readiness and conversion completion.

## Risks And Test Signals
Risks include firmware channel parsing exposing no channels or malformed external PL channel `reg` values, missing PS or PL bases for channels that later assume them, interrupt storm hazards from level-sensitive alarms, and no range validation on threshold writes beyond raw register width. `ams_event_to_channel()` assumes a matching channel exists for each delivered alarm; malformed channel lists can make that fragile. Tests should cover PS-only, PL-only, controller-only, and combined nodes; raw reads of controller VCC channels; label output; rising/falling/either threshold attributes; alarm enable/disable and delayed unmask behavior under persistent threshold levels; suspend/resume; and probe failures for missing clock, bad child MMIO, or IRQ request failure.
