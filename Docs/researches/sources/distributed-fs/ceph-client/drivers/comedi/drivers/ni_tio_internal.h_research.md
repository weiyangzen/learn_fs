## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio_internal.h

### Purpose
`ni_tio_internal.h` provides the private NI TIO register-offset macros, bit definitions, and internal helper prototypes shared by `ni_tio.c` and `ni_tiocmd.c`.

### Important APIs, Types, And Functions
It defines per-counter register index macros such as `NITIO_CMD_REG(x)`, `NITIO_MODE_REG(x)`, `NITIO_INPUT_SEL_REG(x)`, `NITIO_CNT_MODE_REG(x)`, `NITIO_GATE2_REG(x)`, `NITIO_SHARED_STATUS_REG(x)`, `NITIO_DMA_CFG_REG(x)`, `NITIO_INT_ACK_REG(x)`, and `NITIO_INT_ENA_REG(x)`. Bit macros cover arm/disarm/load, gating modes, edge behavior, stop/output/reload modes, source/gate selectors, counter modes, prescale and alternate sync, DMA enable/status, interrupt acknowledgments, and status/error indicators. The inline `ni_tio_counting_mode_registers_present()` distinguishes E-series from M-series/660x hardware.

### Control Flow, State, And Persistence
The header centralizes the bit layout that both synchronous counter configuration and asynchronous command support use. State persistence comes indirectly through the register-cache APIs declared here: `ni_tio_set_bits()`, `ni_tio_get_soft_copy()`, `ni_tio_arm()`, `ni_tio_set_gate_src()`, and `ni_tio_set_gate_src_raw()`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ni_tio.h` for register enums and structures. Integration risk is high because wrong bit definitions affect hardware programming across all NI counter users. Special care is needed for per-counter shared-status bit calculations, variant-specific prescale/alt-sync bits, and gate interrupt acknowledge/confirm bits. Test signals include compile-time coverage of both `ni_tio.c` and `ni_tiocmd.c`, counter status/error reporting, DMA interrupt acknowledge behavior, and E-series paths that lack counting-mode and gate2 registers.
