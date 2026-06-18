# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.c

## Purpose
This file implements CN23XX Physical Function hardware setup for the LiquidIO core. It maps BARs, discovers PF/PCIe port identity, configures SR-IOV ring ownership, programs global input/output queue registers, manages PF/VF mailboxes, handles PF interrupts, exposes BAR1 index operations, and registers a CN23XX PF function table into `struct octeon_device`.

## Important APIs, Types, And Functions
External APIs are `setup_cn23xx_octeon_pf_device()`, `cn23xx_sriov_config()`, `cn23xx_pf_get_oq_ticks()`, `cn23xx_fw_loaded()`, `cn23xx_tell_vf_its_macaddr_changed()`, and `cn23xx_get_vf_stats()`. Key internal routines are `cn23xx_pf_soft_reset()`, `cn23xx_setup_global_mac_regs()`, `cn23xx_reset_io_queues()`, `cn23xx_pf_setup_global_input_regs()`, `cn23xx_pf_setup_global_output_regs()`, `cn23xx_setup_iq_regs()`, `cn23xx_setup_oq_regs()`, mailbox setup/free/thread helpers, interrupt handlers, and BAR1 helpers.

## Control Flow
`setup_cn23xx_octeon_pf_device()` validates BAR0/BAR1 assignment, maps both BARs, determines PF number from SR-IOV config or a firmware-populated fallback, computes SR-IOV ring layout, writes MAC credit count, fills `oct->fn_list`, installs register-address pointers, and stores the coprocessor clock rate. Device register setup enables PCIe error reporting, programs MAC-to-ring mapping, resets and configures PF-owned queues, configures output queues and backpressure, sets window timeout, and raises packet input jabber for VXLAN TSO. IQ/OQ setup writes descriptor base addresses, sizes, doorbell/count register pointers, and interrupt thresholds. Interrupt handling reads the PF interrupt summary, logs errors, dispatches VF mailbox interrupts, sets generic LiquidIO interrupt-status bits, and clears the summary. Mailbox paths allocate one mailbox per VF ring group, use delayed work for processing, poll on pre-1.1 revisions, and send PF-to-VF notifications or synchronous VF stats requests.

## State And Persistence
State is stored in `oct->chip` as `struct octeon_cn23xx_pf`, `oct->sriov_info`, `oct->fn_list`, `oct->mbox[]`, `oct->io_qmask`, queue structures, MMIO register pointers, and hardware CSR state. The driver persists no files. Firmware readiness is read from `CN23XX_SLI_SCRATCH2` unless multiple PF references imply firmware is already active.

## Dependencies And Integration Points
This file depends on LiquidIO core types (`octeon_device`, IQ/DROQ, mailbox, config), PCI config access, BAR mapping helpers, MMIO CSR helpers, SR-IOV configuration, versioned CN23XX register definitions, and kernel delayed work/vmalloc. Its function table is consumed by the generic LiquidIO core after chip detection.

## Risks
Ring reset polling uses bounded loops and can fail if QUIET/RST transitions do not match hardware expectations. SR-IOV ring partitioning assumes one ring per VF and CPU-count-based PF rings unless overridden. Mailbox allocation cleanup indexes `oct->mbox[i]` rather than the `q_no` used during allocation, which is worth reviewing when `rings_per_vf` is not one. `cn23xx_get_vf_stats()` waits up to one second and cancels mailbox queue `0` on timeout, which may affect unrelated outstanding mailbox work. `cn23xx_fw_loaded()` can intentionally return true from adapter refcount even before scratch status is set. Interrupt masks and mailbox behavior vary by revision.

## Test Signals
Test PF probe on CN23XX revisions 1.0, 1.1, and later; BAR mapping failure cleanup; SR-IOV enabled/disabled builds; PF/VF mailbox handshake, MAC-change notification, VF stats requests and timeout; MSI-X and non-MSI-X interrupt paths; queue enable/disable/reset; VXLAN TSO larger than default jabber; firmware-loaded race during multi-PF initialization.
