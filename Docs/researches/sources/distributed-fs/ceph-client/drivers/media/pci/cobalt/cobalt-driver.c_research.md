<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c

Purpose: Implements PCI probe/remove and high-level initialization for the Cisco Cobalt driver, including PCI resource setup, MSI, I2C bus registration, ADV HDMI subdevice creation, stream topology setup, V4L2/ALSA node registration, interrupt enabling, and flash probing.

Important APIs/functions: `cobalt_probe()` is the main lifecycle entry. `cobalt_setup_pci()` enables the PCI device, validates link width, sets DMA mask, requests/maps BARs, disables interrupts, allocates MSI, requests IRQ, and initializes Omnitek DMA. `cobalt_stream_struct_init()` maps logical streams to DMA/video/audio roles. `cobalt_subdevs_init()` creates four ADV7604 HDMI receivers and marks associated video/audio streams live. `cobalt_subdevs_hsma_init()` detects either an ADV7842 HSMA receiver or ADV7511 transmitter and sets `have_hsma_rx`/`have_hsma_tx`. `cobalt_set_interrupt()` programs system interrupt masks. `cobalt_notify()` handles subdevice hotplug and source-change notifications.

Control flow: PCI probe allocates `struct cobalt`, registers the V4L2 device and IRQ workqueue, sets up PCI/MSI, reads HDL info, initializes I2C, initializes stream records, registers input and HSMA subdevices, creates V4L2/ALSA nodes, enables interrupts, services pending subdevice interrupts, probes flash, and returns. Error labels unwind in reverse. Remove unregisters flash, disables interrupts, flushes work, unregisters nodes/subdevices/I2C/MSI/BARs, disables PCI, destroys workqueue, unregisters V4L2, and frees state.

State/persistence: `struct cobalt` owns all runtime state: PCI/V4L2 handles, BAR mappings, card revision, stream array, I2C adapters, HSMA flags, IRQ counters/workqueue, DMA capabilities, HDL info, and MTD pointer. Hardware state includes sysctrl/sysstat bits, reset lines, interrupt masks, and subdevice EDID/configuration.

Dependencies/integration: Integrates PCI core, V4L2 device/subdev/control/event APIs, ADV7604/ADV7842/ADV7511 I2C subdrivers, Omnitek DMA, Cobalt I2C, V4L2 nodes, ALSA, IRQ, flash, and CPLD support.

Risks: Initialization order is hardware-sensitive; interrupts are disabled before subdevice setup and enabled only after nodes register. Probe fails on PCIe link-width mismatch where a seating issue is inferred. `cobalt_ignore_err` can hide missing I2C/subdevice problems by creating dummy nodes. HSMA detection treats absence of RX as possible TX, so board wiring assumptions matter. Error paths must maintain reverse-order cleanup for partially initialized hardware.

Test signals: PCI probe/remove, MSI request/free, BAR mapping including 64-bit BAR fallback, HDL info read, all I2C adapters, ADV subdevice registration, EDID programming, HSMA RX/TX detection, dummy-node behavior under `ignore_err`, flash probe, and suspend-like remove under active users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.c -->
