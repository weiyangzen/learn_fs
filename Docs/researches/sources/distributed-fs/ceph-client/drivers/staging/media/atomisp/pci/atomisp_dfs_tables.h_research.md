# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_dfs_tables.h

## Purpose
This header defines the data model for AtomISP dynamic frequency scaling rules and per-SoC DFS configuration.

## Important APIs and Types
`struct atomisp_freq_scaling_rule` contains width, height, fps, ISP frequency, and run mode. `struct atomisp_dfs_config` stores low, max-at-vmin, and highest frequencies plus a rule table and size. `dfs_config_cht_soc` is declared for Cherry Trail.

## Control Flow
No logic is implemented here. Runtime DFS code uses these tables to choose operating frequencies during stream start, stream stop, and mode changes.

## State and Persistence
DFS rules are immutable table data. The selected config is referenced by `atomisp_device::dfs`; current runtime frequency is tracked in device fields declared elsewhere.

## Dependencies and Integration Points
Included by AtomISP internals and used by platform/PCI setup and stream-time frequency scaling calls.

## Risks
Incorrect rules can underclock the ISP and cause dropped frames/timeouts, or overclock it unnecessarily. Units are implicit in plain integer field names.

## Test Signals
Check selected frequencies for preview/video/still capture across resolutions and fps, verify stop-stream returns to low mode, and compare CHT table limits to hardware.
