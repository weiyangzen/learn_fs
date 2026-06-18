# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_generic.c

## Purpose
`mpc512x_generic.c` registers a generic MPC512x machine for boards that can rely on shared SoC support with no board-specific setup.

## Important APIs, Types, and Functions
`mpc512x_generic_probe()` performs early common initialization and returns true only for `"fsl,mpc5121"`, `"fsl,mpc5123"`, or `"fsl,mpc5125"` machines that are not `"fsl,mpc5121ads"` or `"ifm,ac14xx"`. The `define_machine(mpc512x_generic)` hooks shared setup, init, IRQ, `ipic_get_irq`, and restart callbacks.

## Control Flow, State, and Persistence
No file-local state is persisted. The probe-time exclusion list prevents a generic machine from stealing boards with custom setup requirements.

## Dependencies and Integration Points
It integrates OF machine compatible matching, shared MPC512x initialization, IPIC interrupt handling, and the common clock/device population path.

## Risks and Test Signals
Risks include generic matching a board that actually needs board-specific GPIO, CPLD, or power setup, and omission of future custom boards from the exclusion list. Test signals are successful generic DT boots, no duplicate machine match for ADS/PDM360NG, device population, and restart behavior.
