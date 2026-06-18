# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_dev.c

## Purpose
This file provides PF-device-specific operations for IDPF. It initializes mailbox control queue register offsets, mailbox and data interrupt register addresses, reset registers, reset triggering, PTP command masks, IDC registration, and the `idpf_dev_ops` table for PF devices.

## Important APIs, Types, And Functions
The exported entry point is `idpf_dev_ops_init()`. Internal operations installed into `adapter->dev_ops.reg_ops` are `idpf_ctlq_reg_init()`, `idpf_intr_reg_init()`, `idpf_mb_intr_reg_init()`, `idpf_reset_reg_init()`, `idpf_trigger_reset()`, and `idpf_ptp_reg_init()`. `idpf_idc_register()` installs the PF IDC auxiliary core device callback. Constants include `IDPF_PF_ITR_IDX_SPACING`.

## Control Flow
`idpf_dev_ops_init()` calls `idpf_reg_ops_init()`, sets `adapter->dev_ops.idc_init`, and records static BAR resource ranges for mailbox and reset/status regions. Later, mailbox setup calls `ctlq_reg_init()` to translate PF firmware ATQ/ARQ registers into offsets relative to the mapped mailbox region. Interrupt setup maps mailbox and traffic dynamic control/ITR registers from capability-provided register chunks. Reset setup maps PF reset status, and reset trigger sets `PFGEN_CTRL_PFSWR`.

## State And Persistence
The file populates `adapter->dev_ops`, `adapter->dev_ops.static_reg_info`, `adapter->mb_vector.intr_reg`, per-queue-vector `intr_reg` fields, `rsrc->noirq_dyn_ctl`, `rsrc->noirq_dyn_ctl_ena`, `adapter->reset_reg`, and PTP command masks. This state persists for the lifetime of the adapter and is recalculated during device initialization or reset-related setup.

## Dependencies And Integration Points
It depends on `idpf_lan_pf_regs.h` for PF register constants, `idpf_virtchnl.h` for interrupt vector register discovery, and `idpf_ptp.h` for PTP state. It integrates with `idpf_main.c`, which selects PF or VF device ops based on PCI device id, and with control queue and interrupt setup paths that call the operation table.

## Risks
Register address translation is hardware-specific and sensitive to static region starts. Incorrect offsets can program the wrong BAR location. `idpf_intr_reg_init()` allocates register metadata for all reserved vectors and indexes by queue vector ids minus the mailbox vector; invalid vector indexes can produce bad register mappings. The NOIRQ vector setup reads `i` after the loop, relying on `i == num_vecs`.

## Test Signals
PF probe tests should verify static resource ranges, mailbox ATQ/ARQ register programming, mailbox interrupt enable behavior, data vector ITR addresses, NOIRQ dyn_ctl setup, reset trigger writes, reset status reads, PTP mask initialization, IDC registration, and error handling when available interrupt register chunks are fewer than requested vectors.
