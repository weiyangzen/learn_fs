# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_hw_regs.h

## Purpose

`mtu3_hw_regs.h` defines MTU3 SSUSB device, endpoint, USB2, USB3, QMU, and IPPC register offsets and bit fields. It is the hardware contract used by the platform, core, gadget, EP0, host, dual-role, QMU, and debugfs code.

## Important APIs, Types, and Functions

The file provides base offsets such as `SSUSB_DEV_BASE`, `SSUSB_EPCTL_CSR_BASE`, `SSUSB_USB3_MAC_CSR_BASE`, `SSUSB_USB2_CSR_BASE`, and `SSUSB_SIFSLV_IPPC_BASE`; register offsets such as `U3D_EP0CSR`, `U3D_DEVICE_CONF`, `U3D_POWER_MANAGEMENT`, and `U3D_SSUSB_IP_PW_CTRL*`; and field macros for interrupts, endpoint CSR fields, QMU status, speed, link power, test modes, port power/mode, and clock/reset status.

## Control Flow

There is no executable control flow. Callers compose these macros with `mtu3_readl()`, `mtu3_writel()`, `mtu3_setbits()`, and `mtu3_clrbits()` to control hardware.

## State and Persistence Behavior

The header defines access constants only. State lives in hardware registers and driver structures. Some fields are write-one-to-clear, captured by masks such as `EP0_W1C_BITS`, `TX_W1C_BITS`, and `RX_W1C_BITS`.

## Dependencies and Integration Points

It depends on kernel bit macro definitions through users including common Linux headers. It is included by `mtu3.h`, making it transitively available to all MTU3 implementation files and debugfs regsets.

## Risks and Test Signals

Risks include incorrect bit definitions causing destructive MMIO writes, Gen2 versus original TX/RX max-packet field differences, W1C mask misuse, and port-mode bits being used inconsistently between host, gadget, and DRD paths. Test signals include register dump comparison with vendor documentation, endpoint CSR programming for IN/OUT endpoints, QMU interrupt enable/clear behavior, speed detection from `U3D_DEVICE_CONF`, and IP clock/reset polling against `U3D_SSUSB_IP_PW_STS*`.
