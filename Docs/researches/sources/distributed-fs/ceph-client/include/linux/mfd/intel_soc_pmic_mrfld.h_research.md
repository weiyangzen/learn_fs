# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_mrfld.h

Purpose: This header defines Intel Merrifield Basin Cove PMIC ID, interrupt, mask, and level-two IRQ bitfields for the common Intel SoC PMIC stack.

Important APIs, types, and constants: Register macros identify ID, level-one IRQ, power-button, TMU, thermal, BCU, ADC, charger, GPIO, critical, and corresponding mask registers. ID extraction helpers `BCOVE_MINOR`, `BCOVE_MAJOR`, and `BCOVE_VENDOR` decode revision/vendor fields. Level-one bits identify the IRQ groups, and level-two bits cover power button press/release, ADC events, charger battery alerts, VBUS/DC/battery/USB-ID detection, and critical charger conditions.

Control flow, state, and persistence: Consumers read interrupt status groups, mask/unmask nested IRQs, and decode PMIC revision. State is PMIC interrupt latch/mask state and hardware revision data.

Dependencies and integration points: It depends on `linux/bits.h` and integrates with `intel_soc_pmic.h`, regmap-irq, power button, ADC, charger, GPIO, thermal, and critical-event child drivers.

Risks and test signals: Risks include grouped IRQ masking errors, charger IRQ0/IRQ1 confusion, ID field decoding mistakes, and missing critical-event handling. Test signals include nested IRQ group tests, charger detection interrupts, ADC interrupt tests, ID decode validation, and suspend wakeup from power button or charger insertion.
