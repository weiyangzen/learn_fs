# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_reg.h

Purpose: defines MMIO register offsets and bit-field helpers for the sun6i CSI controller and capture channel.

Important APIs and constants: covers global enable, interface configuration, capture control, pattern generator, channel config, input/output format constants, FIFO addresses, channel status, interrupt enable/status, frame/line size, buffer length, flip size, counters, and address conversion through `SUN6I_CSI_ADDR_VALUE`.

Control flow: no executable control flow. Bridge code writes interface and channel format registers; capture code writes FIFO addresses, sizes, and buffer lengths; IRQ code reads and clears interrupt status.

State and persistence: no software state. The macros describe volatile hardware state programmed during runtime PM and stream start.

Dependencies and integration points: includes `linux/kernel.h` for `BIT` and `GENMASK`. It is consumed by all sun6i CSI implementation files and must match hardware manuals/BSP behavior.

Risks: comments note that Allwinner documentation inverts some positive/negative and frame/field definitions; misuse can cause polarity or interlacing bugs. Bit-field macros assume caller-supplied values fit expected ranges and silently mask overflow. Address conversion shifts DMA addresses by two, matching hardware word-addressing assumptions.

Test signals: hardware capture with parallel and MIPI sources, polarity tests, interlaced input tests, FIFO overflow interrupt tests, and register dumps compared with known-good BSP programming.
