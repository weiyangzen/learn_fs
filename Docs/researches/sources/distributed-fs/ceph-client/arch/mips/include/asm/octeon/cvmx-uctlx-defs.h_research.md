# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-uctlx-defs.h

Purpose: describes OCTEON USB controller (UCTL) CSRs for clock/reset, PHY control, EHCI/OHCI behavior, interrupt status/enable, timeout controls, BIST, watermarks, and interface enable.

Important APIs/types/functions: address macros include `CVMX_UCTLX_CLK_RST_CTL`, `UPHY_CTL_STATUS`, indexed `UPHY_PORTX_CTL_STATUS`, `INT_REG`, `INT_ENA`, `IF_ENA`, `PPAF_WM`, `EHCI_CTL`, `OHCI_CTL`, `ERTO_CTL`, `ORTO_CTL`, `BIST_STATUS`, and `EHCI_FLA`. Unions define fields for BIST blocks, clock divisors/resets, PHY reset/power/refclk, EHCI/OHCI L2 cache and address controls, timeout values, interrupt bits, watermark, PHY BIST/status, and port tuning/test controls.

Control flow: the header is declarative. USB platform code sequences resets/clocks, programs PHY tuning and host-controller controls, enables the interface, configures interrupts, and polls BIST/PHY status through these layouts.

State and persistence: state is USB controller and PHY CSR state. Clock/reset controls and interface-enable persist until reset or reconfiguration. Interrupt bits and BIST status are live hardware latches.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG`. It integrates with OCTEON USB host initialization, EHCI/OHCI platform drivers, and feature detection for `OCTEON_FEATURE_USB`.

Risks: most macros ignore `block_id`; `UPHY_PORTX_CTL_STATUS` masks the block contribution to zero and only varies by port offset, so assuming multiple blocks would alias. Reset/clock sequencing is fragile and not enforced by types. PHY tuning fields can break signal integrity. Timeout and interrupt fields have similar names for enable and status registers.

Test signals: USB bring-up should verify BIST pass, PHY reset release, EHCI/OHCI register access, interrupt delivery, device enumeration, timeout handling, and port tuning defaults on supported boards.
