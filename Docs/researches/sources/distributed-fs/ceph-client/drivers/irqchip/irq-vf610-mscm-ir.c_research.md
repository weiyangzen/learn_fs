# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vf610-mscm-ir.c

## Purpose
Implements the Freescale/NXP VF610 MSCM interrupt router hierarchy. It routes peripheral interrupts to the CPU running Linux, supports GIC and NVIC parents, and saves router state around CPU cluster power transitions.

## Important APIs, Types, And Functions
`struct vf610_mscm_ir_chip_data` stores MMIO base, CPU routing mask, saved IRSPRC registers, and whether the parent is NVIC. Chip callbacks wrap parent operations and program `MSCM_IRSPRC()` on enable/disable. Domain callbacks translate two-cell specifiers and allocate GIC or NVIC parent fwspecs.

## Control Flow
OF init finds the parent domain, maps MSCM IR registers, reads the current CPU number from the `fsl,cpucfg` syscon, creates a hierarchy domain for 112 lines, detects NVIC parent compatibility, and registers a CPU PM notifier. Enabling a child IRQ writes the local CPU mask into its route register before enabling the parent; disabling clears it.

## State And Persistence
Global singleton `mscm_ir_data` holds routing state. CPU cluster PM enter saves all 112 route registers; failed enter or exit restores them. Runtime route state is entirely hardware-backed per interrupt.

## Dependencies And Integration Points
Depends on OF address, syscon/regmap, CPU PM notifier, GIC binding constants, hierarchy domains, and compatible `fsl,vf610-mscm-ir`.

## Risks
CPU mask comes from hardware CPU ID and must match Linux's running core. Route registers are 16-bit and only low two bits are valid. Parent fwspec formatting diverges for NVIC versus GIC. PM notifier is global and assumes one controller.

## Test Signals
Validate single-core and dual-core VF610 configurations, interrupt delivery after enable, route clearing after disable, GIC and NVIC parent paths, and CPU cluster suspend/resume preserving IRSPRC state.
