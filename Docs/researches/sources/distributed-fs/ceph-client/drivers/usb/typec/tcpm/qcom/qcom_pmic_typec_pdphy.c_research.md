# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.c

## Purpose

`qcom_pmic_typec_pdphy.c` implements the Qualcomm PMIC USB PD PHY half of the TCPM adapter. It handles PD message TX/RX registers, hard reset signaling, PD role header configuration, IRQ mapping, regulator enablement, and PHY reset.

## Important APIs, Types, and Functions

`struct pmic_typec_pdphy` stores device, TCPM port, regmap/base, IRQ data, reset/receive work, `vdd-pdphy` regulator, and a spinlock for register atomicity. TCPM callbacks installed here are `qcom_pmic_typec_pdphy_set_pd_rx()`, `qcom_pmic_typec_pdphy_set_roles()`, and `qcom_pmic_typec_pdphy_pd_transmit()`. Internal helpers include reset on/off, TX control clear, signal/payload transmit, receive buffer handling, ISR dispatch, enable/disable/reset, start/stop, and `qcom_pmic_typec_pdphy_probe()`.

## Control Flow

Probe validates resource IRQ count, allocates IRQ data, gets `vdd-pdphy`, initializes state and work, requests named IRQs with `IRQF_NO_AUTOEN`, installs TCPM callbacks, and assigns start/stop functions. Start enables the regulator, stores the TCPM port, resets/enables the PHY, then enables all IRQs. Transmit either frames a payload into header/data/size registers and starts SEND_MSG, or clears TX control and starts a signal/hard reset command with retry count based on negotiated revision. IRQs translate message TX success/fail/discard to `tcpm_pd_transmit_complete()`, message RX to buffer read plus `tcpm_pd_receive()`, and signal RX to scheduled hard reset work.

## State and Persistence Behavior

PD PHY state is runtime-only. The spinlock protects multi-register sequences and RX ownership handoff. The regulator and hardware enable bit define whether the PHY is active. Stop disables IRQs, resets filtering/TX, and disables the regulator.

## Dependencies and Integration Points

It depends on platform named IRQs, regmap, regulator core, TCPM PD callbacks, USB PD helpers, workqueues, and `qcom_pmic_typec` shared state. It integrates as the PD message transport provider for Qualcomm PMIC TCPM ports.

## Risks and Test Signals

Risks include RX buffer ownership races, size validation around hardware's off-by-one length convention, ignored `receive_work` field, hard reset scheduling from IRQ work, transmit busy when RX pending, and all PMIC IRQ names matching DT resources. Test signals include PD RX enable/disable, role header writes, SOP payload TX, hard/cable reset TX, TX success/fail/discard IRQs, RX message parsing and acknowledge, hard reset receive, regulator failure unwind, and stop disabling IRQs.
