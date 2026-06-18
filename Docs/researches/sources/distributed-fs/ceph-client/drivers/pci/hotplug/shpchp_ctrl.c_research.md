# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_ctrl.c

## Purpose
Implements the SHPC policy/state machine for handling attention button, latch, presence, power-fault, sysfs enable/disable, board add, and board remove events.

## Important APIs, Types, and Functions
Event entry points are `shpchp_handle_attention_button()`, `shpchp_handle_switch_change()`, `shpchp_handle_presence_change()`, and `shpchp_handle_power_fault()`. User entry points are `shpchp_sysfs_enable_slot()` and `shpchp_sysfs_disable_slot()`. Core helpers include `board_added()`, `remove_board()`, `handle_button_press_event()`, `shpchp_queue_pushbutton_work()`, `interrupt_event_handler()`, `shpchp_enable_slot()`, and `shpchp_disable_slot()`.

## Control Flow
Hardware IRQ handlers queue compact event objects to per-slot workqueues. Button events enter a five-second blinking confirmation window; a second press cancels, while delayed work commits power on/off. Sysfs enable/disable bypasses the delay but still obeys the slot state machine. Add validates adapter present, latch closed, and power off, powers the slot, negotiates PCI/PCI-X bus speed if needed, enables the slot, waits for power fault, scans/configures PCI devices, updates state, and turns the green LED on. Remove unconfigures devices, disables the slot, clears attention, and updates cached state.

## State and Persistence Behavior
Per-slot state includes button state (`STATIC`, `BLINKING*`, `POWER*`), cached power/presence/latch/attention, `is_a_board`, fault status, and pending delayed work. Controller-level `crit_sect` serializes add/remove operations; per-slot `lock` serializes button/sysfs state transitions. Hardware slot power/LED/bus speed persists in SHPC registers.

## Dependencies and Integration Points
Depends on SHPC hardware commands/status from `shpchp_hpc.c`, PCI enumeration/removal in `shpchp_pci.c`, hotplug callbacks in `shpchp_core.c`, workqueues, timers, and PCI bus speed fields.

## Risks
State transitions are easy to break because the code unlocks around blocking enable/disable operations and relocks to update state. Bus speed changes are unsafe if other devices exist on the same bus and are guarded by `slots_not_empty`. Power-fault handling uses `p_slot->status == 0xFF` as an event flag. Button delayed work cancellation must be synchronized with sysfs actions and slot teardown.

## Test Signals
Exercise button press/commit/cancel, sysfs enable/disable in every state, presence/latch/power-fault interrupts, PCI-X bus speed mismatch, add failure rollback, AMD POGO errata path, and repeated rapid events on the same slot.
