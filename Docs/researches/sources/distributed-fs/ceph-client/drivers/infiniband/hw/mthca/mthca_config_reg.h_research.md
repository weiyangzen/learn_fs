# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_config_reg.h

## Purpose
`mthca_config_reg.h` centralizes PCI BAR0 register offsets and sizes used for command, event, interrupt-clear, and EQ consumer-index MMIO mappings.

## Important APIs, types, and functions
It defines `MTHCA_HCR_BASE/SIZE`, `MTHCA_ECR_BASE/SIZE`, `MTHCA_ECR_CLR_BASE/SIZE`, `MTHCA_MAP_ECR_SIZE`, `MTHCA_CLR_INT_BASE/SIZE`, and `MTHCA_EQ_SET_CI_SIZE`.

## Control flow
`mthca_cmd.c` maps the HCR using the HCR constants. `mthca_eq.c` maps interrupt clear, Tavor ECR/ECR clear, and Arbel EQ set-CI regions using these constants or firmware-provided bases masked into BAR0.

## State and persistence
No runtime state is stored. These constants represent persistent hardware register layout expectations.

## Dependencies and integration points
The header is included by command, EQ, and main code and depends only on the hardware programming model.

## Risks
Incorrect offsets or sizes cause MMIO writes to the wrong device register, which can hang command submission or interrupt handling. The fixed sizes assume supported HCA generations keep these register windows compatible.

## Test signals
Probe Tavor and Arbel devices, verify HCR command posting, legacy interrupt clear/ECR handling, Arbel EQ set-CI writes, and ioremap failure paths for each mapped range.
