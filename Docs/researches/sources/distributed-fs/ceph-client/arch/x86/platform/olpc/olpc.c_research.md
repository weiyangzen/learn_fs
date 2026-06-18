<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c

## Purpose
Provides OLPC platform detection, EC command transport, EC suspend/resume behavior, and registration of OLPC platform devices.

## Important APIs, Types, And Functions
Exports `olpc_platform_info`. `olpc_xo1_ec_cmd()` implements port `0x6c/0x68` EC command protocol with IBF/OBF waits and OBF restart retries. `platform_detect()` checks OF root architecture and board revision. `olpc_init()` registers model-specific EC drivers, `olpc-ec`, XO-1 devices, DCON flags, and optional PCI init override.

## Control Flow
Boot parameter `olpc_ec_timeout=` adjusts command timeouts. `postcore_initcall` requires OFW presence and OLPC architecture, then chooses XO-1 vs XO-1.5 EC driver based on board revision. XO-1 EC suspend inhibits SCIs; resume releases inhibition and wakes WLAN twice.

## State And Persistence
Global `olpc_platform_info` records board revision and feature flags. `ec_timeout` persists from boot parameter. EC command effects and registered platform devices persist across runtime.

## Dependencies And Integration Points
Depends on OpenFirmware/device-tree availability, OLPC EC core, Geode/VSA PCI support, DCON users, platform devices, and x86 PCI init hooks.

## Risks And Edge Cases
The EC protocol is timing-sensitive and uses busy millisecond waits. OBF timeouts can restart commands up to ten times. Board revision gates many downstream devices, so incorrect DT properties misconfigure the platform.

## Test Signals
OLPC board revision logs, successful `olpc-ec` registration, EC command success, XO-1 rfkill/platform devices, and suspend/resume EC behavior are main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c -->
