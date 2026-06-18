# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.h

Purpose: public interface and data model for the RP1 CSI-2 receiver component.

Important APIs/types/functions: defines channel and pad counts, `enum csi2_mode`, `enum csi2_compression_mode`, discard counter indexes, `struct csi2_device`, and function prototypes for ISR, buffer programming, compression, channel start/stop, RX open/close, init, and uninit.

Control flow: no implementation; the CFE core calls these functions during stream setup, scheduling, ISR dispatch, and teardown.

State and persistence: `struct csi2_device` stores V4L2 device pointer, MMIO base, DPHY state, bus flags, line counts, pads/subdev, and discard/overflow counters.

Dependencies and integration: includes debugfs, MMIO types, V4L2 device/subdev, and `dphy.h`. The structure is embedded in `struct cfe_device`.

Risks: constants such as `CSI2_NUM_CHANNELS` and pad indexes must stay aligned with CFE node descriptions and media links. Changes to `struct csi2_device` affect the core driver layout.

Test signals: build/link coverage and runtime validation that each CFE CSI2 node maps to the expected source pad/channel.
