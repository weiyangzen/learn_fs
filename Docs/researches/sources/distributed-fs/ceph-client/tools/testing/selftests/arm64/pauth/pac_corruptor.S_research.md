# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac_corruptor.S

## Purpose

This assembly helper deliberately corrupts a return-address PAC to prove authentication faults are delivered.

## Important APIs, Types, and Functions

It exports `pac_corruptor`, executes `paciasp`, flips bit 53 of `lr`, executes `autiasp`, and returns.

## Control Flow and Data Flow

The function signs the current return address, mutates a PAC bit outside the top byte, authenticates with the IA key, and attempts to return. Correct hardware/kernel behavior raises SIGSEGV or SIGILL before normal return.

## State and Persistence Behavior

It mutates only the link register and uses current PAC key state. There is no memory or persistent state.

## Dependencies and Integration Points

It is linked into `pac` and called under a temporary signal handler in `TEST(corrupt_pac)`.

## Risks and Edge Cases

The chosen bit assumes default TBI and PAC placement. If architecture or VA-size assumptions change, the corruption bit may need review.

## Test Signals

The calling test passes only if SIGSEGV or SIGILL is observed; returning normally is a failure.
