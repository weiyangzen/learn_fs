# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3.h

## Purpose

`mtu3.h` is the central internal header for the MediaTek MTU3 USB3 dual-role controller. It defines register access helpers, endpoint/request/controller state, QMU descriptor layout, FIFO management, OTG switch state, and prototypes shared by platform, host, gadget, EP0, QMU, debug, and DRD code.

## Important APIs, Types, and Functions

Key types are `struct ssusb_mtk` for the whole SSUSB controller, `struct mtu3` for the gadget/device controller, `struct mtu3_ep` for endpoint state, `struct mtu3_request` for wrapped gadget requests, `struct qmu_gpd` and `struct mtu3_gpd_ring` for Queue Management Unit descriptors, `struct mtu3_fifo_info` for FIFO bitmap allocation, and `struct otg_switch_mtk` for role switching. Inline helpers map from gadget or endpoint objects and wrap MMIO read/write/set/clear. Prototypes cover gadget setup, endpoint configuration, QMU-facing request completion, start/stop, and EP0 ISR handling.

## Control Flow

The header itself has no execution path, but its structures define the runtime flow: platform probe creates `ssusb_mtk`, gadget init creates `mtu3`, endpoints queue `mtu3_request` objects into QMU rings, interrupts dispatch through core and EP0 code, and dual-role code switches host/device state through `otg_switch_mtk`.

## State and Persistence Behavior

All state is runtime memory and MMIO-backed hardware state. Persistent-like flags include role, speed, endpoint flags, softconnect, wakeup ability, U1/U2 enable state, delayed status, hardware version, and FIFO bitmaps, but none survive device removal.

## Dependencies and Integration Points

The header depends on Linux clocks, devices, DMA pools, extcon, PHY, regulator, USB gadget, USB role switch, and local `mtu3_hw_regs.h` and `mtu3_qmu.h`. It is the main compile-time integration point for all MTU3 implementation files.

## Risks and Test Signals

Risks include structure field coupling across many files, register helper misuse without locking, mismatched QMU descriptor bit layout for Gen2-compatible hardware, and endpoint array indexing assumptions. Test signals are full compile coverage of host/gadget/dual-role configs, endpoint enable/disable on every endpoint number, QMU transfer completion, EP0 standard request handling, and suspend/resume using the same shared state.
