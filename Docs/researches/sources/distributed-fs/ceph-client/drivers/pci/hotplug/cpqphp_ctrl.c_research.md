# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_ctrl.c

## Purpose
Contains the Compaq hotplug controller event engine and resource allocator. It handles hardware interrupts, switch/presence/power-fault events, pushbutton delay semantics, board add/replace/remove, bus speed changes, resource splitting/combining, recursive bridge configuration, and controller hardware tests.

## Important APIs, Types, and Functions
Public functions are `cpqhp_ctrl_intr()`, `cpqhp_slot_create()`, `cpqhp_slot_find()`, `cpqhp_resource_sort_and_combine()`, `cpqhp_event_start_thread()`, `cpqhp_event_stop_thread()`, `cpqhp_pushbutton_thread()`, `cpqhp_process_SI()`, `cpqhp_process_SS()`, and `cpqhp_hardware_test()`. Key internal routines include `handle_switch_change()`, `handle_presence_change()`, `handle_power_fault()`, resource selection helpers `get_io_resource()`, `get_resource()`, `get_max_resource()`, bridge split helpers, `set_controller_speed()`, `board_replaced()`, `board_added()`, `remove_board()`, `event_thread()`, `interrupt_event_handler()`, `configure_new_device()`, and `configure_new_function()`.

## Control Flow
The IRQ handler checks SOGO completion and general input interrupts, clears hardware bits, diffs `INT_INPUT_CLEAR` against `ctrl_int_comp`, converts switch/presence/power changes into `event_queue` entries, handles reset completion, and wakes the event kthread. The kthread either runs a pending pushbutton timer action or drains all controller event queues. Button releases blink the green LED and arm a five-second timer; cancellation restores LED state. Timer expiry calls SI for power-on/add or SS for power-off/remove. Board add powers the slot briefly to read adapter speed, may change segment speed, powers off, then enables the slot, configures resources and devices, saves slot config, and turns the green LED on. Remove unconfigures devices, saves or returns resources, powers down, and recreates an empty placeholder.

## State and Persistence Behavior
State is kept in `cpqhp_event_thread`, `pushbutton_pending`, each controller's circular ten-entry `event_queue`, slot timer/state fields, `pci_func` presence/switch/status/configured flags, resource lists, and PCI config-space snapshots. Resource allocation mutates controller free pools and function-owned lists; remove returns them when add support is available. No direct durable persistence is done here, but its resource-list mutations are the data later stored by NVRAM teardown.

## Dependencies and Integration Points
Depends on controller MMIO helpers from `cpqphp.h`, PCI config-space access, PCI hotplug-core callbacks from `cpqphp_core.c`, Linux kthreads/timers/wait queues, and PCI-core scan/remove helpers via `cpqphp_pci.c`. Legacy IRQ programming calls `cpqhp_set_irq()` for direct devices and bridge interrupt swizzling.

## Risks
The event queue has fixed length ten with overwrite-style modulo advancement and no locking in enqueue/dequeue paths. Resource allocation is hand-written and assumes 32-bit BARs, specific bridge windows, power-of-two sizes, and x86-era IRQ behavior. Several config writes ignore intermediate `rc` values. Pushbutton timer state is global, so concurrent button timers can collide. Bus speed changes temporarily disable slots and LEDs, so errors can leave hardware in surprising states.

## Test Signals
Interrupt diff handling, switch open/close, presence insert/remove, power-fault set/clear, button press/release/cancel timing, SI/SS sysfs operations, add of normal and multifunction devices, bridge add with subordinate devices, remove with resource return, replace validation, speed changes across 33/66/PCI-X modes, event thread stop on unload, resource sort/combine correctness, and ENOMEM/error-path rollback are key signals.
