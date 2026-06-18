# sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.h

## Purpose
Private command definitions and internal APIs for NetLabel unlabeled traffic handling.

## Important APIs, Types, And Functions
Defines commands for accept/list and static label add/remove/list operations, including default-interface variants. Defines attributes for accept flag, IPv4/IPv6 addresses and masks, interface name, and LSM security context. Declares hash size `NETLBL_UNLHSH_BITSIZE`, initialization, static add/remove, receive getattr, and default configuration functions.

## Control Flow
The comments specify netlink payload requirements: static mutations need address/mask pairs and usually an interface, default variants omit the interface, and accept toggles require a boolean flag. The receive API is designed to return secattrs for unlabeled packets or permit unlabeled traffic according to policy.

## State And Persistence Behavior
No state is stored in the header, but declarations correspond to persistent hash entries keyed by interface/address and to a global accept flag maintained in the C file.

## Dependencies And Integration Points
Includes `net/netlabel.h`. Used by KAPI configuration wrappers, global NetLabel initialization, netlink setup, and receive fallback.

## Risks And Test Signals
Risks include ABI drift, attribute naming mismatch (`NLA_NULL_STRING` in comments vs implementation policy), and callers passing incorrect address lengths. Test signals include netlink policy/enum alignment, IPv6-disabled builds, and add/remove/getattr integration coverage.
