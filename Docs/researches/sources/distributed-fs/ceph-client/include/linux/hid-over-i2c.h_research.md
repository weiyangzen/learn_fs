# sources/distributed-fs/ceph-client/include/linux/hid-over-i2c.h

## Purpose
`hid-over-i2c.h` defines the wire-level constants and packed structures for the HID over I2C protocol. It is a transport contract for I2C HID controller drivers: it describes report packets, command encoding, report/power/opcode enums, and the fixed HID-I2C device descriptor.

## Important APIs, Types, And Functions
The important types are `enum hidi2c_report_type`, `enum hidi2c_power_state`, `enum hidi2c_opcode`, `struct hidi2c_report_packet`, and `struct hidi2c_dev_descriptor`. Macros such as `HIDI2C_PACKET_LEN()`, `HIDI2C_DATA_LEN()`, `HIDI2C_CMD_REPORT_ID`, `HIDI2C_CMD_REPORT_TYPE`, `HIDI2C_CMD_OPCODE`, `HIDI2C_CMD_3RD_BYTE`, and `HIDI2C_DEV_DESC_LEN` define packet length and bitfield extraction rules. There are no functions.

## Control Flow And State
Drivers read a device descriptor from the descriptor register, use register addresses and maximum report sizes from that descriptor, issue command words through `cmd_reg` and optional data through `data_reg`, and read/write report packets through input/output registers. State lives in device hardware and driver-private transport state; this header only defines serialized little-endian fields.

## Dependencies And Integration Points
It depends on `linux/bits.h` and kernel integer types. It integrates with HID core through low-level `hid_ll_driver` operations that parse descriptors, send `GET_REPORT`/`SET_REPORT`, set power, and deliver input packets as HID reports.

## Risks
Important risks are incorrect little-endian conversion, off-by-two length handling around the leading length field, invalid optional report ID encoding for IDs >= 15, duplicate `HIDI2C_CMD_OPCODE` macro definition, and trusting descriptor-provided `max_input_len`/`max_output_len` without buffer bounds. Protocol BCD and fixed descriptor length validation are critical.

## Test Signals
Test signals include descriptor length/version checks, short and extended report IDs, reset/get/set report commands, sleep/on transitions, maximum-sized input reports, malformed short packets, and HID core report parsing through an I2C transport driver.
