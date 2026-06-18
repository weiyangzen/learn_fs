# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.h

Purpose: register-layout and private-state header for the IBM PPC 4xx IIC driver. It defines the MMIO register struct, the per-controller software struct, and named bit masks for all controller control/status registers used by `i2c-ibm_iic.c`.

Important APIs/types/functions: `struct iic_regs` maps the IIC register block, including master data buffer, slave buffer, address registers, control/mode/status registers, clock divider, interrupt mask, transfer count, extended control/status, and direct line control. `struct ibm_iic_private` contains `i2c_adapter`, volatile MMIO pointer, waitqueue, controller index, IRQ, fast-mode flag, and clock divider. Macros cover `CNTL_*`, `MDCNTL_*`, `STS_*`, `EXTSTS_*`, `INTRMSK_*`, `XFRCNT_MTC_MASK`, `XTCNTLSS_*`, `DIRCNTL_*`, and `DIRCTNL_FREE()`.

Control flow: the C file includes this header and uses the register struct with `in_8/out_8` to initialize hardware, program target addresses, start transfers, poll or wake on status bits, check errors, reset the controller, and bit-bang direct-control lines for SMBus Quick and recovery.

State and persistence: this header documents all persistent software and hardware state but performs no work itself. The `volatile __iomem` register view is the stable contract between the driver and hardware.

Dependencies and integration: depends only on `<linux/i2c.h>` for adapter type visibility. It is tightly coupled to `i2c-ibm_iic.c` and the IBM PPC 4xx IIC hardware ABI.

Risks: register layout and bit masks must exactly match the hardware; any packing or offset drift would corrupt all operations. `DIRCTNL_FREE()` encodes bus-free ownership assumptions used during reset and SMBus Quick. The private struct exposes fields with no locking primitives besides the waitqueue, so the C file must maintain transfer serialization through the I2C core.

Test signals: compile-time inclusion by `i2c-ibm_iic.c`, successful MMIO register access on PPC 4xx, correct status/error decoding, clock-divider programming, interrupt-mask behavior, and direct-control recovery.
