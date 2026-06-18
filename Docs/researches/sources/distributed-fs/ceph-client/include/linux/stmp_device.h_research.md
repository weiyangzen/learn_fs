<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp_device.h -->
# sources/distributed-fs/ceph-client/include/linux/stmp_device.h

Purpose: Declares common helpers and register offset conventions for devices using the STMP set/clear/toggle register layout.

Important APIs/types/functions: `STMP_OFFSET_REG_SET`, `STMP_OFFSET_REG_CLR`, `STMP_OFFSET_REG_TOG`, and `stmp_reset_block(void __iomem *)`.

Control flow: Drivers use base register addresses plus SET/CLR/TOG offsets for atomic-style bit manipulation and can call `stmp_reset_block()` to reset a hardware block.

State and persistence behavior: Header has no state; operations affect MMIO register state of STMP-style devices.

Dependencies: MMIO pointer annotation `__iomem` via includer context.

Integration points: STMP/i.MX-style platform drivers with common register layout.

Risks: Passing the wrong base address to reset or offset calculations can modify unrelated registers. Reset timing and completion are implementation-specific.

Test signals: Register offset unit checks in drivers, hardware reset tests, and build coverage for drivers including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp_device.h -->
