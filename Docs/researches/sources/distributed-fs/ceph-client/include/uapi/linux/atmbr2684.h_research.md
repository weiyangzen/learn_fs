<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h

## Purpose
Defines the RFC 1483/2684 ATM bridging/routing backend ABI for creating virtual network interfaces and attaching ATM VCs.

## Important APIs, Types, And Functions
Exports media, routed, FCS, encapsulation, and payload constants. `struct atm_newif_br2684` creates backend interfaces. `struct br2684_if_spec` selects an interface by number/name. `struct atm_backend_br2684` attaches a VC with FCS/encapsulation/padding options. `struct br2684_filter_set` and `BR2684_SETFILT` manage an experimental IP filter.

## Control Flow
Userspace creates a BR2684 backend netdevice with `ATM_NEWBACKENDIF`, then uses `ATM_SETBACKEND` on an ATM VC to attach it to an interface. Optional filter ioctls constrain routed IP traffic.

## State And Persistence
State includes created netdevices, VC-to-interface attachments, encapsulation/payload/FCS settings, and optional filters. It lasts until interface/VC teardown.

## Dependencies And Integration Points
Depends on ATM core types and `IFNAMSIZ`. Integrates with Ethernet-like netdevices over ATM, PPP/CLIP alternatives, and legacy DSL/ATM tools.

## Risks And Edge Cases
Many constants are marked unsupported, interface lookup by name/number can race with netdevice lifecycle, and experimental filters may not compose with netfilter.

## Test Signals
Interface creation, VC attach/detach, LLC vs VC-mux encapsulation, routed vs bridged payload, filter set/disable, and invalid media/FCS options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h -->
