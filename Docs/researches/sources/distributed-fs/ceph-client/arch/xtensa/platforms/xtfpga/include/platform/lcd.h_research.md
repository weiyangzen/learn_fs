# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/lcd.h

Purpose: Declares optional XTFPGA LCD display helpers or provides no-op stubs when LCD support is disabled.

Important APIs, types, and functions: `lcd_disp_at_pos()`, `lcd_shiftleft()`, and `lcd_shiftright()`.

Control flow: With `CONFIG_XTFPGA_LCD`, declares external functions implemented by LCD support. Without it, inline stubs do nothing so callers can compile unconditionally.

State and persistence: Real implementation would mutate LCD display state; stub implementation has no state.

Dependencies and integration: `CONFIG_XTFPGA_LCD`, optional `lcd.o` from platform Makefile, and board UI/status code.

Risks: Stubbed calls can hide missing LCD support in tests; function prototypes use mutable `char *` for display text.

Test signals: Build with LCD disabled and enabled, call sites link correctly, and LCD display operations work on board when enabled.
