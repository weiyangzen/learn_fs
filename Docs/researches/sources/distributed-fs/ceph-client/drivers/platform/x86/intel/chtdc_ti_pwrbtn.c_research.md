<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c

## Purpose
Reports the Cherry Trail Dollar Cove TI PMIC power button as a Linux input `KEY_POWER` device.

## Important APIs, Types, And Functions
The IRQ handler reads `CHTDC_TI_SIRQ_REG` through the parent PMIC regmap and reports press when `SIRQ_PWRBTN_REL` is clear. Probe allocates an input device, registers `KEY_POWER`, requests a threaded IRQ, and configures wake IRQ support.

## Control Flow
Platform probe obtains IRQ 0 and parent `intel_soc_pmic` regmap. Every interrupt reads button state, emits key event plus sync, and returns handled. Remove clears wake IRQ and disables device wakeup.

## State And Persistence
Driver state is devres-managed input and the regmap pointer stored in device drvdata. Wake IRQ state persists while the device is active.

## Dependencies And Integration Points
Depends on the Dollar Cove TI PMIC MFD child, input subsystem, platform IRQs, regmap, and PM wakeirq.

## Risks And Test Signals
Risks include interpreting release polarity incorrectly and failing to wake from suspend. Test press/release with `evtest`, IRQ count, suspend wake, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c -->
