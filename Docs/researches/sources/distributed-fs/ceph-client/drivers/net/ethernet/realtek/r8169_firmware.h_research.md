# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.h

Purpose: Declares the r8169 firmware interpreter data structures and public firmware lifecycle/execution functions.

Important APIs and types: `rtl_fw_write_t` and `rtl_fw_read_t` abstract register access callbacks. `RTL_VER_SIZE` bounds firmware version strings. `struct rtl_fw` stores PHY and MAC MCU callbacks, firmware pointer/name/device, parsed version, and `rtl_fw_phy_action` opcode pointer/size.

Control flow and integration: r8169 hardware setup fills `struct rtl_fw`, calls request, optionally writes firmware, then releases it. The function-pointer design lets the interpreter switch between PHY and MAC MCU register spaces.

State and persistence: Holds firmware object lifetime state and parsed action metadata. Hardware writes caused by execution persist in device registers.

Risks and test signals: Risks include uninitialized callbacks, lifetime misuse after release, and version buffer assumptions. Compile tests validate declarations, while runtime tests should exercise request/write/release order and failure handling.
