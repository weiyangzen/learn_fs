# sources/distributed-fs/ceph-client/drivers/usb/atm/ueagle-atm.c

## Purpose
`ueagle-atm.c` is a `usbatm` mini-driver for ADI 930 and Eagle USB ADSL modems. It handles pre-firmware USB bootstrap, DSP page loading, CMV configuration, modem reset/reboot, status monitoring, optional synchronization wait, sysfs statistics, and multiple chip generations including Eagle IV protocol differences.

## Important APIs, Types, And Functions
- `struct uea_softc` stores USB/usbatm pointers, chip metadata, annex selection, boot/reset flags, wait queue, control thread, CMV descriptors, work item, DSP firmware, interrupt URB, protocol function pointers, and exported PHY stats.
- `uea_probe()` resets the USB device, loads pre-firmware for prefirm IDs, or delegates post-firmware devices to `usbatm_usb_probe()`.
- `uea_bind()` claims monitor/upstream/downstream interfaces, selects annex and altsetting, sets `UDSL_USE_ISOC`/`UDSL_IGNORE_EILSEQ`, and calls `uea_boot()`.
- `uea_boot()` chooses Eagle I/IV handlers, allocates the interrupt URB, submits it, and creates the monitoring kthread.
- `uea_start_reset()` drives modem reset, schedules DSP page 0 load, waits for modem-ready CMV, sends CMV configuration, and clears reset.
- `uea_load_page_e1()` and `uea_load_page_e4()` send DSP blocks over IDMA when interrupt packets request swap pages.
- `uea_cmv_e1()`/`uea_cmv_e4()` issue CMV reads/writes and wait for interrupt acknowledgements.
- `uea_stat_e1()`/`uea_stat_e4()` poll modem state and update ATM signal, link rate, margins, attenuation, and error counters.

## Control Flow
Pre-firmware devices request generation-specific firmware asynchronously and upload it through vendor control writes. Post-firmware devices bind through `usbatm`, claim extra interfaces, and create a control thread but only start it after generic initialization completes. The thread loops: reset or recover on errors, load DSP pages on interrupt requests via workqueue, wait for modem-ready CMV, send CMV files, then poll stats every second. Interrupt URBs dispatch either swap-page requests or CMV replies and resubmit themselves.

## State And Persistence Behavior
Runtime state is substantial: CMV ack state, current DSP page/overlay, loaded firmware pointer, modem stats, reset flag, synchronization wait queue, and module-parameter-derived annex/altsetting choices. Sysfs attributes expose and sometimes reset cached counters; writing `stat_status` requests reset. Firmware and CMV files are read from the firmware loader but no persistent state is written.

## Dependencies And Integration Points
The driver depends on USB core, firmware loader, CRC validation, kthreads, workqueues, wait queues, sysfs, `usbatm`, and ATM. It declares many `MODULE_FIRMWARE()` names for bootstrap, DSP, FPGA, and CMV files. It integrates with `usbatm` via mini-driver hooks and endpoint definitions.

## Risks And Edge Cases
There are many hardware-generation branches and endian-specific packet formats. CMV ack waits can timeout, causing reboot loops. Interrupt resubmission errors are not strongly recovered. Interface-claim failure paths in `uea_bind()` can leave earlier claimed interfaces until generic disconnect/release. Firmware/CMV validation prevents some corruption but missing files are common deployment failures. `modem_index` is global and wraps, so module-parameter association across multiple devices is order-dependent.

## Test Signals
Test prefirm and postfirm IDs for each chip family. Validate firmware CRC/corruption rejection, DSP page loading after interrupt requests, CMV v1/v2 fallback, annex auto/manual selection, bulk and isochronous modes, `sync_wait`, sysfs stats, write-triggered reset, and disconnect while the kthread waits for CMV or sync. Confirm ATM carrier becomes lost during reset and found when operational.
