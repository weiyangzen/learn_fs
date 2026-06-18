# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-port.h

## Purpose
Defines xHCI port register bit fields and helper macros used by hub, port, ring, and PM code to interpret and update PORTSC, PORTPMSC, PORTLI, and related port-management registers.

## Important APIs, Types, And Functions
Important masks and values include `PORT_CONNECT`, `PORT_PE`, `PORT_RESET`, `PORT_PLS_MASK`, link states `XDEV_U0` through `XDEV_RESUME`, speed helpers `DEV_FULLSPEED()`, `DEV_SUPERSPEED_ANY()`, `DEV_PORT_SPEED()`, slot speed encodings, change bits in `PORT_CHANGE_MASK`, wake bits, `PORT_WR`, `PORT_U1_TIMEOUT()`, `PORT_U2_TIMEOUT()`, USB2 L1 fields, USB3 lane/link information helpers, default `XHCI_L1_TIMEOUT`, `XHCI_DEFAULT_BESL`, and `XHCI_PORT_POLLING_LFPS_TIME`.

## Control Flow
The header has no execution. Its macros are used by code that handles port status events, root-hub control requests, suspend/resume, warm reset, LPM programming, wake setup, and port polling. Correct neutralizing and write-one-to-clear behavior is enforced in callers using these definitions.

## State And Persistence
No state is allocated here. The macros describe volatile hardware state in xHCI port registers and derived software state such as root-hub status, link state, speed, and wake policy.

## Dependencies And Integration Points
Included by xHCI core files through private headers. It integrates with USB hub semantics, USB2/USB3 link power management, root-hub emulation, and event handling in `xhci-ring.c` and hub code.

## Risks And Test Signals
Risks include incorrect bit definitions corrupting port control writes, speed misclassification, mishandled write-one-to-clear change bits, and LPM fields violating device latency constraints. Test signals include connect/disconnect, reset/warm reset, over-current, remote wake, U1/U2/U3 transitions, USB2 L1 suspend/resume, SuperSpeedPlus speed reporting, and root-hub `GetPortStatus`/`SetPortFeature` tests.
