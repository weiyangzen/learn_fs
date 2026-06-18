<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h

## Purpose
`hpet.h` defines the userspace ioctl ABI for High Precision Event Timer devices exposed through `/dev/hpet`.

## Important APIs, types, and functions
`struct hpet_info` returns interrupt frequency, feature flags, HPET block number, and timer number. `HPET_INFO_PERIODIC` indicates periodic-capable comparator support. Ioctls are `HPET_IE_ON`, `HPET_IE_OFF`, `HPET_INFO`, `HPET_EPI`, `HPET_DPI`, and `HPET_IRQFREQ`. `MAX_HPET_TBS` bounds timer blocks.

## Control flow
Users open an HPET timer, query its capabilities, set interrupt frequency, optionally enable periodic mode, then turn interrupts on or off and read timer events from the device.

## State and persistence behavior
Timer interrupt enablement, periodic mode, and requested frequency are live device/open-file state. No configuration is persisted by the header.

## Dependencies and integration points
It depends on `<linux/compiler.h>` for ioctl macro availability in included environments. It integrates with HPET hardware, the misc/char driver, timer interrupt delivery, and legacy timing applications.

## Risks and test signals
Risks include unsupported periodic mode, invalid frequency requests, timer resource conflicts, architecture availability differences, and unexpected interrupt rates. Test signals include ioctl round trips, periodic and one-shot interrupt counts, invalid-frequency rejection, open/close cleanup, and `HPET_INFO` capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h -->
