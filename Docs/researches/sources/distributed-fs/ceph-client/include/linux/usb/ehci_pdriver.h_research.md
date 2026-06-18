<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h

Purpose: defines platform data for the generic platform EHCI host-controller driver.

Important APIs and types: `struct usb_ehci_pdata` carries capability-register offset, integrated TT flag, hardware quirk flags for Synopsys, endian descriptors/MMIO, watchdog, reset-on-resume, 64-bit DMA, spurious overcurrent, and platform hooks for power on/off/suspend and pre-setup.

Control flow: platform glue provides this data at probe; the generic EHCI platform driver powers clocks/regulators, applies pre-setup quirks, configures endian/DMA/watchdog behavior, and handles suspend/resume power transitions through hooks.

State and persistence: platform data is static configuration plus callback pointers. Runtime controller state is owned by the EHCI HCD and platform driver.

Dependencies and integration points: forward-declares platform devices and USB HCDs. It integrates board/SoC glue with generic EHCI core.

Risks and test signals: risks include wrong caps offset, endian flags mismatched to hardware, power hook ordering failures, reset-on-resume data loss, and spurious overcurrent masking real faults. Test platform probe/remove, power transitions, suspend/resume, DMA mask selection, and quirk-specific controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_pdriver.h -->
