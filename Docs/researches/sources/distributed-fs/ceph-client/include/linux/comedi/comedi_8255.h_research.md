# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8255.h

Purpose: This header provides generic Comedi support for 8255 digital I/O subdevices.

Important APIs/types/functions: It defines register offsets `I8255_DATA_A_REG`, `I8255_DATA_B_REG`, `I8255_DATA_C_REG`, `I8255_CTRL_REG`, size `I8255_SIZE`, control bits for port directions/modes, and helper `I8255_CTRL_A_MODE(x)`. APIs are `subdev_8255_io_init`, `subdev_8255_mm_init`, `subdev_8255_cb_init`, and `subdev_8255_regbase`. `subdev_8255_io_init` returns `-ENXIO` when I/O ports are unavailable.

Control flow: A low-level driver initializes a Comedi subdevice for I/O-port, MMIO, or callback-based access. The generic implementation then handles digital input/output instruction operations through the configured access path.

State and persistence behavior: Hardware state is the 8255 control word and port data registers; Comedi subdevice private state records register base/context. The header itself stores none.

Dependencies and integration points: It includes errno support and integrates with Comedi DIO subdevices, legacy I/O-port boards, MMIO boards, and custom bus access callbacks.

Risks: Port direction bits are split across A/B/C high/C low fields, and wrong control words can invert intended input/output behavior. I/O-port stubs require callers to handle `-ENXIO`.

Test signals: DIO read/write/config tests, callback and MMIO access tests, I/O-port-disabled builds, and port direction readback validate behavior.
