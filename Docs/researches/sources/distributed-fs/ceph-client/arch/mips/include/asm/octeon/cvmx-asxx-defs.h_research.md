# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asxx-defs.h

## Purpose
This header defines Octeon ASX/ASXX Ethernet interface CSRs. It covers RX/TX port enables, clock and data delay settings, RGMII/GMII/MII loopback and compensation, wake-on-LAN matching, interrupt status/enables, and RLD/FCRAM interface tuning registers.

## Important APIs, Types, and Functions
Address macros include `CVMX_ASXX_RX_PRT_EN`, `CVMX_ASXX_TX_PRT_EN`, `CVMX_ASXX_INT_REG`, `CVMX_ASXX_INT_EN`, RX/TX clock setup arrays, `CVMX_ASXX_PRT_LOOP`, `CVMX_ASXX_TX_HI_WATERX`, WOL registers, GMII/MII data/clock set registers, and RLD tuning registers. `__cvmx_interrupt_asxx_enable(int block)` is declared for interrupt enable integration. Bitfield unions model each CSR, including interrupt bits for overflow, TX/RX pop, and port-level events; loopback enable bits; RX/TX port enable masks; WOL mask/signature/power-ok fields; and RLD drive/control/bypass values.

## Control Flow
The file has no inline logic. Callers compute a block-indexed CSR address, load the matching union, modify fields, and write the CSR. The ASX hardware applies port gating, clock/data delay, loopback, WOL, and interrupt behavior immediately.

## State and Persistence Behavior
State is held by ASX hardware CSRs. Port enables, loopback, high-water, delay, compensation, and WOL settings persist until reset or later writes. Interrupt registers latch hardware conditions and are consumed by interrupt handlers.

## Dependencies and Integration Points
It depends on `CVMX_ADD_IO_SEG()` and Octeon endian bitfield definitions. It integrates with Octeon Ethernet helper code, GMX/IPD/PKO setup, PHY/link management, wake-on-LAN support, and the platform interrupt layer via the declared ASXX interrupt enable helper.

## Risks
Register offsets mask block and lane values, so incorrect block IDs can target the wrong ASX instance. RX/TX timing fields are board- and PHY-sensitive; bad values can produce marginal links rather than obvious failures. WOL and interrupt status fields must be cleared and masked carefully to avoid missed wake events or interrupt storms.

## Test Signals
Build-test drivers that include ASXX definitions. Runtime checks include link stability across RGMII/GMII/MII modes, loopback diagnostics, RX/TX enable transitions, WOL signature behavior, absence of ASXX interrupt storms, and stable packet traffic after clock/data delay changes.
