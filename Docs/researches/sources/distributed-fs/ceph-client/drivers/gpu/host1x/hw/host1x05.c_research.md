<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c

## Purpose

`host1x05.c` is the generation include unit for host1x05 (Tegra210). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 5`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x05.h` and `host1x05_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x05_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra210. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra210, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c -->
