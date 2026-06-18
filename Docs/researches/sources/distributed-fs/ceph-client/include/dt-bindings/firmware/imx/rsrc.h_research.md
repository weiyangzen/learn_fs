# sources/distributed-fs/ceph-client/include/dt-bindings/firmware/imx/rsrc.h

## Purpose
Defines NXP i.MX System Controller resource and control IDs for firmware-mediated DT bindings. The file explicitly states that resource list items should never be changed or removed and only added at the end, making it a strict firmware/DT ABI.

## Important APIs, Types, and Constants
The main namespace is `IMX_SC_R_*`, covering application processors, display controllers, V2X, DMA channels, UART/SPI/I2C, ADC, FTM, CAN, GPU partitions, PCIe, SATA, SERDES, LCD, PWM, GPIO, MU, OCRAM, audio, MIPI, CSI, HDMI, VPU, DC resources, pads, and board resources. `IMX_SC_R_CAN(x)` is a function-like convenience macro over `IMX_SC_R_CAN_0`. The later `IMX_SC_C_*` constants define control IDs such as clock, reset, power, timing, link, PHY, MISC, and `IMX_SC_C_LAST`.

## Control Flow and State
No runtime flow exists in the header. Resource ownership, power state, clocks, resets, and controls are persisted or enforced by the i.MX system controller firmware; the kernel passes these IDs across firmware calls.

## Dependencies and Integration Points
Self-contained binding used by i.MX DT nodes and firmware clients that communicate with SCU/SCFW services. It integrates with power-domain, clock, reset, pin, and resource-management drivers.

## Risks and Test Signals
Risk is very high because values cross firmware and partition boundaries. Removing, reordering, or reusing IDs can break power/resource ownership or secure partitioning. Test signals include DT compilation, firmware API compatibility checks, boot on SCFW-based i.MX platforms, and runtime tests for resource allocation, power domains, clocks, resets, and peripheral access.
