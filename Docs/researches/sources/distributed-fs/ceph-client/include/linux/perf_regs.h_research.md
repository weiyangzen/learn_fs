<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_regs.h

## Purpose
Defines the generic perf register capture wrapper and architecture hooks used to validate, read, and expose sampled register values to perf.

## Important APIs, Types, And Functions
- `struct perf_regs` stores `struct pt_regs *regs` and a register ABI selector.
- When `CONFIG_HAVE_PERF_REGS` is enabled, architecture `<asm/perf_regs.h>` supplies `PERF_REG_EXTENDED_MASK` and implementations for `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`.
- Without register support, inline stubs return zero or `-EINVAL` and clear `regs_user->regs`.

## Control Flow
Perf sampling code asks the architecture to validate a user-requested register mask, determine the ABI for a task, extract register values from `pt_regs`, and populate user register snapshots. In unsupported builds, validation fails and register capture is disabled.

## State And Persistence
The only state is the transient `perf_regs` view used while constructing samples. It references `pt_regs` owned by interrupt, exception, or task stack contexts and does not persist register storage itself.

## Dependencies And Integration Points
Includes task stack helpers and optional architecture perf register definitions. Integrates with perf sample types `PERF_SAMPLE_REGS_USER` and `PERF_SAMPLE_REGS_INTR`, callchain capture, and BPF perf event register views.

## Risks And Edge Cases
Risks include stale `pt_regs` pointers, exposing registers with the wrong ABI, accepting unsupported masks, architecture stubs hiding missing support, and user-register capture from tasks without a valid saved user register frame.

## Test Signals
Run perf register sampling on supported architectures, validate bad masks return `-EINVAL`, test 32-bit compatibility tasks on 64-bit kernels, sample interrupt and user registers, and build unsupported architectures to confirm clean stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_regs.h -->
