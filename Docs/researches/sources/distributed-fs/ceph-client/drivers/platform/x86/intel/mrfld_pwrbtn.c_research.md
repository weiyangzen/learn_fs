<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c

## Purpose
Reports the Merrifield Basin Cove PMIC power button through the Linux input subsystem.

## Important APIs, Types, And Functions
`mrfld_pwrbtn_interrupt()` reads `BCOVE_PBSTATUS`, reports `KEY_POWER` pressed when `BCOVE_PBSTATUS_PBLVL` is clear, syncs input, and unmasks the level-1 power-button interrupt. Probe registers an input device, requests a shared threaded IRQ, unmasks PMIC interrupt bits, and sets wake IRQ.

## Control Flow
Platform child `mrfld_bcove_pwrbtn` binds, obtains IRQ 0 and parent regmap, registers input, requests IRQ with `IRQF_ONESHOT | IRQF_SHARED`, unmasks PMIC interrupt levels, and enables wake.

## State And Persistence
Driver state is the input device and regmap pointer. PMIC interrupt masks and wake IRQ state persist while bound.

## Dependencies And Integration Points
Depends on Basin Cove PMIC MFD/regmap, input subsystem, PM wakeirq, and platform IRQ resources.

## Risks And Test Signals
Risks are polarity mismatch, failure to unmask nested PMIC interrupt bits, and shared IRQ noise. Test press/release events, suspend wake, IRQ sharing, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c -->
