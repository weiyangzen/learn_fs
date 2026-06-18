<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spmi.h -->
# sources/distributed-fs/ceph-client/include/linux/spmi.h

Purpose: Defines the System Power Management Interface bus model, including SPMI devices, controllers, drivers, command opcodes, registration helpers, and register access helpers.

Important APIs/types/functions: `SPMI_MAX_SLAVE_ID`, `SPMI_CMD_*`, `struct spmi_device`, `to_spmi_device()`, `spmi_device_alloc/add/remove/put()`, `struct spmi_controller`, controller command callbacks, `spmi_controller_alloc/add/remove/put()`, devm controller helpers, `struct spmi_driver`, `spmi_driver_register/unregister()`, `module_spmi_driver()`, `spmi_find_device_by_of_node()`, register read/write helpers, and reset/sleep/wakeup/shutdown command helpers.

Control flow: Controller drivers allocate and add a `spmi_controller` with callbacks for command/read/write transactions. Device instances attach to controllers by USID. Client drivers register `spmi_driver` objects and bind through the driver model. Helper functions route standard register operations to controller callbacks with the right SPMI opcode.

State and persistence behavior: Runtime state is in embedded `struct device` objects, controller number, USID, driver data, and controller callbacks. Power state transitions are represented by SLEEP/WAKEUP/SHUTDOWN commands, not persistent storage.

Dependencies: Uses Linux device model, module ownership, OF node lookup, and `mod_devicetable.h`.

Integration points: PMIC and power-management devices on SPMI buses; runtime PM can issue SLEEP and WAKEUP commands as described in driver comments.

Risks: Invalid USID/opcode/length combinations can fail bus transactions. Controller callbacks must validate address widths and transfer sizes. Runtime PM balancing in client probe/remove must match command-side behavior.

Test signals: Controller registration tests, OF matching, client probe/remove, register read/write opcodes including extended long address paths, and runtime suspend/resume command traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spmi.h -->
