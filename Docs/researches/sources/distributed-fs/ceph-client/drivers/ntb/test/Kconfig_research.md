# sources/distributed-fs/ceph-client/drivers/ntb/test/Kconfig

## Purpose
Defines Kconfig entries for NTB test/debug clients: ping-pong, manual debug tool, raw performance tool, and MSI test.

## Important APIs, Types, And Functions
This file has no C APIs. It declares:
- `NTB_PINGPONG`: simple scratchpad/doorbell test client.
- `NTB_TOOL`: debugfs-driven NTB operation exerciser.
- `NTB_PERF`: raw MW transfer performance tool.
- `NTB_MSI_TEST`: MSI-over-NTB test client, depending on `NTB_MSI`.

## Control Flow
Kconfig selection controls which test modules are compiled. The `tristate` entries permit built-in or module builds and default to off by user choice.

## State And Persistence
No runtime state. It affects build configuration only.

## Dependencies And Integration Points
Integrates with the NTB test Makefile and NTB subsystem menu. `NTB_MSI_TEST` correctly guards itself behind the MSI helper.

## Risks And Edge Cases
The test clients expose low-level hardware access and should remain opt-in. Dependency declarations are minimal; build errors in optional APIs may surface only when selected.

## Test Signals
Menuconfig should show all four entries. `NTB_MSI_TEST` should be unavailable unless `NTB_MSI` is enabled. Module builds should produce corresponding objects through the Makefile.
