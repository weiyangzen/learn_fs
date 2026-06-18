# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c

This driver controls Qualcomm PMIC eUSB2 repeaters through the parent device regmap. Per-compatible `eusb2_repeater_cfg` tables provide default tuning registers and regulator names for PM8550B, PMIV0104, SMB2360, and SMB2370.

Probe gets match data, obtains the parent regmap, reads the `reg` base offset, initializes bulk regulators, creates a PHY, and registers a provider. Init enables regulators, sets `EUSB2_RPTR_EN`, writes PMIC-specific tuning defaults, applies DT overrides such as `qcom,tune-usb2-preem`, `qcom,tune-usb2-disc-thres`, amplitude, FSDIF, and squelch detector breakpoint mapping, then polls `RPTR_OK`. `set_mode()` applies a host-mode workaround forcing 19.2 MHz clock bits and clears it for device mode. Exit disables regulators; remove calls exit defensively.

State includes base offset, regulators, mode-sensitive force registers, and tuning registers. Dependencies are regmap, regulators, generic PHY, OF properties, and PMIC parent devices. Risks include a very small poll timeout, repeated exit on remove after managed PHY users may already have exited, silent ignore of unsupported squelch DT values, and shared-regulator host/device mode persistence. Test signals are init timeout logs and USB role-switch behavior.
