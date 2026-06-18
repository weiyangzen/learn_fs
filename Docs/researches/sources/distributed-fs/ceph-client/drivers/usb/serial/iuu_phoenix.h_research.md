<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h

## Purpose
Defines USB IDs, command bytes, status/error codes, UART framing options, baud constants, clock constants, card-state bits, and VCC constants for the Infinity USB Unlimited Phoenix driver.

## Important APIs, Types, And Functions
The USB binding constants are `IUU_USB_VENDOR_ID` and `IUU_USB_PRODUCT_ID`. Programmer command constants include product/version/status reads, LED setting, waits, reset set/clear, VCC setting, UART enable/disable, I2C writes, UART escape/trap/RX/TX/change operations, AVR/PIC/EEPROM programming commands, and delay encoding. Status codes such as `IUU_OPERATION_OK`, `IUU_INVALID_PARAMETER`, `IUU_WRITE_ERROR`, and `IUU_RX_ERROR` provide symbolic results. UART settings include parity modes, one/two stop bits, fixed baud codes, and the supported clock frequencies `IUU_CLK_3579000`, `IUU_CLK_3680000`, and `IUU_CLK_6000000`.

## Control Flow
This header has no executable flow. In `iuu_phoenix.c`, the command constants drive all device communication: open sends UART enable and clock commands, the poll loop sends `IUU_UART_RX`, writes use `IUU_UART_ESC` plus `IUU_UART_TX`, baud changes use `IUU_UART_CHANGE`, reset uses `IUU_RST_SET`/`IUU_RST_CLEAR`, LEDs use `IUU_SET_LED`, and sysfs VCC changes use `IUU_SET_VCC`.

## State And Persistence
The header does not own state, but its constants encode transient device state changes. VCC, clock, UART enablement, reset, LED color, and UART baud/parity are all device-side state selected through these command values.

## Dependencies And Integration Points
It is included directly by `iuu_phoenix.c` and must match the Infinity USB Unlimited firmware command protocol. The USB IDs integrate with Linux usb-serial device matching.

## Risks And Edge Cases
The command namespace includes many programming commands that the researched C file does not currently use, so future expansion must verify command semantics before exposing them. Several status names contain historical typos such as `IUU_INVALID_voidERFACE`, and consumers should not infer Linux errno values from these numeric protocol constants. `IUU_VCC_5V` and `IUU_VCC_3V` are defined as protocol values, while the C sysfs path sends literal 3 or 5, a mismatch worth checking against hardware behavior.

## Test Signals
Build success confirms all command names used by `iuu_phoenix.c` resolve. Hardware tests should verify the USB ID binds, UART enable/disable commands work, baud and clock constants produce expected card timing, reset and LED commands are accepted, and VCC command values match the reader firmware contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h -->
