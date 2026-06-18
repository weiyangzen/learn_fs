# sources/distributed-fs/ceph-client/include/linux/soc/qcom/irq.h

Purpose: This header defines Qualcomm IRQ-domain flags and helpers for wake-capable interrupt controllers such as PDC and MPM.

Important APIs/types/functions: It defines `GPIO_NO_WAKE_IRQ`, `IRQ_DOMAIN_FLAG_QCOM_PDC_WAKEUP`, `IRQ_DOMAIN_FLAG_QCOM_MPM_WAKEUP`, and inline `irq_domain_qcom_handle_wakeup` to detect domains that need Qualcomm wake handling.

Control flow: GPIO/irqchip code checks the domain flags when mapping or configuring IRQ wake behavior, especially when a GPIO IRQ has a separate wake interrupt path.

State and persistence: Wake capability is stored in IRQ domain flags and irqchip state. Hardware wake configuration persists through suspend until cleared.

Dependencies and integration: Depends on IRQ domain structures and integrates with Qualcomm PDC, MPM, GPIO, pinctrl, and suspend wakeup paths.

Risks and test signals: Incorrect flags can make wake IRQs unavailable or duplicated. Test suspend/resume wake from GPIOs, domains without wake flags, and GPIOs with `GPIO_NO_WAKE_IRQ`.
