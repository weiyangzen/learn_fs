# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_regs.c

## Purpose

This testcase checks that an enabled ZA context includes register payload of the correct size and zero contents.

## Important APIs, Types, and Functions

The key implementation is `setup_za_regs()` starts ZA and `do_one_sme_vl()` validates `ZA_MAGIC`, VL, size, data, and post-capture SVCR. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
