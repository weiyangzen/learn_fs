<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c

## Purpose

`test_FCOMI.c` tests x87 floating-point compare instructions that update integer flags, including ordered and unordered variants, pop variants, quiet NaN, and signaling NaN behavior.

## Important APIs, Types, and Functions

The file defines flag-result enums, NaN test data, and helpers `test()`, `test_qnan()`, `testu_qnan()`, `testu_snan()`, `testp()`, `testp_qnan()`, and `testup_qnan()`. Each uses inline x87 assembly to execute `fcomi/fucomi` style instructions and return flag state. `sighandler()` catches floating or illegal instruction signals.

## Control Flow and State

`main()` initializes signal handling, executes compare variants with baseline flags, and validates result globals such as `res_fcomi_pi_1`, `res_fcomi_1_pi`, and NaN cases. State is in global result variables and process signal status.

## Dependencies and Integration Points

It depends on x87 compare instruction availability, assembler support, EFLAGS extraction, and Linux signal behavior for exceptional floating-point cases. It is part of x86 instruction selftest coverage.

## Risks and Test Signals

Risks include incorrect unordered compare flag results, pop/no-pop x87 stack mistakes, mishandling signaling NaNs, and emulator differences. Passing output means all compare-result flags match expected values without unexpected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c -->
