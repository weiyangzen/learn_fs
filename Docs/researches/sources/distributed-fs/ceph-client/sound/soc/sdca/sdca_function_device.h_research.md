# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_function_device.h

## Purpose
Private container type for SDCA auxiliary function devices.

## APIs, Types, and Functions
Defines `struct sdca_dev`, containing an `auxiliary_device` and copied `struct sdca_function_data`, plus `auxiliary_dev_to_sdca_dev()` for container lookup.

## Control Flow, State, and Persistence
The header has no executable code. It defines the per-function auxiliary device state used by registration and function-driver probe paths.

## Dependencies and Integration
Depends on auxiliary bus and SDCA function metadata via included users. It is shared by `sdca_function_device.c` and function drivers that need to recover the SDCA container.

## Risks and Test Signals
Risks are structure drift with registration code and confusion between the copied `function` field and the parsed function data held by the class core. Build coverage and auxiliary probe path tests are the main signals.
