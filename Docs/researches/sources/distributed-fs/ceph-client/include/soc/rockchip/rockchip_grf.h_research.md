# sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_grf.h

Purpose: centralizes Rockchip DDR type enum values shared by SoC-specific GRF readers.

Important APIs/types/functions: defines enum values for DDR3, LPDDR2, LPDDR3, LPDDR4, LPDDR4X, and LPDDR5 as `ROCKCHIP_DDRTYPE_*`.

Control flow: no executable flow. Consumers map extracted GRF DRAM type fields to these enum values.

State and persistence: no state. The enum is a shared ABI between GRF register interpretation and memory/devfreq logic.

Dependencies and integration: included by Rockchip DMC/devfreq and DFI event drivers with SoC-specific `rk*_grf.h` headers.

Risks: enum values must match firmware/GRF encodings. Wrong values break memory-type-specific bandwidth scaling and reporting. Test signals include memory type detection on multiple Rockchip boards and DFI/devfreq behavior.
