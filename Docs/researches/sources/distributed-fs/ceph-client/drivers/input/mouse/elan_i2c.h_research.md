# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c.h

## Purpose

`elan_i2c.h` is the shared contract between the Elan touchpad core and its I2C/SMBus transport backends. It defines report IDs/layout offsets, common mode bits, firmware-update constants, product IDs, the IAP mode enum, the transport operation table, and extern declarations for the two backend implementations.

## Important APIs, Types, and Functions

Important constants include `ETP_ENABLE_ABS`, `ETP_ENABLE_CALIBRATE`, report IDs `ETP_REPORT_ID`, `ETP_REPORT_ID2`, `ETP_TP_REPORT_ID`, `ETP_TP_REPORT_ID2`, report offsets, `ETP_MAX_REPORT_LEN`, `ETP_MAX_FINGERS`, firmware page sizes, firmware signature size, and product IDs used for quirks. `enum tp_mode` distinguishes `IAP_MODE` and `MAIN_MODE`. `struct elan_transport_ops` is the central ABI between core and transports, covering initialization, sleep/power/mode control, calibration, baseline, version/product/checksum/geometry queries, IAP reset/update, report feature discovery, report reads, pressure adjustment, and pattern query.

## Control Flow

The header has no runtime control flow. At probe time, `elan_i2c_core.c` selects either `elan_i2c_ops` or `elan_smbus_ops`, then drives all device operations through this table. The report ID/offset constants are used in IRQ decoding for touchpad, high-precision touchpad, and optional trackpoint packets.

## State and Persistence Behavior

This file defines no storage, but it determines how state is represented by the core: report geometry, firmware metadata, calibration state, IAP mode, and firmware page/update parameters. The firmware constants also define the expected naming and signature contract for persistent device firmware updates.

## Dependencies and Integration Points

It depends on Linux integer types and forward-declares `struct i2c_client` and `struct completion`. It is included by `elan_i2c_core.c`, `elan_i2c_i2c.c`, and `elan_i2c_smbus.c`, making operation-table compatibility the main integration point.

## Risks and Edge Cases

Any signature change in `struct elan_transport_ops` must be implemented by both transports. Shared report offsets must remain valid for both full I2C and SMBus packet layouts; SMBus fakes the same offsets by reading into an offset buffer. Product IDs in this header feed quirks in the core, so missing IDs can affect resume behavior and firmware handling.

## Test Signals

Build tests should cover both `CONFIG_MOUSE_ELAN_I2C_I2C` and `CONFIG_MOUSE_ELAN_I2C_SMBUS`. Runtime tests should verify all ops are populated, report IDs dispatch correctly, firmware page-size constants match selected IC/IAP versions, firmware names include product IDs, and property/quirk handling recognizes the listed product IDs.
