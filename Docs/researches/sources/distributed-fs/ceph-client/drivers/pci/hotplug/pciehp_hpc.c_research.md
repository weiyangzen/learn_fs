# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_hpc.c

## Purpose
Implements the hardware-facing half of the PCI Express hotplug controller driver. It owns Slot Control/Status command sequencing, link and presence checks, attention/power indicator control, power on/off commands, interrupt or polling notification setup, reset/link-flap suppression, and `struct controller` initialization for a PCIe hotplug port.

## Important APIs, Types, and Functions
Public entry points include `pcie_init()`, `pciehp_release_ctrl()`, `pcie_init_notification()`, `pcie_shutdown_notification()`, `pciehp_power_on_slot()`, `pciehp_power_off_slot()`, `pciehp_check_link_status()`, `pciehp_check_link_active()`, `pciehp_card_present()`, `pciehp_card_present_or_link_active()`, `pciehp_reset_slot()`, and indicator/status helpers used by the core hotplug slot operations. Internal command helpers are `pcie_do_write_cmd()`, `pcie_wait_cmd()`, and `pcie_poll_cmd()`. Notification handlers are `pciehp_isr()`, `pciehp_ist()`, and `pciehp_poll()`. The file also declares DMI and PCI fixups for broken presence and command-complete behavior.

## Control Flow
`pcie_init()` allocates and initializes the controller, reads slot capabilities, sets state from the subordinate bus contents, applies in-band presence disable and command-completion quirks, clears stale Slot Status event bits, and powers off empty slots when possible. Runtime commands serialize under `ctrl_lock`, wait for any outstanding command completion unless `NO_CMD_CMPL`, write Slot Control, and optionally wait again. IRQ mode installs a shared threaded IRQ; polling mode starts a kthread that repeatedly runs the same ISR/IST paths. The hard IRQ clears Slot Status bits, wakes waiters for Command Completed immediately, and records hotplug events for the thread. The IRQ thread handles attention buttons, power faults, DPC/spurious link changes, disable requests, and presence/link changes under `reset_lock`.

## State and Persistence Behavior
Persistent controller state lives in `struct controller`: cached slot capabilities/control, command busy/start time, pending event bits, wait queues, state locks, `reset_lock`, current ON/OFF state, notification-enabled flag, in-band presence disable flag, stored downstream device serial number, and power-fault suppression flag. Hardware state is PCIe Slot Control, Slot Status, Link Control, and Link Status. Runtime PM references keep the port parent accessible during interrupt handling.

## Dependencies and Integration Points
Depends on PCIe capability accessors, PCI hotplug core data from `pciehp.h`, runtime PM, DMI matching, IRQ threading, kthreads, DPC/AER helpers, secondary bus reset helpers, and global PCI bus locking semantics in callers. It integrates with `pciehp_pci.c` enumeration/removal and higher-level pciehp state-machine functions such as `pciehp_handle_presence_or_link_change()`, `pciehp_handle_button_press()`, and `pciehp_request()`.

## Risks
Command completion handling is hardware-quirk sensitive; clearing `cmd_busy` too early or waiting when completions never arrive can wedge hotplug. Slot Status bits are write-1-to-clear and can race with MSI reassertion, so the reread loop matters. Link and presence events may be intentionally ignored during DPC recovery, secondary bus reset, suspend, or firmware reconfiguration; missing the synthetic follow-up can hide removal. Runtime PM and reset locking are interleaved with IRQ handling, so lock ordering changes can deadlock hotplug, reset, and driver bind/unbind paths.

## Test Signals
Exercise module probe/remove on real or emulated PCIe hotplug ports, interrupt and polling modes, attention-button workflows, surprise removal, safe removal, DPC recovery, secondary bus reset, runtime suspend/resume, broken Command Completed controllers, Dell/in-band presence disable systems, link training failure, empty-slot power-off, indicator sysfs reads/writes, and repeated hotplug under MSI and INTx.
