# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_host_smp.c

## Purpose

`sas_host_smp.c` implements a virtual SMP target for SAS hosts when no expander rphy is targeted. It lets BSG SMP requests query and control host PHY state, report host manufacturer information, report SATA information for directly attached SATA devices, and optionally write GPIO registers through low-level driver callbacks.

## Important APIs, Types, and Functions

The top-level handler is `sas_smp_host_handler()`. Request handlers include `sas_host_smp_discover()`, `sas_report_phy_sata()`, `sas_phy_control()`, and `sas_host_smp_write_gpio()`. GPIO bit helpers are `to_sas_gpio_gp_bit()` and exported `try_test_sas_gpio_gp_bit()`.

Important structures are `struct sas_ha_struct`, `struct asd_sas_phy`, `struct sas_phy`, `struct sas_rphy`, `struct bsg_job`, `struct dev_to_host_fis`, and low-level driver callbacks `lldd_write_gpio` and `lldd_control_phy`.

## Control Flow

`sas_smp_host_handler()` validates minimum request and response payload sizes, copies the BSG request sglist into a linear buffer, allocates a response buffer large enough for known frames, validates `SMP_REQUEST`, initializes a default unknown-function response, and switches on the SMP function code. REPORT GENERAL returns the host phy count. REPORT MANUFACTURER INFORMATION returns the SCSI host template name and a fixed virtual product string. DISCOVER reports per-phy link rates, SAS addresses, attached addresses, and attached device protocol/type from the current port device. REPORT PHY SATA returns directly attached SATA information and converts the saved D2H FIS into the response byte order. WRITE GPIO delegates raw register writes to `lldd_write_gpio()`. PHY CONTROL validates the operation and forwards it to `lldd_control_phy()`, except link reset may be satisfied by libata reset coordination via `sas_try_ata_reset()`.

The handler copies the response back to the reply sglist and completes the BSG job with the selected response length. Unsupported functions generally complete with `SMP_RESP_FUNC_UNK`; invalid frame lengths fail the job.

## State and Persistence Behavior

The file does not own persistent state. It reads current HA PHY topology, current `sas_phy` linkrate limits, attached SAS addresses, rphy identify fields, and saved SATA FIS data from the port device. GPIO writes and PHY control requests may change hardware state through low-level callbacks, but no configuration is stored here.

## Dependencies and Integration Points

The file depends on the SAS transport BSG path, libsas HA/PHY/port state, SMP protocol constants, low-level driver callbacks for GPIO and PHY control, and libata reset coordination through `sas_try_ata_reset()`. It is compiled when `CONFIG_SCSI_SAS_HOST_SMP` is selected and is also used as fallback by `sas_expander.c` when an SMP BSG job has no target rphy.

## Risks and Edge Cases

Many responses are best-effort snapshots without global topology locking. `sas_report_phy_sata()` assumes a port and `port_dev` exist after checking only the phy's port pointer, so host topology transitions must keep those pointers consistent. Only single linear request/response copies are used through temporary buffers sized from BSG payload lengths. GPIO bit layout is nonintuitive and depends on SFF-8485 register indexing. PHY CONTROL can trigger disruptive link/hard resets or disables if authorized by userspace and the low-level driver.

## Test Signals

Test signals include BSG REPORT GENERAL, REPORT MANUFACTURER INFO, DISCOVER for valid and invalid phy IDs, REPORT PHY SATA for SATA and non-SATA phys, WRITE GPIO with and without a low-level callback, GPIO bit extraction across register indexes, PHY CONTROL operations including invalid op and no-phy cases, libata-coordinated link reset, and response length/error handling for undersized request or reply payloads.
