# sources/distributed-fs/ceph-client/drivers/thermal/qcom/lmh.c

Purpose: Qualcomm Limits Management Hardware initialization and IRQ bridge driver. It programs secure firmware LMh thermal/current/reliability/BCL thresholds and exposes a child IRQ domain so cpufreq can handle LMh mitigation interrupts.

Important APIs/types/functions: `struct lmh_hw_data` stores MMIO base, parent IRQ, and IRQ domain. `lmh_handle_irq()` maps hardware event 0 into the child IRQ and calls `generic_handle_irq()`. `lmh_enable_interrupt()` clears DCVS interrupt status and enables the parent IRQ; `lmh_disable_interrupt()` disables it. `lmh_irq_map()` installs the simple IRQ chip and lockdep class. `lmh_probe()` validates SCM availability, maps MMIO, resolves the associated CPU phandle, reads three threshold properties, maps CPU IDs to LMh cluster node IDs, optionally enables LMh algorithms for SDM845, programs thresholds through `qcom_scm_lmh_dcvsh()`, creates a one-cell IRQ domain, and requests the parent IRQ with no auto-enable.

Control flow: firmware programming happens before IRQ setup. The parent IRQ remains disabled until a consumer enables the mapped child IRQ. On interrupt, the handler forwards to the child domain rather than doing thermal policy locally.

State/persistence: thresholds and algorithm enablement persist in LMh firmware/hardware; driver state is MMIO/IRQ-domain handles. Dependencies: QCOM SCM, OF CPU phandle and properties, IRQ domains, platform MMIO/IRQ. Compatibles include `qcom,sc8180x-lmh`, `qcom,sdm845-lmh`, and `qcom,sm8150-lmh`.

Risks: CPU ID to cluster mapping is hard-coded to 0 and 4; failures after `irq_domain_create_linear()` require cleanup only on request-IRQ failure; SCM availability causes probe deferral or failure depending on call. Test signals include missing threshold properties, CPU phandle mapping, SCM error propagation, child IRQ enable/disable, parent IRQ forwarding, and SDM845 algorithm enable path.
