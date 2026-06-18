<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h -->
# sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h

Purpose: Supplies platform configuration for ADXL34x digital accelerometer input drivers.

Important APIs/types/functions: `struct adxl34x_platform_data` captures axis offsets, tap/double-tap axis and timing thresholds, activity/inactivity AC/DC and axis masks, free-fall threshold/time, data rate, range/full-resolution mode, low-power/power behavior, FIFO mode, watermark, interrupt mapping, event codes, and optional platform callbacks. Macros define bit positions and ranges for tap, activity, full-resolution, g range, FIFO, and interrupt behavior.

Control flow: Probe applies board data to sensor registers and input capabilities; interrupt paths report configured tap/activity/free-fall/motion events.

State/persistence: Configuration persists in hardware registers; platform callback state is external.

Dependencies/integration: Depends on input event codes and board-specific device data.

Risks: Many zero values disable or destabilize detection; data rate versus bus speed can drop samples.

Test signals: Register programming, tap/activity/free-fall event tests, range/resolution reporting, FIFO watermark IRQs, and suspend/resume power callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h -->
