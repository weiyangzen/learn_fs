# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_sas.c

## Purpose

`scsi_transport_sas.c` implements the Linux SCSI Serial Attached SCSI transport class. It models SAS hosts, local PHYs, ports, remote PHYs, end devices, and expanders in the Linux device model, exposes their properties through sysfs, provides SMP BSG passthrough queues, and links SAS topology events to SCSI scanning and target removal.

This is shared infrastructure for SAS LLDDs, not a hardware driver. Drivers attach with `sas_attach_transport()` and use exported allocation/add/delete helpers to publish the SAS topology they discover.

## Important APIs, Types, and Functions

`struct sas_host_attrs` is per-host transport state stored in `shost_data`: the remote-PHY list, a mutex, optional host SMP BSG queue, and monotonically increasing target, expander, and port IDs. `struct sas_internal` is allocated by `sas_attach_transport()` and stores the SCSI transport template, callback table, and attribute containers for host, phy, port, rphy, end-device, and expander classes.

Topology APIs include `sas_phy_alloc()`, `sas_phy_add()`, `sas_phy_free()`, `sas_phy_delete()`, `sas_port_alloc()`, `sas_port_alloc_num()`, `sas_port_add()`, `sas_port_free()`, `sas_port_delete()`, `sas_port_add_phy()`, `sas_port_delete_phy()`, `sas_port_get_phy()`, `sas_port_mark_backlink()`, `sas_end_device_alloc()`, `sas_expander_alloc()`, `sas_rphy_add()`, `sas_rphy_remove()`, `sas_rphy_free()`, `sas_rphy_delete()`, and `sas_rphy_unlink()`.

Removal helpers are `sas_remove_children()` and `sas_remove_host()`. Device predicates include `scsi_is_sas_phy()`, `scsi_is_sas_port()`, and `scsi_is_sas_rphy()`. Device capability helpers include `sas_get_address()`, `sas_tlr_supported()`, `sas_enable_tlr()`, `sas_disable_tlr()`, `sas_is_tlr_enabled()`, `sas_ata_ncq_prio_supported()`, and `sas_read_port_mode_page()`.

## Control Flow

Module initialization registers six transport classes: host, phy, port, generic SAS device/rphy, end device, and expander. `sas_attach_transport()` registers one transport container per class, fills attribute arrays according to the provided `sas_function_template`, installs `sas_user_scan()` as the SCSI user scan hook, and sets `host_size` to hold `struct sas_host_attrs`.

Host setup initializes the remote-PHY list and counters, creates a host BSG queue if the driver has an SMP handler, and derives `shost->opt_sectors` from the DMA device's optimal mapping size. Host removal removes the BSG queue.

A local PHY is allocated under either a host or expander rphy, named by host and PHY number, initialized with `enabled = 1`, and prepared with `transport_setup_device()`. `sas_phy_add()` publishes it with `device_add()`, `transport_add_device()`, and `transport_configure_device()`. Deletion requires that it is no longer linked into any port, then removes the transport/device state and drops the final reference.

A SAS port is allocated under a host or expander and may be numbered by the caller or by the host/expander counter. PHYs are linked into ports with reciprocal sysfs links. Adding an already-linked PHY is permitted only when it is already on the same port; otherwise the code logs and BUGs because a PHY cannot belong to two ports. Deleting a port first deletes any attached rphy, unlinks all member PHYs, removes optional backlink sysfs state, and tears down the device.

Remote PHY add enforces one rphy per port, publishes the rphy, adds optional per-rphy BSG, inserts it into the host `rphy_list`, assigns SCSI target IDs for end devices that advertise SSP, STP, or SATA target protocols, and scans the SCSI target. SSP devices are scanned for wildcard LUNs; STP/SATA devices scan LUN 0. Remote PHY remove removes SCSI targets for end devices or recursively removes children for expanders, unlinks the parent port, removes BSG, and deletes transport/device state.

Manual scans route channel 0 through the SAS rphy list and delegate other channels to the generic SCSI selected scan. Wildcard scans do both channel 0 SAS topology scans and normal scans across channels 1 through `max_channel`.

## State and Persistence Behavior

State is in-memory and scoped to the SCSI host lifetime. The host mutex protects the rphy list and ID counters. Port membership is protected by each port's `phy_list_mutex`. Parent references keep host, port, and rphy devices alive until child release callbacks run.

The topology model preserves no state on disk. Target IDs and expander IDs are increment-only while the host exists. End-device fields such as TLR support, TLR enablement, port mode-page data, and expander strings are cached in their rphy-specific structures and exposed through sysfs.

BSG queues are created for the host and for each rphy only when the driver supplies `smp_handler`. `sas_smp_dispatch()` passes host-level jobs with `rphy == NULL` and rphy-level jobs with the target rphy pointer.

## Dependencies and Integration Points

The file integrates with the SCSI midlayer for host/user scan, target scan, and target removal; the transport class framework for sysfs objects; the device model for topology naming and links; BSG for SMP passthrough; DMA helpers for optimal transfer sizing; and VPD/mode-page helpers for TLR, NCQ priority, and port timing information.

Driver callbacks in `struct sas_function_template` supply SMP handling, PHY setup/release, link error refresh, PHY speed changes, PHY reset, PHY enable/disable, and optional enclosure/bay identifiers. libsas and hardware-specific SAS drivers are the natural producers of these topology objects.

## Risks and Edge Cases

Topology lifetime ordering is strict. A PHY must be removed from its port before `sas_phy_delete()`, and a port's rphy must be removed before port teardown completes. Violations intentionally BUG in several places because the sysfs topology would otherwise become inconsistent.

`sas_rphy_free()` removes the rphy from `rphy_list` even though the list insertion happens in `sas_rphy_add()`. The documented safe use says free is for never-added or removed rphys, so callers must not free an object that was never on the list unless list state has been initialized appropriately.

The file uses incremental IDs rather than IDR reuse, so long-lived hosts with repeated topology churn can grow IDs monotonically. That is expected but visible in sysfs names and target IDs.

Attribute output uses small `snprintf(buf, 20, ...)` buffers for many simple values; this is adequate for fixed numeric SAS fields but would be fragile if reused for longer formatted content. Expander string fields are printed directly from cached driver-provided strings.

SMP BSG dispatch only checks for reply payload space before calling the driver. Request semantic validation and completion behavior are driver responsibilities.

## Test Signals

Useful signals include class registration and release; host attach with optional SMP BSG queue; PHY add/delete and driver setup/release callbacks; link reset, hard reset, enable, speed, and link-error sysfs paths; port creation with one and multiple PHY links; refusal of a PHY already attached to a different port; end-device and expander rphy add/remove; recursive expander child deletion; SCSI target scan behavior for SSP versus SATA/STP devices; manual user scans for channel 0 and wildcard channels; TLR VPD and port mode-page reads; NCQ priority from VPD page 0x89; and BSG SMP dispatch for host and rphy devices.
