# sources/distributed-fs/ceph-client/drivers/mmc/core/host.h

## Purpose
Private host declarations and small capability/timing helpers for MMC core users.

## Important APIs, Types, And Functions
- Declares host class and retuning helper functions.
- Inline helpers clear, hold, and recheck retune state.
- Capability predicates check CMD23, done-complete, boot access, and UHS.
- Timing predicates check HS200, DDR52, HS400, HS400 enhanced strobe, and SD Express.

## Control Flow
Core, protocol, and block code include this header to make feature decisions and manage retuning around operations.

## State And Persistence
No owned state. Inline helpers mutate retune fields and read capability/IOS fields.

## Dependencies And Integration Points
Depends on public `linux/mmc/host.h`; integrates host lifecycle, request handling, protocol mode switching, and block recovery.

## Risks And Edge Cases
Unbalanced inline retune manipulation can leave tuning disabled or forced. Timing predicates reflect current IOS and can change during resets/mode switches.

## Test Signals
Compile coverage; runtime CMD23 selection, done-complete path, boot partition access, UHS/HS timing, and balanced retune state after recovery.
