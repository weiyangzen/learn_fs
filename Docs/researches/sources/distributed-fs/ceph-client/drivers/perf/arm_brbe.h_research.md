# sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.h

Purpose: Declares the BRBE helper interface used by the ARM PMU perf driver and provides safe stubs when `CONFIG_ARM64_BRBE` is disabled.

Important APIs and types: Forward-declares `struct arm_pmu`, `struct perf_branch_stack`, and `struct perf_event`. Under `CONFIG_ARM64_BRBE`, it declares `brbe_probe()`, `brbe_num_branch_records()`, `brbe_invalidate()`, `brbe_enable()`, `brbe_disable()`, `brbe_branch_attr_valid()`, and `brbe_read_filtered_entries()`. The disabled configuration returns zero/no-op for capability/control helpers and makes branch-stack validation fail with a warning if called on a branch-stack event.

Control flow: There is no runtime control flow in enabled builds beyond function linkage. In disabled builds, callers can compile unchanged: probing does nothing, branch record count is zero, enable/disable/invalidate are no-ops, branch attribute validation returns false, and filtered read leaves the stack untouched.

State and persistence: The header owns no state. It defines the compile-time contract between the ARM PMU core and `arm_brbe.c`, including the behavior when BRBE support is absent.

Dependencies and integration points: Depends on ARM PMU/perf types and the `CONFIG_ARM64_BRBE` Kconfig symbol. The stubs call `has_branch_stack()` and `WARN_ON_ONCE()`, so include order must provide those declarations through the ARM PMU/perf context.

Risks: Signature drift breaks ARM PMU integration at compile time. The disabled stub for `brbe_read_filtered_entries()` is declared `static` rather than `static inline`, which is acceptable for a header-local no-op but should not grow logic. Callers must still gate branch-stack support on `brbe_branch_attr_valid()` or record count.

Test signals: Compile both BRBE-enabled and disabled configurations, verify no unresolved symbols, and confirm branch-stack events are rejected cleanly when disabled.
