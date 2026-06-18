# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/asp834x.c

## Purpose
`asp834x.c` registers the Analogue & Micro ASP8347E board, derived from MPC834x ITX setup.

## Important APIs, Types, and Functions
`asp834x_setup_arch()` calls common `mpc83xx_setup_arch()` and configures MPC834x USB with `mpc834x_usb_cfg()`. The machine definition uses compatible `"analogue-and-micro,asp8347e"` and shared PCI, IPIC, restart, time, and progress hooks.

## Control Flow, State, and Persistence
The file persists no local state. Board setup mutates IMMR USB mux/clock registers through the USB helper.

## Dependencies and Integration Points
It depends on common 83xx setup, FSL PCI, IPIC, UDBG progress, and OF platform device declaration via `machine_device_initcall`.

## Risks and Test Signals
Risks are limited to USB mux assumptions and generic 83xx behavior. Test signals are board-compatible matching, USB controller mode, PCI bridge discovery, IPIC interrupts, and restart.
