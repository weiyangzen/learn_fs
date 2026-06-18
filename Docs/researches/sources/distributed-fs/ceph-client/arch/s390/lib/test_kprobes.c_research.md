# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.c

## Purpose
KUnit suite validating s390 kprobe registration rejects invalid offsets inside instructions or odd byte positions while accepting valid function-entry probes.

## Important APIs, Types, And Functions
`setup_kprobe()` initializes a `struct kprobe` by symbol and offset. `test_kprobe_offset()` checks that registration succeeds at offset 0 and fails with `-EINVAL` at a supplied invalid offset. Test cases cover `kprobes_target_odd`, `kprobes_target_in_insn4`, `kprobes_target_in_insn6_lo`, and `kprobes_target_in_insn6_hi`. The suite is named `kprobes_test_s390`.

## Control Flow And State
Each test registers a probe at the target symbol start, unregisters on success, then attempts registration at a problematic offset and expects rejection. The file uses a single static `struct kprobe kp`; tests run through KUnit infrastructure.

## Dependencies And Integration
Depends on KUnit, kprobes, and symbols/offset constants emitted by `test_kprobes_asm.S` and declared in `test_kprobes.h`. Built under `CONFIG_S390_KPROBES_SANITY_TEST`.

## Risks And Test Signals
Risks include target assembly drift invalidating offsets, shared static kprobe state if tests become parallelized, and changed kprobe error codes. The test itself is a signal for instruction-boundary validation and probe decoder correctness.
