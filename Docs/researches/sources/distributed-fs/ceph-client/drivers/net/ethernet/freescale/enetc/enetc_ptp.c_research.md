# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ptp.c

## Purpose
Registers the ENETC PTP hardware clock PCI function using the shared QorIQ PTP implementation.

## Important APIs, Types, and Functions
Important elements are `enetc_ptp_caps`, `enetc_ptp_probe`, `enetc_ptp_remove`, the PCI ID table for `ENETC_DEV_ID_PTP`, and module PCI driver registration. PTP operations are delegated to `ptp_qoriq_adjfine`, `ptp_qoriq_adjtime`, `ptp_qoriq_gettime`, `ptp_qoriq_settime`, and `ptp_qoriq_enable`.

## Control Flow
Probe skips disabled OF nodes, enables PCI memory space, sets a 64-bit DMA mask, requests BARs, enables bus mastering, allocates `struct ptp_qoriq`, maps BAR0, allocates one MSI-X vector, requests the QorIQ PTP ISR, initializes the PTP clock with `ptp_qoriq_init`, and stores drvdata. Remove frees the PTP clock, IRQ vectors, driver state, memory regions, and PCI device.

## State and Persistence
Persistent hardware state is the mapped timer/PTP PCI BAR and MSI-X interrupt. Software state is `struct ptp_qoriq`, including IRQ number, device pointer, registered PTP clock, and QorIQ timer state.

## Dependencies and Integration Points
Depends on PCI core, `linux/fsl/ptp_qoriq.h`, kernel PTP clock APIs, and OF availability checks. PF/VF ethtool timestamp reporting locates this PHC by OF `ptp-timer` phandle or PCI devfn assumptions.

## Risks
Risks include PHC lookup mismatch if PCI devfn layout changes, interrupt allocation failure, missing cleanup of mapped BAR on init failure, and relying on QorIQ PTP behavior for all ENETC timer revisions. Remove calls `ptp_qoriq_free` but not an explicit `iounmap`, assuming the QorIQ free path owns mapped resources after init.

## Test Signals
Probe the PTP function, run `phc2sys`/`ptp4l`, query `ethtool -T` from PF/VF, test disabled DT nodes, force MSI-X or PTP init failures, and verify module unload/reload leaves no IRQ or PHC leaks.
