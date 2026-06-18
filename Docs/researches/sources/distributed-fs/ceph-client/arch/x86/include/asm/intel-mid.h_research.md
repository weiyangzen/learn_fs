<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h

## Purpose
Intel MID platform helper declarations for legacy mobile/SoC detection and platform initialization. The header is 23 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/pci.h>`

Notable constants/macros: `#define _ASM_X86_INTEL_MID_H`; `#define INTEL_MID_PWR_LSS_OFFSET 4`; `#define INTEL_MID_PWR_LSS_TYPE (1 << 7)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_MID_H`; `extern int intel_mid_pci_init(void);`; `extern int intel_mid_pci_set_power_state(struct pci_dev *pdev, pci_power_t state);`; `extern pci_power_t intel_mid_pci_get_power_state(struct pci_dev *pdev);`; `extern void intel_mid_pwr_power_off(void);`; `#define INTEL_MID_PWR_LSS_OFFSET 4`; `#define INTEL_MID_PWR_LSS_TYPE (1 << 7)`; `extern int intel_mid_pwr_get_lss_id(struct pci_dev *pdev);`

## Control Flow
Boot/platform code uses these declarations to detect MID variants and install SoC-specific callbacks or device setup.

## State and Persistence
State is global platform type/callback data in implementation files, not this header.

## Dependencies and Integration Points
Depends on x86 platform init, device enumeration, and legacy Intel MID support code.

## Risks
Risks include stale platform IDs, wrong init ordering, and bitrot due to rare hardware.

## Test Signals
Tests should compile MID configs and boot available MID/SoC hardware or emulation for platform detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h -->
