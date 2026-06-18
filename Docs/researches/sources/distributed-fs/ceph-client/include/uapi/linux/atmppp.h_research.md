<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h

## Purpose
Defines the PPP over ATM backend selection payload and encapsulation constants for RFC2364 support.

## Important APIs, Types, And Functions
Encapsulation constants are autodetect, VC-mux, and LLC. `struct atm_backend_ppp` is passed to `ATM_SETBACKEND` with `backend_num` set to `ATM_BACKEND_PPP` and `encaps` set to one of the exported values.

## Control Flow
Userspace opens/configures an ATM VC, then sets the PPP backend using `ATM_SETBACKEND`. PPP frames are then carried over the selected ATM encapsulation.

## State And Persistence
State is the VC backend binding and encapsulation mode. It persists for the lifetime of the VC.

## Dependencies And Integration Points
Depends on `atm.h`. Integrates with PPP, pppd plugins, ATM VCs, and RFC2364 networking.

## Risks And Edge Cases
Autodetect may fail with ambiguous traffic, encapsulation must match peer configuration, and backend selection must happen at the correct VC lifecycle point.

## Test Signals
PPP session establishment over VC and LLC modes, autodetect behavior, invalid encapsulation rejection, and backend teardown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h -->
