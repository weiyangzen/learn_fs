<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h

## Purpose

`arm64_exception_types.h` provides ARM64 KVM exception and ESR exception-class constants plus macro tables that map numeric exit values to display names for `perf kvm stat`.

## Important APIs, Types, and Functions

The file defines `ARM_EXCEPTION_*` values, `HVC_STUB_ERR`, the `kvm_arm_exception_type` table macro, ESR exception-class constants `ESR_ELx_EC_*`, `ECN(x)`, and `kvm_arm_exception_class`.

## Control Flow

There is no executable control flow. `kvm-stat-arm64.c` expands these macros into `exit_reasons_table` arrays and selects the basic exception table or ESR class table depending on whether the exit reason is `ARM_EXCEPTION_TRAP`.

## State and Persistence Behavior

The mappings are static source metadata. They must track kernel UAPI/asm values so recorded tracepoint fields decode correctly.

## Dependencies and Integration Points

The constants mirror Linux ARM64 `asm/virt.h`, `asm/kvm_asm.h`, and `asm/esr.h` values and integrate with common `exit_event_decode_key()`.

## Risks and Edge Cases

Stale constants cause misleading VM-exit names. The class table intentionally omits some unallocated or newer EC values, so unknown values decode as `UNKNOWN`.

## Test Signals

Tests should feed ARM64 `kvm_exit` samples for IRQ, SERROR, TRAP with ESR EC, illegal exception, and unknown EC values and verify decoded names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h -->
