# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ppc-of.c

## Purpose

`ohci-ppc-of.c` is Open Firmware platform glue for PowerPC OHCI controllers. It supports little-endian and big-endian compatible strings, maps OF resources, and registers an OHCI HCD using core callbacks.

## Important APIs, Types, and Functions

Important functions are `ohci_ppc_of_start()`, `ohci_hcd_ppc_of_probe()`, and `ohci_hcd_ppc_of_remove()`. The file defines a dedicated `ohci_ppc_of_hc_driver`, OF match table, and `ohci_hcd_ppc_of_driver`.

## Control Flow

Probe rejects disabled USB, detects big-endian compatibles, translates the first OF address resource, creates an HCD, maps MMIO with `devm_ioremap_resource()`, maps the first OF IRQ, sets big-endian MMIO/descriptor flags and MPC5200 frame-number quirk when needed, initializes core state, and calls `usb_add_hcd()`. Start calls `ohci_init()` and `ohci_run()` directly. Remove unregisters the HCD, disposes the IRQ mapping, and releases the HCD. There is also an IBM 440EPx EHCI-related workaround path on failed add.

## State and Persistence Behavior

Runtime state is the HCD, mapped OF IRQ, resource mapping, and OHCI endian quirk flags. Hardware state is reset and initialized by the shared OHCI core. No persistent state exists.

## Dependencies and Integration Points

It depends on OF address/IRQ APIs, PowerPC endian Kconfig choices, platform bus registration from `ohci-hcd.c`, and generic OHCI core internals because it is included by the main module when configured.

## Risks and Test Signals

Risks include wrong compatible endianness, missing Kconfig endian selection, IRQ mapping leaks on errors, the unusual 440EPx fallback path, and direct use of core internals instead of `ohci_init_driver()`. Test signals include PPC OF probe for `ohci-be`, `ohci-bigendian`, and `ohci-le`, MPC5200 frame number behavior, IRQ disposal on remove, and enumeration on big-endian descriptor systems.
