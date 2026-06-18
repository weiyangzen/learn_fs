# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/copy_first_unaligned.c

## Purpose
Verifies that an unaligned PowerPC `copy_first` instruction causes SIGBUS rather than silently succeeding.

## Important APIs, Types, and Functions
Defines `signal_action_handler()` to check `si_signo`, `si_code == BUS_ADRALN`, and `si_addr`; `setup_signal_handler()` installs it; `test_copy_first_unaligned()` emits `PPC_INST_COPY_FIRST` on an intentionally unaligned pointer.

## Control Flow
The test installs a SIGBUS handler, executes the unaligned instruction, and expects the handler to terminate with success. Reaching normal return is a failure.

## State and Persistence
No durable state. It uses process signal disposition and stack memory only.

## Dependencies and Integration Points
Depends on `instructions.h` raw instruction encoding, `utils.h` harness macros, and PowerPC copy/paste instruction support.

## Risks and Test Signals
Risk is running on hardware/kernel combinations without the expected copy instruction behavior. Test signal is process exit through the signal handler with matching address/code.
