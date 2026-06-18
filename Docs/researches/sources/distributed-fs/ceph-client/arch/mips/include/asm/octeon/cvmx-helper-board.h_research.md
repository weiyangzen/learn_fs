# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-board.h

## Purpose
`cvmx-helper-board.h` defines the board abstraction layer used by generic Octeon packet helper code. It isolates per-board PHY addressing, link discovery, interface port count overrides, management-port handling, PHY link set flags, and USB reference clock selection from common interface bring-up logic.

## Important APIs, Types, And Functions
The file defines `enum cvmx_helper_board_usb_clock_types`, `cvmx_helper_board_set_phy_link_flags_types_t`, and the fake management-port marker `CVMX_HELPER_BOARD_MGMT_IPD_PORT`. The exported hooks are `cvmx_helper_board_get_mii_address(int ipd_port)`, `__cvmx_helper_board_link_get(int ipd_port)`, `__cvmx_helper_board_interface_probe(int interface, int supported_ports)`, and `__cvmx_helper_board_usb_get_clock_type(void)`.

## Control Flow
Common helper code probes an interface, computes the hardware-supported port count, then calls the board probe hook to clamp or override the result for actual wiring. Link get/set logic asks this layer for PHY bus/address and current link state before programming GMX/PCS state. USB setup calls the clock hook to choose the reference source.

## State And Persistence
This header stores no state. Implementations usually consult bootloader-provided `cvmx_sysinfo` board type/revision and may read PHY registers through MDIO. Results affect persistent hardware state only when callers subsequently program link, PHY, or interface registers.

## Dependencies And Integration Points
It includes `cvmx-helper.h`, and therefore uses `union cvmx_helper_link_info`. It is integrated by RGMII/SGMII/XAUI/SPI helper implementations, PHY drivers, management Ethernet support, and USB initialization code.

## Risks
Every new board needs accurate switch cases. A wrong PHY address, bus encoding, port-count override, or USB clock type can make otherwise-correct generic helper code fail. The negative management IPD port is a sentinel and must not be treated as a normal port number by range checks.

## Test Signals
Board bring-up should verify expected port counts, MDIO reads for each IPD port, management-port PHY access, reported link speed/duplex under cable changes, and USB operation with the selected reference clock. Regression tests should cover unknown board types falling back safely.
