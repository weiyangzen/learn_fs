# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc834x_itx.c

## Purpose
`mpc834x_itx.c` registers the Freescale MPC834x ITX board and adds localbus platform-device probing.

## Important APIs, Types, and Functions
`mpc834x_itx_declare_of_platform_devices()` runs common 83xx platform population and probes `"fsl,pq2pro-localbus"`. `mpc834x_itx_setup_arch()` calls common setup and `mpc834x_usb_cfg()`. The machine uses compatible `"MPC834xMITX"` and shared PCI, IPIC, restart, and time hooks.

## Control Flow, State, and Persistence
No file-local runtime state is retained. Localbus devices are registered by OF probing; USB mux/clock state is written to IMMR.

## Dependencies and Integration Points
It depends on common 83xx setup, OF platform bus, FSL PCI, IPIC, and the MPC834x USB helper.

## Risks and Test Signals
Risks include bootloader responsibility for PCI initialization, localbus DT compatibility, and USB port conflict handling. Test signals are localbus child probing, USB DR/MPH behavior, PCI presence, and interrupts.
