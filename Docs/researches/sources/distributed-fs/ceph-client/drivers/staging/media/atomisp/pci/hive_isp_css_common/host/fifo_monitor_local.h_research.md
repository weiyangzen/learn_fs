# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_local.h

## Purpose

`fifo_monitor_local.h` is the local include layer for the `fifo monitor` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `fifo_monitor_global.h`, `hive_isp_css_defs.h`. Important macros/constants include `__FIFO_MONITOR_LOCAL_H_INCLUDED__`, `_hive_str_mon_valid_offset`, `_hive_str_mon_accept_offset`, `FIFO_CHANNEL_SP_VALID_MASK`, `FIFO_CHANNEL_SP_VALID_B_MASK`, `FIFO_CHANNEL_ISP_VALID_MASK`, `FIFO_CHANNEL_MOD_VALID_MASK`. Important types include `fifo_switch`, `fifo_channel`, `fifo_switch_t`, `fifo_channel_t`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
