# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_firmware.c

Purpose: Loads, validates, and executes Realtek r8169 PHY firmware scripts encoded as 32-bit opcodes.

Important APIs and functions: `rtl_fw_request_firmware()` requests firmware by name and validates format and opcode ranges. `rtl_fw_write_firmware()` interprets opcodes against PHY or MAC MCU read/write callbacks. `rtl_fw_release_firmware()` releases the firmware. Internal validators are `rtl_fw_format_ok()` and `rtl_fw_data_ok()`.

Control flow: Format validation supports a headered format with zero magic, checksum over the whole file, version string, start offset, and opcode count, plus a raw opcode format used when magic is nonzero. Data validation scans all opcodes, verifies branch/skip targets remain in range, validates MDIO selector values, and rejects unknown opcodes. Execution maintains `predata`, `count`, active read/write callback pair, and an instruction index. Opcodes read, OR/AND previous data, branch backward, switch MDIO target, clear read count, write literal or previous values, conditionally skip, unconditionally skip, and delay in milliseconds.

State and persistence: Firmware data remains in `rtl_fw->fw`, parsed action pointer/size, and version string until release. Execution writes hardware registers through callbacks but does not persist interpreter state after completion.

Dependencies and integration: Uses Linux firmware loader, endian helpers, device logging, and callbacks supplied by r8169 main/PHY code. It is built into the composite r8169 object.

Risks and test signals: Risks include malformed firmware bounds, checksum/header interpretation, backward branch loops, hardware callback side effects, and version string truncation. Tests should cover missing firmware warnings, headered/raw valid firmware, invalid opcodes, out-of-range skip/branch, MDIO selector validation, and interpreter callback sequences.
