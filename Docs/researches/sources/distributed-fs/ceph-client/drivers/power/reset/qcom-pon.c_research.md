# sources/distributed-fs/ceph-client/drivers/power/reset/qcom-pon.c

## Purpose
Qualcomm SPMI PMIC PON reboot-mode driver.

## Important APIs, Types, and Functions
`struct qcom_pon`, `qcom_pon_reboot_mode_write()`, and probe with reboot-mode registration.

## Control Flow
probe obtains parent regmap/base address from resources or match data, initializes reboot-mode driver, and registers it; write callback stores magic into PON spare/reset-reason register fields.

## State and Persistence Behavior
selected reboot mode persists in PMIC PON registers for bootloader/firmware after reset.

## Dependencies and Integration Points
ARCH_QCOM, MFD_SPMI_PMIC, regmap, OF match data, reboot-mode core.

## Risks and Edge Cases
register offsets/masks vary by PMIC generation; wrong magic layout breaks bootloader interpretation; write failures happen during reboot notification.

## Test Signals
Qualcomm DT compatibles, reboot modes such as bootloader/recovery, regmap failure injection, and bootloader consumption.
