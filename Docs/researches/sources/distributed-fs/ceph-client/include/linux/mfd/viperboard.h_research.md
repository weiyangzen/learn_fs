# sources/distributed-fs/ceph-client/include/linux/mfd/viperboard.h

## Purpose
`viperboard.h` defines USB protocol constants and packed message formats for Nano River Technologies Viperboard MFD support, especially its USB-backed I2C, ADC, and GPIO functions.

## Important APIs, Types, and Functions
Constants define USB IN/OUT endpoints, a 512-byte I2C message limit, I2C bus frequency command values, I2C write/read/address command values, USB control request types, timeout, and vendor request IDs for I2C frequency, I2C transfer, major/minor version, ADC, and GPIO banks. Packed structs describe I2C write/read headers, status response, write/read messages with payload, address messages, and parent `struct vprbrd` containing USB device, mutex, shared transfer buffer, and platform device.

## Control Flow
The USB parent serializes access with `vprbrd.lock`, fills one of the packed request buffers, sends vendor control/bulk transfers to the fixed endpoints/requests, and child platform devices implement I2C/GPIO/ADC behavior using the shared buffer and protocol constants.

## State and Persistence Behavior
Hardware/firmware state includes selected I2C frequency, GPIO bank state, ADC state, and active USB transfer status. Software state is minimal: USB device pointer, one mutex-protected buffer sized for the largest write message, and embedded child platform device.

## Dependencies and Integration Points
The header depends on Linux types and USB APIs. It integrates with the MFD parent, USB core, I2C adapter implementation, GPIO controller, ADC interface, and platform-device child registration.

## Risks and Test Signals
Risks include packed-struct ABI drift, endianness assumptions for unannotated `u16` fields, buffer overrun if payload length exceeds `VPRBRD_I2C_MSG_LEN`, concurrent child transfers without the mutex, and USB timeout handling. Test signals are USB descriptor/probe tests, firmware version requests, I2C transfer tests at each supported frequency, oversized-message rejection, GPIOA/B request tests, ADC request tests, and disconnect-during-transfer handling.
