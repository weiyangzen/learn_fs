<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h

## Purpose
Intel Debug Store/PEBS/BTS structure declarations for perf and low-level CPU tracing support. The header is 47 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/percpu-defs.h>`

Notable constants/macros: `#define _ASM_INTEL_DS_H`; `#define BTS_BUFFER_SIZE (PAGE_SIZE << 4)`; `#define PEBS_BUFFER_SHIFT 4`; `#define PEBS_BUFFER_SIZE (PAGE_SIZE << PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_MULTI ((PEBS_BUFFER_SIZE - PAGE_SIZE) >> PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_SINGLE 1`; `#define MAX_PEBS_EVENTS_FMT4 8`; `#define MAX_PEBS_EVENTS 32`; `#define MAX_PEBS_EVENTS_MASK GENMASK_ULL(MAX_PEBS_EVENTS - 1, 0)`; `#define MAX_FIXED_PEBS_EVENTS 16`

Notable declarations and inline helpers: `#define _ASM_INTEL_DS_H`; `#define BTS_BUFFER_SIZE (PAGE_SIZE << 4)`; `#define PEBS_BUFFER_SHIFT 4`; `#define PEBS_BUFFER_SIZE (PAGE_SIZE << PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_MULTI ((PEBS_BUFFER_SIZE - PAGE_SIZE) >> PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_SINGLE 1`; `#define MAX_PEBS_EVENTS_FMT4 8`; `#define MAX_PEBS_EVENTS 32`; `#define MAX_PEBS_EVENTS_MASK GENMASK_ULL(MAX_PEBS_EVENTS - 1, 0)`; `#define MAX_FIXED_PEBS_EVENTS 16`; `struct debug_store {`; `u64 bts_buffer_base;`; `u64 bts_index;`; `u64 bts_absolute_maximum;`; `u64 bts_interrupt_threshold;`; `u64 pebs_buffer_base;`; `u64 pebs_index;`; `u64 pebs_absolute_maximum;`; `u64 pebs_interrupt_threshold;`; `u64 pebs_event_reset[MAX_PEBS_EVENTS + MAX_FIXED_PEBS_EVENTS];`; `struct debug_store_buffers {`

## Control Flow
Perf configures DS buffers and CPU debug-store MSRs using these layouts to collect branch trace or precise event records.

## State and Persistence
State lives in per-CPU DS buffer memory and debug-store MSRs; records persist only until perf consumes or overwrites them.

## Dependencies and Integration Points
Depends on perf_event, Intel PMU, MSR access, CPU model quirks, and context-switch/debug handling.

## Risks
Risks include record layout mismatch, buffer overflow accounting, and CPU-model differences in PEBS/branch formats.

## Test Signals
Tests should run perf record with PEBS/BTS where supported, context-switch stress, NMI sampling, and CPU model matrix validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h -->
