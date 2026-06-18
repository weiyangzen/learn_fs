# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_osdep.h

## Purpose
This header is the OS-dependent glue for the legacy `e1000` shared hardware code. It maps generic e1000 register operations onto Linux I/O primitives and hides register layout differences between 82542-era parts and later devices.

## Important APIs, Types, and Functions
It defines MMIO helpers `er32(reg)` and `ew32(reg, value)` for read/write of scalar registers using a local `struct e1000_hw *hw`. It also defines array register helpers for dword, word, and byte widths, `E1000_WRITE_FLUSH()` as a status read flush, ICH flash access helpers, and CE4100-style configuration RAM/flash helpers based on `CONFIG_RAM_BASE`, `GBE_CONFIG_OFFSET`, and `phys_to_virt()`.

## Control Flow
There is no executable control flow beyond macro expansion. Callers pass either the implicit local `hw` variable or an explicit `struct e1000_hw *a`. Each access selects the register offset by checking `mac_type >= e1000_82543`; older 82542 devices use alternate register constants. Writes go through `writel`, `writew`, or `writeb`; reads go through `readl`, `readw`, or `readb`. `E1000_WRITE_FLUSH()` forces posted MMIO writes to reach the device by reading STATUS.

## State and Persistence
The header stores no state. It mutates hardware MMIO registers and flash/config spaces through the caller's mapped base pointers: `hw->hw_addr`, `hw->flash_address`, or CE4100 config address macros. Correct behavior depends on those mappings being valid and on the caller selecting the correct access width and offset.

## Dependencies and Integration Points
It includes `<asm/io.h>` and depends on Linux I/O accessors plus register constants from the e1000 headers. It is used by `e1000_main.c` and shared hardware files to keep register accesses compact and consistent. The implicit `hw` dependency in `er32`/`ew32` is a notable integration convention: functions using those macros must have a local variable named `hw`.

## Risks
Risks are mostly low-level and severe: wrong register selection for 82542 versus later devices, missing flushes after control writes, invalid MMIO pointers after remove/suspend/error recovery, and incorrect word/byte array offset shifts. The CE4100 config macros use physical-to-virtual mapping assumptions and replicated I/O helpers, so misuse can hit the wrong memory-mapped area. Because these are macros, type checking and side-effect protection are limited.

## Test Signals
Build coverage is important because macro users must compile in context. Runtime signals include successful probe/reset/link operations across both older 82542 and newer devices, register dump sanity, EEPROM/flash access where supported, and absence of MMIO faults during suspend/resume, remove, and PCI error recovery.
