# `sources/distributed-fs/ceph-client/include/linux/usb/pd_vdo.h`

## Purpose

`pd_vdo.h` defines USB PD Vendor Defined Object and Structured VDM helpers. It covers identity headers, certification/stat VDOs, product VDOs, cable VDOs, active cable VDOs, AMA/VPD VDOs, SVID discovery, USB-IF SIDs, modal command encodings, and VDM timing constants.

## Important APIs, Types, and Constants

- VDM header macros encode VID/SID, structured/unstructured type, version, object position, command type, and command.
- Identity helpers build/extract ID headers, product VDOs, cable VDOs, active cable VDOs, alternate-mode adapter VDOs, and VPD VDOs.
- Cable constants describe connector type, latency, termination, VCONN requirements, VBUS voltage/current, USB signaling capability, USB4/USB2/USB3 support, lane count, optical isolation, redriver/retimer state, and operating temperature.
- SVID helpers pack/unpack two SVIDs per VDO and define USB-IF SIDs for PD, DisplayPort, and MHL.
- VDM timeout constants describe expected command response windows.

## Control Flow and Lifetimes

TCPM and alt-mode managers send Discover Identity/SVIDs/Modes/Enter/Exit/Attention VDMs, then parse returned VDOs with these macros to identify partner, cable, and modal capabilities. Cable/partner identity is cached while the Type-C connection remains attached.

## State and Persistence Behavior

VDOs are transient PD payloads, but decoded identity and mode capability state persists in Type-C partner/cable/plug objects for the connection lifetime.

## Dependencies and Integration Points

It integrates PD message handling with the Type-C class, alt-mode drivers such as DisplayPort, cable discovery, VCONN swap policy, and USB4/retimer/redriver decisions.

## Risks and Edge Cases

The same bit positions can mean different things for passive cable, active cable, AMA, and VPD objects, so consumers must select the correct decoder. PD revision and VDO version gate field validity. Identity discovery can happen over SOP or SOP prime, and cable communication may be unsupported. Timeouts are policy-sensitive.

## Test Signals

Test Discover Identity/SVID/Modes flows for partners, passive cables, active cables, VPDs, and AMAs; verify DisplayPort SVID discovery; fuzz VDO versions and reserved bits; check VCONN swap policy; and validate timeout/retry behavior.
