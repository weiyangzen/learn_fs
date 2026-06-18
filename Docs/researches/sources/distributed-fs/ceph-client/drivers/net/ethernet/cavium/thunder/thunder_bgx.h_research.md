# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.h

## Purpose
`thunder_bgx.h` defines the public register, constant, type, and exported-function contract for the Thunder BGX/RGX MAC support code. It is consumed by BGX, XCV, NIC PF/VF-adjacent code, and mailbox-driven features that need link state, MAC addresses, filtering, pause, timestamping, and hardware statistics.

## Important APIs, Types, and Constants
The header defines PCI and subsystem IDs, maximum BGX/LMAC/channel/filter counts, frame and pause defaults, BGX register offsets and bit masks for CMR/SPU/SMU/GMP/MSI-X blocks, multicast mode bits, exported BGX service prototypes, XCV prototypes, BGX RX/TX stats counts, `struct bgx_stats`, and `enum LMAC_TYPE` values such as SGMII, XAUI, RXAUI, XFI, XLAUI, KR, RGMII, QSGMII, and invalid.

## Control Flow and Integration
There is no executable control flow, but the header fixes the register map used by `thunder_bgx.c` and the service API used by other Thunder NIC components. `nicvf_main.c` stores `struct bgx_stats` and reacts to BGX link/stat mailbox responses. PF-side code can call exported functions to configure BGX RX/TX, MAC filters, xcast modes, timestamping, pause, loopback, and statistics on behalf of VFs.

## State and Persistence
The file describes hardware state rather than storing it. Register macros address persistent-until-reset hardware state such as packet enable bits, filter CAM contents, link/PCS state, pause controls, timestamp insertion, interrupt enables, and counters. `struct bgx_stats` is a software snapshot buffer.

## Dependencies and Risks
The header depends on Linux integer/bool types and bit macros through includers. Risks are register ABI mismatch, incorrect LMAC mode constants, stat count drift relative to arrays and mailbox loops, and prototype changes that break symbol users. Since constants are shared across MAC and VF-facing paths, mistakes can surface as silent hardware misconfiguration rather than compile failures.

## Test Signals
Compile all Thunder NIC objects, then validate BGX probe, link mode reporting, stats loops using `BGX_RX_STATS_COUNT`/`BGX_TX_STATS_COUNT`, multicast mode changes, PFC and timestamp toggles, and RGX/XCV integration using `xcv_init_hw`/`xcv_setup_link`.
