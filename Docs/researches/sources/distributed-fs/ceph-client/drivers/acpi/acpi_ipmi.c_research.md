# sources/distributed-fs/ceph-client/drivers/acpi/acpi_ipmi.c

## Purpose
`acpi_ipmi.c` implements the ACPI IPMI operation-region handler. It lets AML issue IPMI commands through a selected ACPI-described BMC system interface and returns IPMI responses in the ACPI-defined request/response buffer format.

## Important APIs, Types, And Functions
Core structures are `struct acpi_ipmi_device`, `struct ipmi_driver_data`, `struct acpi_ipmi_msg`, and `struct acpi_ipmi_buffer`. Important functions include `ipmi_dev_alloc()`, `__ipmi_dev_kill()`, `acpi_ipmi_dev_get()`, `ipmi_msg_alloc()`, `acpi_format_ipmi_request()`, `acpi_format_ipmi_response()`, `ipmi_flush_tx_msg()`, `ipmi_cancel_tx_msg()`, `ipmi_msg_handler()`, `ipmi_register_bmc()`, `ipmi_bmc_gone()`, `acpi_ipmi_space_handler()`, `acpi_wait_for_acpi_ipmi()`, `acpi_ipmi_init()`, and `acpi_ipmi_exit()`.

## Control Flow
Module init installs an `ACPI_ADR_SPACE_IPMI` handler at the root and registers an IPMI SMI watcher. When an ACPI-backed BMC appears, `ipmi_register_bmc()` creates an IPMI user, records the ACPI handle, selects the first SMI if none is selected, completes the selection wait, and adds it to the device list. AML write accesses allocate a message tied to the selected SMI, format netfn/cmd from the OpRegion address, copy request data from the ACPI buffer, assign a message ID, add the message to the pending list, send it with `ipmi_request_settime()`, wait for completion, and format the response back into the ACPI buffer. The IPMI receive handler matches response message IDs, copies bounded response data, sets ACPI completion status, completes the pending request, and releases references. Exit unregisters the watcher, kills devices, flushes pending messages, and removes the address-space handler.

## State And Persistence
State is in memory: the selected SMI, list of IPMI devices, per-device pending transmit lists, message IDs, completions, dead flags, and krefs. ACPI OpRegion transactions are synchronous from AML's perspective but backed by asynchronous IPMI receive callbacks.

## Dependencies And Integration Points
It depends on ACPI address-space handling, the IPMI core, `ipmi_smi_watcher`, completions, spinlocks, krefs, and ACPI firmware using IPMI OpRegions. `acpi_wait_for_acpi_ipmi()` is exported so other ACPI code can wait briefly for BMC selection.

## Risks
The removal path in `ipmi_bmc_gone()` appears to remove an entry when `iter->ipmi_ifnum != iface`, which is surprising because the gone callback should target the matching interface; this deserves review. The code intentionally skips parsing IPMB `SEND_MESSAGE` addressing. Response handling sets `msg->recv_type = IPMI_RESPONSE_RECV_TYPE` before checking it, making that condition tautological. Timeouts and BMC removal must correctly complete and release pending messages to avoid stuck AML execution.

## Test Signals
Tests should cover no selected SMI, ACPI-backed and non-ACPI SMI registration, multiple BMCs, BMC removal, request length overflow, response length overflow, timeout completion code, pending request flush during exit, and AML write/read behavior for the IPMI OpRegion.
