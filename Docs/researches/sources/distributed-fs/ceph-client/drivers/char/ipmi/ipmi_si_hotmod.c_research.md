# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hotmod.c

Purpose: This module implements the writable `hotmod` module parameter used to dynamically add or remove IPMI SI platform devices after module load.

Important APIs, types, and functions: `module_param_call(hotmod, hotmod_handler, ...)` binds writes to `hotmod_handler`. Parsing helpers are `parse_str`, `check_hotmod_int_op`, and `parse_hotmod_str`. Operations are `add` and `remove`; interface types are `kcs`, `smic`, and `bt`; address spaces are `mem` and `i/o`; options include `rsp`, `rsi`, `rsh`, `irq`, and `ipmb`. `hotmod_nr` generates add instance IDs.

Control flow: `hotmod_handler` duplicates and strips the input string, processes colon-separated operations, parses each comma-separated operation into `struct ipmi_plat_data`, then either creates a `hotmod-ipmi-si` platform device through `ipmi_platform_add` or removes a matching SI with `ipmi_si_remove_by_data`. On removal, it unregisters the platform device only if the returned device is a platform device named `hotmod-ipmi-si`.

State and persistence behavior: Dynamic devices persist in the platform bus until explicitly removed or until `ipmi_si_hotmod_exit` removes all hotmod devices by name. The atomic instance counter persists for the module lifetime. No disk state is stored.

Dependencies and integration points: It depends on kernel parameter writes, IPMI platform-data synthesis, SI remove-by-address/type, platform-device unregister, and normal SI probe/cleanup paths. It is designed as a runtime companion to hardcoded and firmware discovery.

Risks and edge cases: The parser mutates a duplicated input buffer and returns the original input length on success, as module parameter setters expect. Bad option syntax fails the whole write at the first invalid operation. Remove can target an SI by address/type even if the matching device was not hotmod-created, but it only unregisters platform devices with the hotmod name. `put_device(dev)` is called even when no device is found, relying on NULL-safe behavior.

Test signals: Write single and multiple colon-separated add/remove operations, invalid operations/types/address spaces/options, decimal and hex addresses, each optional register/IRQ/slave field, removal of existing hotmod devices, attempted removal of non-hotmod devices, and cleanup removing all remaining hotmod devices.
