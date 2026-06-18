# sources/distributed-fs/ceph-client/drivers/mailbox/zynqmp-ipi-mailbox.c

## Purpose
`zynqmp-ipi-mailbox.c` implements the Xilinx ZynqMP and Versal Inter-Processor Interrupt mailbox controller. It exposes per-remote-agent TX/RX mailbox channels backed by IPI firmware calls and optional shared memory message buffers.

## Important APIs, Types, and Functions
Key types are `zynqmp_ipi_pdata`, `zynqmp_ipi_mbox`, and `zynqmp_ipi_mchan`. Important routines include `zynqmp_ipi_fw_call()`, `zynqmp_ipi_interrupt()`, `zynqmp_sgi_interrupt()`, `zynqmp_ipi_peek_data()`, `zynqmp_ipi_last_tx_done()`, `zynqmp_ipi_send_data()`, `zynqmp_ipi_startup()`, `zynqmp_ipi_shutdown()`, `zynqmp_ipi_mbox_probe()`, `zynqmp_ipi_setup()`, `versal_ipi_setup()`, `xlnx_mbox_init_sgi()`, `zynqmp_ipi_probe()`, and `zynqmp_ipi_free_mboxes()`.

## Control Flow, State, and Persistence
Top-level probe reads the local IPI ID, allocates private data for child mailbox nodes, registers one child device/controller per remote ID, then configures either an SPI/shared IRQ or per-CPU SGI path. Channel startup opens the firmware mailbox once per TX/RX pair and enables notification IRQs for RX. TX copies request data into the request buffer, then invokes `SMC_IPI_MAILBOX_NOTIFY`; RX responses use `SMC_IPI_MAILBOX_ACK` after optional response-buffer writes. Interrupt handling polls firmware status per remote mailbox, copies pending request data from IO memory into the preallocated `zynqmp_ipi_message`, and delivers it to the mailbox core. State includes per-channel `is_opened`, buffer mappings/sizes, remote/local IDs, SGI mappings, and firmware call method. The driver persists no data itself; correctness depends on firmware-visible message buffer contents and IPI status.

## Dependencies and Integration Points
The driver depends on ARM SMCCC SMC/HVC calls, mailbox controller APIs, OF child nodes and `reg-names`, IRQ domains, CPU hotplug, per-CPU IRQs, and `linux/mailbox/zynqmp-ipi-message.h`. It binds `xlnx,zynqmp-ipi-mailbox` and `xlnx,versal-ipi-mailbox`.

## Risks and Test Signals
Risks include incorrect buffer resource pairing, SGI hotplug cleanup using dynamic CPUHP state, status/ack races, missing bounds when buffers are absent, and firmware method mismatches. Tests should cover buffered and bufferless Versal layouts, invalid IPI IDs, TX/RX startup ordering, interrupt delivery through SPI and SGI, CPU hotplug cycles, message length limits, and remove cleanup after partial child registration failure.
