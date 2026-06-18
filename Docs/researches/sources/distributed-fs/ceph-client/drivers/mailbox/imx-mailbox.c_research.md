<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c

## Purpose
`imx-mailbox.c` implements NXP i.MX Message Unit mailbox controllers across several SoC generations and firmware protocols. It supports generic TX/RX registers, doorbells, reset channels, SCU/S4 multiword RPC, and SECO-style doorbell RPC.

## Important APIs, Types, and Functions
`struct imx_mu_priv` holds MMIO base, controller, channels, config, clock, IRQs, saved control registers, TR/RR counts, and PM state. `struct imx_mu_con_priv` describes each channel's index/type and deferred TX doorbell work. SoC-specific `struct imx_mu_dcfg` instances provide register offsets, type flags, and tx/rx/init callbacks. Key functions include generic/specific/SECO TX/RX helpers, `imx_mu_isr()`, `imx_mu_startup()`, `imx_mu_shutdown()`, xlate variants, init variants, PM callbacks, and `imx_mu_probe()`.

## Control Flow
Probe maps registers, selects match data, obtains shared or named TX/RX IRQs, allocates a maximum RPC receive buffer, enables the optional clock, discovers TR/RR counts, detects side B, initializes channels through the selected config, registers the mailbox controller, populates child devices, enables runtime PM, performs an initial resume/put cycle, then disables the clock until clients start. Startup resumes runtime PM, initializes doorbell work or requests an IRQ, and enables RX/RXDB interrupt bits. Send dispatches to config TX callbacks: generic single-word TX writes TR and enables TX interrupt; doorbells set GIR bits; specific SCU/S4 TX streams a bounded RPC message through available TR registers; SECO TX sends header, signals, and waits for remote reads. The ISR filters status by enabled bits and channel type, then completes TX or calls RX/RXDB callbacks.

## State and Persistence
Runtime PM gates the clock around active channels. `xcr_lock` protects control-register RMW operations. `priv->msg` is a reusable receive buffer for specific protocols. Suspend-noirq optionally saves control registers when no clock provider exists and restores only if context appears lost. `suspend` flags wakeup behavior for interrupts during system sleep.

## Dependencies and Integration Points
The driver integrates with firmware headers `linux/firmware/imx/ipc.h` and `s4.h`, platform IRQ/MMIO/clock/runtime PM, OF child population, mailbox core, and compatibles for `fsl,imx6sx-mu`, `imx7ulp`, `imx8ulp`, `imx8ulp-mu-s4`, `imx93-mu-s4`, `imx95` variants, `imx8-mu-scu`, and `imx8-mu-seco`.

## Risks and Edge Cases
This is a high-variance driver: channel numbering and IRQ semantics differ by SoC type. Message size fields are validated, but clients must supply the correct RPC struct. Some TXDB paths synthesize completion through work because hardware lacks ACK support. The source contains a duplicated line in `imx_mu_seco_tx()` that compile testing should catch. Runtime PM error paths and IRQ request failures must not leak clocks or active PM references.

## Test Signals
Test each compatible configuration, generic and specific xlate validation, single-word TX/RX, TXDB and RXDB, SCU/S4/SECO max-size rejection, timeout paths for full/empty TR/RR, runtime PM clock balancing, suspend/resume register save/restore, named IRQ mode, and side-B initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c -->
