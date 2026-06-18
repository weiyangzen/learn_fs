# sources/distributed-fs/ceph-client/drivers/ntb/test/Makefile

## Purpose
Maps NTB test Kconfig symbols to module objects.

## Important APIs, Types, And Functions
No runtime APIs. It builds:
- `ntb_pingpong.o` for `CONFIG_NTB_PINGPONG`
- `ntb_tool.o` for `CONFIG_NTB_TOOL`
- `ntb_perf.o` for `CONFIG_NTB_PERF`
- `ntb_msi_test.o` for `CONFIG_NTB_MSI_TEST`

## Control Flow
The kernel build system includes each object when its config symbol is `y` or `m`.

## State And Persistence
Build-only state. No runtime persistence.

## Dependencies And Integration Points
Relies on the sibling Kconfig symbols and the broader NTB build hierarchy.

## Risks And Edge Cases
No complex logic. The main risk is config/object name drift if source files or symbols are renamed.

## Test Signals
Selecting each config should produce the matching built-in object or module without unresolved symbols.
