# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_local.h

## Purpose

`irq_local.h` is the local include layer for the `irq` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `irq_global.h`, `irq_controller_defs.h`, `hive_isp_css_defs.h`, `input_formatter_subsystem_defs.h`, `input_system_defs.h`, `input_selector_defs.h`. Important macros/constants include `__IRQ_LOCAL_H_INCLUDED__`, `HIVE_GP_DEV_IRQ_NUM_IRQS`, `HIVE_IFMT_IRQ_NUM_IRQS`, `IRQ_ID_OFFSET`, `IRQ0_ID_OFFSET`, `IRQ1_ID_OFFSET`, `IRQ2_ID_OFFSET`, `IRQ3_ID_OFFSET`, `IRQ_END_OFFSET`, `IRQ0_ID_N_CHANNEL`.

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
