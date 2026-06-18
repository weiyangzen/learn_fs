# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_glink.c

## Purpose

`ucsi_glink.c` adapts Qualcomm PMIC GLINK USBC messages into the common UCSI core. It lets platforms where the PD controller is exposed through PMIC GLINK register a UCSI device, handle connector-change notifications, and optionally publish connector orientation from per-port GPIOs.

## Important APIs, Types, and Functions

`struct pmic_glink_ucsi` stores the GLINK client, UCSI handle, read/write completions, transaction mutex, PD service state, work items, and up to three orientation GPIOs. `pmic_glink_ucsi_read()` sends `UC_UCSI_READ_BUF_REQ`, waits up to five seconds for `read_ack`, and copies from the cached UCSI buffer. `pmic_glink_ucsi_locked_write()` builds a UCSI v1 or v2 write request based on `ucsi->version`. The `ucsi_operations` callbacks expose version, CCI, message-in, sync/async control, connector setup, and connector-status orientation. `pmic_glink_ucsi_callback()` dispatches GLINK read/write responses and notifications. `pmic_glink_ucsi_pdr_notify()` tracks PD service up/down and schedules registration work.

## Control Flow

Probe allocates the UCSI object, attaches Qualcomm SoC quirks from the parent compatible, reads optional child-node orientation GPIOs, creates the PMIC GLINK client, and registers it. Runtime UCSI reads/writes serialize through `lock` and complete from GLINK response callbacks. GLINK notify indications schedule work that rereads CCI and calls `ucsi_notify_common()`. PDR service state drives `ucsi_register()` when PD is up and `ucsi_unregister()` when PD goes down.

## State and Persistence Behavior

State is in memory only. `pd_running` and `ucsi_registered` gate UCSI lifetime; `read_buf` caches the last GLINK read response long enough to satisfy a UCSI core read. No device settings are persisted by this driver.

## Dependencies and Integration Points

It depends on the Qualcomm PMIC GLINK auxiliary device, service-registry/PDR notifications, UCSI core, Type-C orientation APIs, firmware child nodes, GPIO descriptors, and SoC-specific quirk flags such as `UCSI_NO_PARTNER_PDOS` and `UCSI_DELAY_DEVICE_PDOS`.

## Risks and Test Signals

Risks include response-length mismatches during unknown UCSI-version probing, timeouts leaving UCSI commands failed, races between GLINK callbacks and teardown, bad child `reg` values, and PD service flaps. Test signals include UCSI registration only after PDR up, v1/v2 buffer selection, read/write timeout behavior, orientation GPIO changes reflected on connector status, and clean unregister on auxiliary removal or PD down.
