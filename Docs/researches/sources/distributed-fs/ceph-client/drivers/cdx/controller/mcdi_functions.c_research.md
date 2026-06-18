# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.c

## Purpose
This file provides typed CDX firmware operations on top of the generic MCDI RPC engine. It turns controller needs such as enumeration, device configuration, reset, bus control, MSI writes, and device control flags into concrete MCDI commands.

## Important APIs, Types, and Functions
Public helper APIs are `cdx_mcdi_get_num_buses()`, `cdx_mcdi_get_num_devs()`, `cdx_mcdi_get_dev_config()`, `cdx_mcdi_bus_enable()`, `cdx_mcdi_bus_disable()`, `cdx_mcdi_write_msi()`, `cdx_mcdi_reset_device()`, `cdx_mcdi_bus_master_enable()`, and `cdx_mcdi_msi_enable()`. Internal helpers `cdx_mcdi_ctrl_flag_get()` and `cdx_mcdi_ctrl_flag_set()` implement read-modify-write of device control flags.

## Control Flow
Enumeration first calls `MC_CMD_CDX_BUS_ENUM_BUSES`, then per bus `MC_CMD_CDX_BUS_ENUM_DEVICES`, then per device `MC_CMD_CDX_BUS_GET_DEVICE_CONFIG`. Device config decoding copies bus/device IDs, requester IDs, MSI device ID/count, identity fields, revision, class, and up to four non-empty MMIO resources into `struct cdx_dev_params`. Control helpers build small input buffers and call `cdx_mcdi_rpc()`.

## State and Persistence Behavior
The helpers do not keep state. They populate caller-owned `cdx_dev_params` and rely on firmware to persist bus reset state, device reset state, MSI enable state, bus-master state, and MSI message programming.

## Dependencies and Integration Points
It depends on MCDI buffer macros and protocol offsets from `mcdid.h`/`mc_cdx_pcol.h`, the generic `cdx_mcdi_rpc()` API, Linux resource flags, and the private CDX bus add parameter structure. It is used by `cdx_controller.c` controller callbacks.

## Risks
Strict output length checks return `-EIO` on version mismatch; firmware ABI changes will break enumeration until handled. `cdx_mcdi_get_dev_config()` appends resources without checking against `MAX_CDX_DEV_RESOURCES`, relying on exactly four protocol regions matching array capacity. `cdx_mcdi_ctrl_flag_set()` performs read-modify-write without concurrency protection at firmware level, so simultaneous flag updates can race unless firmware serializes per device. Bus/device number validity is delegated to firmware.

## Test Signals
Mock MCDI responses should verify length validation, all MMIO region combinations, class masking to 24 bits, requester/MSI device ID mapping, bus up/down commands, reset command payloads, MSI write payloads, and control flag preservation when toggling bus master or MSI enable.
