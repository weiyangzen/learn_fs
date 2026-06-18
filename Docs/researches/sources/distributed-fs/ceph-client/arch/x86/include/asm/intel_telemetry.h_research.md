<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h

## Purpose
Intel telemetry interface declarations for SoC telemetry event/configuration access. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/platform_data/x86/intel_scu_ipc.h>`

Notable constants/macros: `#define INTEL_TELEMETRY_H`; `#define TELEM_MAX_EVENTS_SRAM 28`; `#define TELEM_MAX_OS_ALLOCATED_EVENTS 20`

Notable declarations and inline helpers: `#define INTEL_TELEMETRY_H`; `#define TELEM_MAX_EVENTS_SRAM 28`; `#define TELEM_MAX_OS_ALLOCATED_EVENTS 20`; `enum telemetry_unit {`; `struct telemetry_evtlog {`; `u32 telem_evtid;`; `u64 telem_evtlog;`; `struct telemetry_evtconfig {`; `u32 *evtmap;`; `u8 num_evts;`; `u8 period;`; `struct telemetry_evtmap {`; `u32 evt_id;`; `struct telemetry_unit_config {`; `struct telemetry_evtmap *telem_evts;`; `void __iomem *regmap;`; `u8 ssram_evts_used;`; `u8 curr_period;`; `u8 max_period;`; `u8 min_period;`; `struct telemetry_plt_config {`; `struct telemetry_unit_config pss_config;`; `struct telemetry_unit_config ioss_config;`; `struct mutex telem_trace_lock;`

## Control Flow
Telemetry users configure sampling/events and read telemetry data through platform-specific backend functions.

## State and Persistence
State is telemetry hardware configuration, event masks, and buffers managed by implementation files.

## Dependencies and Integration Points
Depends on Intel SoC platform drivers, IPC/IOSF-style access paths, and power/thermal subsystems.

## Risks
Risks include unsupported platform access, stale event IDs, and races with firmware-managed telemetry state.

## Test Signals
Tests should include platform probe, telemetry read/config calls, invalid event handling, suspend/resume, and non-supported build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h -->
