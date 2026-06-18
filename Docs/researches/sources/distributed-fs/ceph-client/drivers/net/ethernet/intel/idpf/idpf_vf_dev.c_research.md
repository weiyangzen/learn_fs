# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_vf_dev.c

## Purpose

`idpf_vf_dev.c` installs the virtual-function-specific device operations for the IDPF driver. It maps VF mailbox, interrupt, reset, and IDC behavior into the generic `adapter->dev_ops` callback table used by the rest of the driver. Unlike the datapath file, this file does not allocate packet queues or process traffic; it tells shared IDPF code how to find VF hardware registers and how to trigger VF reset/control-plane behavior.

## Important APIs and functions

The exported entry point is `idpf_vf_dev_ops_init(struct idpf_adapter *adapter)`. It calls `idpf_vf_reg_ops_init()`, assigns IDC initialization, and records static VF register resource ranges.

Register callback helpers are `idpf_vf_ctlq_reg_init()`, `idpf_vf_mb_intr_reg_init()`, `idpf_vf_intr_reg_init()`, `idpf_vf_reset_reg_init()`, and `idpf_vf_trigger_reset()`. `idpf_idc_vf_register()` wraps IDC auxiliary-device registration for VF mode.

`idpf_vf_ctlq_reg_init()` fills mailbox TX/RX control queue register offsets and masks for `IDPF_CTLQ_TYPE_MAILBOX_TX` and `IDPF_CTLQ_TYPE_MAILBOX_RX`. `idpf_vf_mb_intr_reg_init()` initializes the mailbox interrupt register set from negotiated `adapter->caps.mailbox_dyn_ctl` plus VF interrupt cause masks. `idpf_vf_intr_reg_init()` maps per-vport queue-vector dynamic control and ITR registers using vector register data returned by `idpf_get_reg_intr_vecs()`. `idpf_vf_reset_reg_init()` maps the VF reset status register. `idpf_vf_trigger_reset()` sends `VIRTCHNL2_OP_RESET_VF` for function resets except during driver removal.

## Control flow

During device selection, `idpf_main.c` calls `idpf_vf_dev_ops_init()` for VF devices. That function installs VF register ops into `adapter->dev_ops.reg_ops`, installs `adapter->dev_ops.idc_init`, and sets `adapter->dev_ops.static_reg_info[0]` to the VF mailbox register window and `[1]` to the VF reset-status register window.

Later, shared control queue setup calls the installed `ctlq_reg_init` callback. The VF callback subtracts the mailbox resource start from absolute VF register constants so the control queue code can use resource-relative offsets. It fills head, tail, length, base-address high/low, enable, length, and head masks for the admin transmit and receive queues.

Mailbox interrupt setup calls `mb_intr_reg_init`, which uses the mailbox dynamic control value from capabilities and maps the VF admin-queue interrupt enable register. Vport interrupt setup calls `intr_reg_init`, which allocates temporary `idpf_vec_regs`, asks shared code for interrupt vector register offsets, validates enough registers exist for the requested queue vectors, and fills each `idpf_q_vector::intr_reg` with dynamic-control fields plus RX/TX ITR register addresses. It also configures the no-IRQ data vector used for queues that rely on writeback without normal interrupts.

Reset setup calls `reset_reg_init`, which records the VF reset status register and mask. Reset execution calls `trigger_reset`; for host-requested function reset it sends a virtchnl2 reset message unless removal is already in progress, avoiding unnecessary mailbox traffic during unload.

IDC registration calls `idpf_idc_vf_register()`, which delegates to `idpf_idc_init_aux_core_dev(adapter, IIDC_FUNCTION_TYPE_VF)` so auxiliary consumers see a VF function type.

## State and persistence behavior

This file persists VF behavior by assigning function pointers and resource ranges in `adapter->dev_ops`. The register addresses written into `adapter->mb_vector.intr_reg`, `adapter->reset_reg`, and each `idpf_q_vector::intr_reg` remain valid for the lifetime of the current hardware mapping and are consumed by shared queue, mailbox, interrupt, and reset paths.

`idpf_vf_intr_reg_init()` uses temporary heap state only for `reg_vals`; it frees it before returning. The no-IRQ dynamic-control address and enable value are stored in `struct idpf_q_vec_rsrc` so shared interrupt enable/disable code can write them later.

Reset behavior is state-sensitive: `idpf_vf_trigger_reset()` checks `IDPF_REMOVE_IN_PROG` and suppresses the reset mailbox message during unload. It does not set reset flags itself; it is a callback invoked after shared reset logic has selected a trigger cause.

## Dependencies and integration points

The file depends on `idpf.h` for adapter/vport/dev-ops structures, `idpf_lan_vf_regs.h` for VF register constants and masks, and `idpf_virtchnl.h` for virtchnl2 messaging. It integrates with shared control queue initialization, mailbox interrupt handling, vport interrupt initialization in `idpf_txrx.c`, reset handling, IDC auxiliary-device setup, and device selection in `idpf_main.c`.

`idpf_vf_intr_reg_init()` depends on shared vector helpers such as `idpf_get_reserved_vecs()`, `idpf_get_reg_intr_vecs()`, `idpf_get_reg_addr()`, and `IDPF_ITR_IDX_SPACING()`. The ITR spacing fallback is VF-specific (`IDPF_VF_ITR_IDX_SPACING`), but it uses the shared spacing macro from `idpf_txrx.h`.

## Risks and correctness considerations

Register offset mistakes are high impact. The control queue setup subtracts `static_reg_info[0].start` from mailbox registers, so incorrect resource ranges or register constants will misprogram admin queues. Interrupt register setup indexes `reg_vals` by `rsrc->q_vector_idxs[i] - IDPF_MBX_Q_VEC`; off-by-one errors around the mailbox vector or no-IRQ vector can bind queues to the wrong MSI-X register or write the wrong dynamic-control register.

`idpf_vf_intr_reg_init()` validates `num_regs < num_vecs`, but it later reads the no-IRQ vector using the loop index after processing all queue vectors. Correct operation therefore relies on `idpf_get_reserved_vecs()` and the allocated register data covering the extra reserved no-IRQ vector as well as normal data vectors.

Reset triggering must preserve unload behavior. Sending `VIRTCHNL2_OP_RESET_VF` during removal can race with mailbox teardown, while failing to send it for real host-requested resets can leave the VF wedged until a broader reset.

Because this file installs callbacks into shared ops tables, missing one callback can fail much later in generic code. VF probe coverage needs to exercise mailbox, reset, queue interrupt setup, and IDC init rather than just checking that `idpf_vf_dev_ops_init()` returns.

## Test signals

Useful validation includes VF probe and remove, mailbox control queue bring-up, mailbox interrupt delivery, vport queue interrupt allocation with multiple vector counts, no-IRQ vector programming, queue traffic under dynamic ITR, host-requested VF reset, unload while reset paths are possible, IDC auxiliary registration, and negative tests where vector register enumeration returns too few entries. Register-level tests should verify that mailbox TX/RX head/tail/length/base offsets are relative to `VF_BASE`, that reset status uses `VFGEN_RSTAT`, and that RX/TX ITR addresses honor either hardware-provided spacing or the VF fallback spacing.
