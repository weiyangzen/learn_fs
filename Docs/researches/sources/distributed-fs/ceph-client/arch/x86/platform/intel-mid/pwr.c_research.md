<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c

## Purpose
Implements the Intel MID Power Management Unit driver used to set South Complex PCI device power states and trigger system S5 poweroff.

## Important APIs, Types, And Functions
`struct mid_pwr` holds MMIO registers, IRQ, mutex, availability flag, and Logical SubSystem cache. Exports include `intel_mid_pci_set_power_state()`, `intel_mid_pci_get_power_state()`, `intel_mid_pwr_power_off()`, and `intel_mid_pwr_get_lss_id()`. Probe supports Penwell and Tangier IDs with SoC-specific initial state tables.

## Control Flow
PCI probe enables the PWRMU device, maps BAR0, disables interrupts, initializes all wake/power state registers, requests an IRQ, and publishes the singleton `midpwr`. Power-state changes map PCI vendor capability LSS IDs to 2-bit PM state fields, compute the weakest shared-device state, write SSC registers, issue `CMD_SET_CFG`, and poll PM busy clear.

## State And Persistence
The singleton `midpwr` and `lss` cache persist after probe. Hardware PM registers store current wake and power settings. The mutex serializes all register updates.

## Dependencies And Integration Points
Integrates with `drivers/pci/pci-mid.c` platform PM hooks, PCI config vendor capabilities, MMIO PWRMU registers, IRQ subsystem, and Intel MID platform poweroff code.

## Risks And Edge Cases
`intel_mid_pci_set_power_state()` logs failures but returns 0, matching PCI hook expectations but hiding hardware errors from callers. Shared LSS cache has only four device slots. Busy polling can stall for 500 ms. Poweroff dereferences `midpwr` and assumes probe completed.

## Test Signals
PCI runtime suspend/resume on South Complex devices, correct PM_SSS bit transitions, no unexpected IRQ storms, and successful S5 on MID hardware validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c -->
