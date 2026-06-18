# sources/distributed-fs/ceph-client/drivers/auxdisplay/img-ascii-lcd.c

## Purpose
Supports simple memory-mapped or syscon-backed ASCII LCDs on Imagination/MIPS boards. It adapts board-specific register layouts for Boston, Malta, and SEAD3 into the generic line-display sysfs interface.

## Important APIs, Types, And Functions
- `struct img_ascii_lcd_config` describes character count, external regmap usage, and line-display ops.
- `struct img_ascii_lcd_ctx` stores the `linedisp`, MMIO base or regmap, and register offset.
- Board update functions: `boston_update()`, `malta_update()`, and `sead3_update()`.
- SEAD3 helpers `sead3_wait_sm_idle()` and `sead3_wait_lcd_idle()` poll CPLD/LCD busy state.
- `img_ascii_lcd_probe()` maps resources/registers and registers the line display.

## Control Flow
OF match data selects a config. Probe allocates context, either gets a syscon regmap plus `offset` property or maps platform MMIO resource 0, then calls `linedisp_register()`. It adds a compatibility sysfs link named `message` from the parent device to the linedisp child. Remove deletes the link and unregisters the line display.

## State And Persistence
State is per platform device: line-display buffers/message/timer are owned by the line-display core, and hardware access state is the MMIO pointer or regmap/offset. Displayed content persists in hardware until overwritten; software message state persists until unregister.

## Dependencies And Integration Points
Depends on platform devices, OF match data, syscon/regmap, raw MMIO writes for Boston, and `line-display` exported namespace. Userspace interacts through `linedisp.N/message` and the backwards-compatible link.

## Risks And Edge Cases
Boston uses raw word writes by casting the character buffer to native word sizes, making byte ordering architecture-sensitive but matching board expectations. SEAD3 busy polling has no timeout, so broken hardware can spin indefinitely in update. The compatibility sysfs link is a second path that must be removed on failure/remove.

## Test Signals
Probe each compatible, missing `offset` for syscon variants, sysfs message updates, SEAD3 busy/error paths with rate-limited errors, compatibility link creation/removal, and long-message scrolling through line-display are key signals.
