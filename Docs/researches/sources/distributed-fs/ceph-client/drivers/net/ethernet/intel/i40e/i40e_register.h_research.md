# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_register.h

## Purpose

`i40e_register.h` defines i40e memory-mapped register offsets, index formulas, bit shifts, and masks used by the PF driver and shared code. It is the hardware address map for AdminQ rings, DCB, firmware/reset status, GPIO/MDIO, HMC, interrupts, queue control, NVM/Shadow RAM, PCI capability/configuration, energy-efficient Ethernet, packet filtering/RSS/Flow Director, statistics, PTP/timesync, malicious-driver detection, virtualization allocation, wake/power management, and X722-specific redefinitions.

## Important APIs, Types, and Macros

- `I40E_MASK(mask, shift)` creates 32-bit masks and underpins nearly every field definition.
- AdminQ registers include `I40E_PF_ATQ*`, `I40E_PF_ARQ*`, queue head/tail/base/length fields, enable/overflow/critical bits, and global ATQ critical bits.
- Global/port reset and firmware status include `I40E_GL_FWSTS`, recovery mode masks for XL710/X722, `I40E_GLGEN_RSTAT`, `I40E_GLGEN_RSTCTL`, `I40E_GLGEN_RTRIG`, `I40E_PFGEN_CTRL`, and VF reset status/triggers.
- GPIO/MDIO support includes `I40E_GLGEN_GPIO_CTL()`, GPIO set controls, MDIO/I2C select, MSCA/MSRWD fields, and pin function masks used by PTP pin code.
- Interrupt support includes PF/VF dynamic control, ICR0/ICR0_ENA cause bits, queue interrupt cause controls, linked-list registers, ITR registers, and timesync/adminq/reset/malicious detect bits.
- LAN queue and virtualization mapping include QRX/QTX enable/tail/head/control, PF/VSI/VF queue allocation and mapping tables.
- NVM registers include `I40E_GLNVM_FLA`, `I40E_GLNVM_GENS`, `I40E_GLNVM_SRCTL`, `I40E_GLNVM_SRDATA`, and `I40E_GLNVM_ULD`.
- PTP registers include `I40E_PRTTSYN_CTL0/1`, increment, time, adjust, Tx/Rx timestamp, event, auxiliary, target, and clock-output registers.
- Statistics registers cover global port, switch, VSI, and VEB traffic counters with high/low 32-bit halves.

## Control Flow

There is no executable control flow. The macros encode address arithmetic and field extraction constants for callers using `rd32()`, `wr32()`, `FIELD_GET()`, and bit operations. Indexed macros such as `I40E_QRX_ENA(_Q)`, `I40E_PFINT_DYN_CTLN(_INTPF)`, `I40E_GLV_*(_i)`, or `I40E_PRTTSYN_RXTIME_H(_i)` define how software walks hardware tables. Reset comments (`POR`, `CORER`, `GLOBR`, `PFR`, `VFR`, `EMPR`, etc.) document which hardware reset domains affect each register and guide reset-time reprogramming.

## State and Persistence Behavior

The header itself holds no state, but every macro refers to persistent or semi-persistent hardware state. Some registers reset only on power-on or global reset, while others reset on PF, VF, core, or EMP reset. This distinction affects driver persistence: PTP configuration must be restored after resets, NVM registers expose flash-backed Shadow RAM state, queue registers define live DMA state, interrupt masks define event delivery, and statistics registers accumulate hardware counters until cleared by reset or read/write semantics. Duplicate/redefined entries near the end for X722 and selected NVM/filter registers indicate family-specific compatibility pressure.

## Dependencies and Integration Points

All low-level i40e implementation files depend on this header either directly or through `i40e_type.h`/common includes. The NVM file uses `GLNVM_*` and the global timer. The PTP file uses `PRTTSYN_*`, `PFINT_ICR0_ENA_TIMESYNC`, and GPIO constants. AdminQ code uses PF AQ registers. Interrupt setup uses PF/VF INT and QINT registers. Queue setup/teardown uses QRX/QTX and LAN mapping registers. Statistics collection uses GLPRT/GLSW/GLV/GLVEBTC counters. Reset and error handling use firmware status, malicious detect, and reset registers.

## Risks

- Register macros are trusted constants. A wrong offset, index stride, mask width, or reset-domain assumption can cause silent hardware misprogramming.
- `I40E_MASK` is 32-bit. It is suitable for these register fields but should not be reused for wider values without care.
- Indexed macros rely on callers enforcing documented index ranges in comments. The macro itself does not bound-check queue, VSI, VF, port, or counter indices.
- Some macro names are duplicated or redefined near the end (`I40E_GLNVM_FLA`, `I40E_GLNVM_ULD`, `I40E_PRTQF_FD_INSET`). This can be intentional for family compatibility, but future edits risk compiler redefinition warnings or inconsistent values.
- The header's breadth means unrelated driver areas can be affected by a single change. Register edits should be reviewed against hardware specifications and existing call sites.

## Test Signals

Tests are mostly hardware and integration signals: AdminQ initializes and processes commands, resets complete, interrupts fire and are masked/unmasked correctly, queues enable/disable and pass traffic, NVM Shadow RAM reads work, PTP timestamps progress and latch, GPIO pin settings affect supported boards, statistics counters update, VFs receive mapped queues/interrupts, and malicious detect/error registers report sane values under fault injection. Build logs should be checked for macro redefinition warnings, and static review should compare changed offsets/masks to the hardware datasheet.
