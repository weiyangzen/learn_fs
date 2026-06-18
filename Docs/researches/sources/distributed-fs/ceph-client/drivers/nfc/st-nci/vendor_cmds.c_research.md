# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/vendor_cmds.c

## Purpose
`vendor_cmds.c` registers ST_NCI vendor commands exposed through the NFC generic netlink vendor interface. These commands proxy HCI device-management operations, factory mode, loopback, firmware-update staging, measurements, and manufacturer-specific data.

## Important APIs, types, and functions
- `st_nci_vendor_cmds_init()` installs `st_nci_vendor_cmds` with `nci_set_vendor_cmds()`.
- Factory mode toggles `ST_NCI_FACTORY_MODE` in driver flags.
- HCI DM helpers send PUTDATA, UPDATE_AID, GETINFO, GETDATA, FWUPD_START/STOP, LOAD, RESET, FIELD_GENERATOR, VDC measurement, and VDC comparison commands to `ST_NCI_DEVICE_MGNT_GATE`.
- Reply-producing helpers allocate vendor reply skbs and attach `NFC_ATTR_VENDOR_DATA`.
- `st_nci_loopback()` uses `nci_nfcc_loopback()`.
- `st_nci_manufacturer_specific()` returns `ndev->manufact_specific_info`.

## Control flow
Userspace sends an NFC vendor command with ST OUI and a subcommand from `enum nfc_vendor_cmds`. Most handlers synchronously send an HCI command and either return the status or wrap returned data in a vendor reply. Firmware download uses a state bit in `nfc_dev`: `FWUPD_START` sets `fw_download_in_progress`, `DIRECT_LOAD` is accepted only once while the flag is set and then clears it, and `FWUPD_END` sends the stop command.

## State and persistence
State changes include factory-mode flag and `nfc_dev->fw_download_in_progress`. No persistent files are written. Vendor replies expose current chip/HCI/manufacturer data to userspace.

## Dependencies and integration points
The file depends on generic netlink attributes, NFC vendor command APIs, NCI HCI helpers, NCI loopback, and ST_NCI gate/command constants. It is initialized during `st_nci_probe()`.

## Risks
Many commands pass arbitrary userspace vendor data directly to HCI device-management commands; validation is limited to a few length checks. `st_nci_hci_dm_reset()` ignores the return from `nci_hci_send_cmd()` and always returns 0 after a fixed 200 ms sleep. Firmware direct load clears the in-progress flag before sending, so a failed load requires another start. `nci_set_vendor_cmds()` receives `sizeof(st_nci_vendor_cmds)`, matching existing kernel API expectations but worth checking if API changes.

## Test signals
Test each vendor subcommand, invalid payload lengths, vendor reply allocation failures, factory mode effect on SE discovery, firmware update sequencing start/load/end, loopback echo, manufacturer data reply, and reset behavior on HCI command failure.
