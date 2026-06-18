# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp.h

Purpose: Defines the shared private interface and controller state for the PCI Express hotplug driver. It centralizes the controller data structure, state machine constants, request flags, capability predicates, logging helpers, and function prototypes shared by `pciehp_core.c`, `pciehp_ctrl.c`, `pciehp_hpc.c`, and PCIe hotplug PCI configuration code.

Important APIs and types: The key type is `struct controller`, which owns the PCIe port service pointer, cached Device Serial Number, slot capability/control state, command-completion synchronization, pending events, notification/polling state, state machine fields, delayed attention-button work, hotplug core object, reset lock, and requester waitqueue. Important constants are `OFF_STATE`, `BLINKINGON_STATE`, `BLINKINGOFF_STATE`, `POWERON_STATE`, `POWEROFF_STATE`, `ON_STATE`, `DISABLE_SLOT`, and `RERUN_ISR`. Capability helpers include `ATTN_BUTTN()`, `POWER_CTRL()`, `MRL_SENS()`, `ATTN_LED()`, `PWR_LED()`, `NO_CMD_CMPL()`, and `PSN()`.

Control flow: The header has no executable flow beyond inline accessors `slot_name()` and `to_ctrl()`. It defines the control contract: core probe initializes `struct controller`, HPC code handles slot-control/register access and interrupts, ctrl code consumes pending events and transitions state, and config code enumerates or removes downstream PCI devices.

State and persistence: `struct controller` is the persistent state container for one PCIe hotplug slot. It caches slot registers, tracks command-completion timing, stores event bits across IRQ top/bottom halves, records whether notifications are enabled, and serializes state transitions through `state_lock` and `reset_lock`.

Dependencies and integration points: Includes Linux PCI, hotplug, mutex, rwsem, delay, and workqueue APIs plus PCIe port service definitions. The prototypes connect core lifecycle (`pcie_init()`, `pciehp_release_ctrl()`), notification (`pcie_init_notification()`), hardware operations (`pciehp_power_on_slot()`), event handling (`pciehp_handle_presence_or_link_change()`), sysfs entry points, and reset support.

Risks: State constants and request flags are shared across multiple C files, so changing values requires auditing IRQ event encoding and state-machine transitions. `DISABLE_SLOT` and `RERUN_ISR` deliberately live above the 16-bit Slot Status event width; new flags must preserve that separation. `struct controller` lock fields have documented responsibilities, and violating those lock boundaries can race sysfs, IRQ thread, PM, and reset paths.

Test signals: Compile coverage of all pciehp objects validates declarations. Runtime signals include one controller per hotplug-capable port, correct sysfs slot naming from `PSN()`, valid transitions among the six states, command completion waits waking through `queue`, requester waits waking after sysfs operations, and reset paths honoring `reset_lock`.
