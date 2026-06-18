# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rfim.c

## Purpose

`processor_thermal_rfim.c` exposes RF interference mitigation controls for FIVR, DLVR, and DVFS through sysfs groups backed by processor thermal MMIO, mailbox commands, and selected PCI config fields.

## Important APIs, Types, and Functions

`struct mmio_reg` describes attribute bitfields; `struct mapping_table` maps special integer/string values. Generated `RFIM_SHOW` and `RFIM_STORE` callbacks implement many sysfs attributes. Additional attributes include mailbox-backed `rfi_restriction` and `ddr_data_rate`. Exports are `proc_thermal_rfim_add()` and `proc_thermal_rfim_remove()`.

## Control Flow

Add creates `fivr`, `dlvr`, and/or `dvfs` sysfs groups based on feature flags. DLVR register tables are selected by PCI device ID, with LNL/PTL/WCL using narrow mapped frequency values and NVL using alternate offsets plus PCI-config DDR data rate. Attribute reads choose a table, read MMIO or mailbox/config, apply bit extraction and optional string mapping. Writes reject read-only fields, parse mapped or numeric input, and perform read-modify-write.

## State and Persistence Behavior

Static globals hold the selected DLVR table, mapping, and DDR register. Hardware MMIO/mailbox/config values persist in platform registers. No per-device locking is used for MMIO RMW in this file.

## Dependencies and Integration Points

It depends on processor thermal MMIO, PCI IDs, sysfs, mailbox helpers, and feature masks from the common header. It is invoked by the core MMIO add/remove path.

## Risks and Test Signals

Risks include static per-platform table selection across devices, read-modify-write races, string matching using prefix lengths, incomplete cleanup if DVFS group creation fails without FIVR/DLVR, and no range check before shifting inputs into MMIO fields. Test signals include sysfs group creation for each feature combination, mapped DLVR values, mailbox `rfi_restriction`, NVL `ddr_data_rate`, read-only attribute rejection, and remove cleanup.
