<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c

## Purpose
Uses the Freescale/NXP Messaging Unit as a small MSI parent controller, exposing four receive channels as MSI vectors for platform devices.

## Important APIs, Types, And Functions
`struct imx_mu_dcfg` describes MU register offsets and version-specific bit layouts. `struct imx_mu_msi` stores the register base, MSI write address, used-channel bitmap, lock, clock, and configuration. Important functions include `imx_mu_probe()`, `imx_mu_msi_domains_init()`, `imx_mu_msi_domain_irq_alloc()`, `imx_mu_msi_parent_compose_msg()`, `imx_mu_msi_irq_handler()`, `imx_mu_msi_parent_mask_irq()`, and runtime PM callbacks.

## Control Flow
IRQCHIP platform-driver matching selects one of the i.MX6SX, i.MX7ULP, or i.MX8ULP register layouts. Probe maps processor A registers, computes the processor B transmit register MSI address, attaches two power domains, creates a parent MSI irqdomain, enables runtime PM, and chains the MU receive IRQ. MSI allocation reserves one of four channels, installs the parent chip, and compose-message points writes at `processor-b-side + xTR + 4 * channel`. The handler reads receive status and dispatches each full receive register.

## State And Persistence
`used` tracks allocated channels in memory. Hardware state is receive interrupt enable bits in the MU receive control register and receive data registers consumed for ACK. Runtime suspend disables the clock; runtime resume re-enables it. Power-domain links keep both MU sides active while needed.

## Dependencies And Integration Points
It depends on IRQCHIP platform-driver macros, MSI parent ops, `irq-msi-lib`, clocks, runtime PM, named memory resources `processor-a-side` and `processor-b-side`, and named power domains. Compatibles are `fsl,imx7ulp-mu-msi`, `fsl,imx6sx-mu-msi`, and `fsl,imx8ulp-mu-msi`.

## Risks
Only four MSI vectors exist, so allocation pressure returns `-ENOSPC`. Register bit definitions differ between v1 and v2 MU blocks. The error path around power-domain links returns `-EINVAL` rather than original errors and must not leak attached domains. Affinity is unsupported.

## Test Signals
Test allocation/free of all four vectors, MSI message address/data contents, interrupt delivery and ACK by receive register read, runtime PM clock behavior, power-domain attach failures, all three compatible register layouts, and over-allocation returning `-ENOSPC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-mu-msi.c -->
