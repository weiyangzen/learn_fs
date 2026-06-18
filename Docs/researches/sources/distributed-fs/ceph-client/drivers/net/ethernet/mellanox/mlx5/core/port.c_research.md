# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/port.c

## Purpose

`port.c` is the mlx5 port-register service layer. It wraps `ACCESS_REG` and several direct command opcodes to query and configure physical port capabilities, link state, MTU, module EEPROM, pause/PFC/DCB/ETS, Wake-on-LAN, FCS checking, PTP pins, trust/DSCP mappings, and link-speed interpretation.

## Important APIs, Types, and Functions

The foundational API is `mlx5_access_reg()`, exported as `mlx5_core_access_reg()`, which packages caller-supplied register payloads into `ACCESS_REG` command buffers. Higher-level register wrappers include `mlx5_query_pcam_reg()`, `mlx5_query_mcam_reg()`, `mlx5_query_qcam_reg()`, `mlx5_set_port_caps()`, `mlx5_query_port_ptys()`, `mlx5_set_port_beacon()`, admin status setters/getters, MTU queries/setters, EEPROM readers, pause/PFC/stall watermark routines, DCBX and ETS routines, port check/FCS helpers, MTPPS/MTPPSE pin access, trust state access, buffer ownership query, DSCP-to-priority mapping, and link speed helpers.

Important local data includes `struct mlx5_reg_pcap`, `mlx5e_link_info[]`, and `mlx5e_ext_link_info[]`, which map PTYS protocol bits to speed/lane tuples for legacy and extended link modes.

## Control Flow

Most functions are one-shot register transactions: populate the register-specific input struct, call `mlx5_core_access_reg()` with read or write mode, then extract fields from output. EEPROM reads have more logic: `mlx5_query_module_eeprom()` obtains the module number from PMLP, reads module ID via MCIA, translates SFP/QSFP offsets into I2C address/page/offset, clamps cross-page reads, and calls `mlx5_query_mcia()`. DSCP update reads the whole QPDPM table, copies it back to input, modifies one entry, and writes the table.

DCB/ETS helpers loop over traffic classes or priorities and program QTCT/QETCR fields. Link speed queries choose the extended PTYS table if supported, then scan capability or operational bitmasks and return the maximum matching speed.

## State and Persistence Behavior

This file does not cache port state. Successful writes persist in firmware/hardware registers: admin status, MTU, pause/PFC, ETS bandwidth and rate limits, DCBX parameters, FCS behavior, PTP pin events, trust state, and DSCP priority mappings. Query helpers return snapshots. `mlx5_toggle_port_link()` temporarily transitions admin status down and restores it if it was up, forcing hardware to apply newly set port registers.

## Dependencies and Integration Points

Dependencies are the mlx5 command executor, register layout macros, Ethernet/IB port constants, PCI/module EEPROM definitions, and exported mlx5 port APIs consumed by mlx5e, RDMA, devlink/ethtool, DCB, PTP, and eswitch paths. Several helpers gate behavior on capability bits such as PCAM, MCAM, PTYS extended Ethernet, ETS, ports check, and MCIA 32-dword support.

## Risks and Edge Cases

Several query wrappers ignore command errors by design or return default fallback values, such as FCS support defaults when PCMR is unavailable. `mlx5_query_mtppse()` appears to read `event_arm` and `event_generation_mode` from the input buffer after the access call rather than from output; that should be verified against local kernel expectations. EEPROM reads must not cross pages incorrectly, and MCIA size depends on capability. DCB arrays assume caller-provided buffers cover all supported traffic classes or 64 DSCP entries.

## Test Signals

Useful tests include ethtool link-mode reporting on legacy and extended PTYS devices, MTU set/query loops, SFP/QSFP EEPROM reads across low/high pages, DCB/PFC/ETS configuration through `dcbnl`, DSCP mapping changes, PTP pin arm/query, FCS toggling on devices with and without PCMR, and fault injection for `ACCESS_REG` allocation and command failures.
