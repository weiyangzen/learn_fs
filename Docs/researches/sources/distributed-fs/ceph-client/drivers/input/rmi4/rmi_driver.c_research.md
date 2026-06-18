<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c

## Purpose
`rmi_driver.c` is the physical-device driver for one RMI4 sensor. It resets the sensor, scans the Page Description Table, creates RMI function devices, allocates interrupt state, owns the shared input device, dispatches attention IRQs, handles suspend/resume, and processes sensor reset/configuration requests.

## Important APIs, Types, and Functions
Exported or cross-file functions include `rmi_free_function_list()`, `rmi_set_attn_data()`, `rmi_find_function()`, `rmi_enable_sensor()`, `rmi_scan_pdt()`, `rmi_read_register_desc()`, `rmi_get_register_desc_item()`, `rmi_register_desc_calc_size()`, `rmi_register_desc_calc_reg_offset()`, `rmi_register_desc_has_subpacket()`, `rmi_initial_reset()`, `rmi_enable_irq()`, `rmi_disable_irq()`, `rmi_driver_suspend()`, `rmi_driver_resume()`, `rmi_probe_interrupts()`, `rmi_init_functions()`, `rmi_register_physical_driver()`, and `rmi_unregister_physical_driver()`. Probe logic is in `rmi_driver_probe()`.

## Control Flow
Probe validates a physical RMI device, loads OF platform data, allocates `struct rmi_driver_data`, performs an initial F01 reset by scanning page 0, reads PDT properties, initializes IRQ locks, counts function IRQs and bootloader state, allocates IRQ masks/domain, allocates or reuses an input device, scans the PDT again to create function children, creates F34 sysfs, registers input if owned by the core, registers the physical IRQ, and enables the sensor once F01 is bound. On interrupt, `rmi_irq_fn()` optionally consumes transport-provided attention FIFO data, processes enabled IRQ bits, calls `handle_nested_irq()` for each function bit, and syncs the shared input device.

## State and Persistence
`struct rmi_driver_data` stores the function list, f01/f34 containers, IRQ domain, IRQ bitmaps, current/new masks, enabled state, attention FIFO, input device, bootloader mode, and PDT properties. It is devm-managed for the physical device. Function list teardown unregisters child devices in reverse order so F01 is removed last.

## Dependencies and Integration Points
The file integrates with RMI transport devices, `rmi_bus.c` function registration, function handlers such as F01/F11/F12/F34, Linux irqdomain/nested IRQ, input core, OF properties, and PM wrappers exported to transports. `rmi_driver.h` exposes register descriptor parsing and PDT definitions to function drivers.

## Risks and Edge Cases
Initial reset failure is logged but not fatal so slow cold-boot sensors can still bind. The PDT scan stops after two empty pages or bootloader mode. IRQ memory allocation uses one devm block split into four bitmaps, so size calculations must remain consistent. Transport attention FIFO data is allocated with `GFP_ATOMIC` and drained recursively if multiple entries exist. `rmi_register_desc_calc_reg_offset()` increments offset by one per register instead of by each register size, which may be intentional for register index offsets or a risk for byte-offset consumers.

## Test Signals
Test cold/warm boot reset behavior, devices in bootloader mode, PDT scan over multiple pages, IRQ enable/disable mask writes, nested function IRQ dispatch, transport-provided attention data, suspend/resume with wake IRQ, function teardown order, and register descriptor parsing with known F12/F54 descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c -->
