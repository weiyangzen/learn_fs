# sources/distributed-fs/ceph-client/drivers/peci/internal.h

Purpose: Defines the internal PECI core contract shared by bus, device, sysfs, CPU, and request implementation files. It declares request allocation/transfer helpers, data accessors, bus/device types, driver registration helpers, and controller scan/create/destroy functions.

Important APIs and types: Constants `PECI_BASE_ADDR` and `PECI_DEVICE_NUM_MAX` define the CPU address window. `struct peci_device_id` matches devices by x86 VFM and carries driver data. `struct peci_driver` wraps a Linux `device_driver` with PECI `probe`, optional `remove`, and `id_table`. Macros `peci_driver_register()` and `module_peci_driver()` provide registration boilerplate. Numerous `peci_xfer_*` declarations expose typed PECI command builders.

Control flow: The header itself has no runtime flow, but it defines how requests move from higher-level clients to `request.c`, how drivers bind through `core.c`, and how devices are created/destroyed by scanning and sysfs.

State and persistence: No storage is defined here. The declarations expose stateful objects owned elsewhere: PECI request buffers, controller/device embedded `struct device` objects, bus attribute groups, and device attribute groups.

Dependencies and integration points: Includes Linux device/types headers and is included by all local PECI implementation files. It bridges private implementation details with exported namespace functions in `request.c`, `device.c`, and `core.c`.

Risks: Because this is the private ABI between PECI compilation units, signature drift breaks builds across multiple files. Buffer-size assumptions live in the public request structure while allocation validation is in `request.c`; new commands must keep these declarations and implementation macros aligned.

Test signals: Full PECI subsystem build, namespace export resolution, module_peci_driver users compiling, and command helper consumers linking against all declared functions.
