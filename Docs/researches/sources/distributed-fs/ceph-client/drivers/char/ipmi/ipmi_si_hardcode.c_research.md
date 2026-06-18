# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hardcode.c

Purpose: This module converts boot/module parameters into synthetic SI platform devices for systems where firmware discovery is absent or intentionally overridden.

Important APIs, types, and functions: Parameters include `type`, `addrs`, `ports`, `irqs`, `regspacings`, `regsizes`, `regshifts`, and `slave_addrs`, each capped by `SI_MAX_PARMS`. `ipmi_hardcode_init_one` builds `struct ipmi_plat_data` and calls `ipmi_platform_add`. `ipmi_hardcode_init` parses comma-separated SI type strings and creates one platform device per configured port or memory address. `ipmi_si_hardcode_exit` removes hardcoded devices by name, and `ipmi_si_hardcode_match` reports whether an address is already user-hardcoded.

Control flow: During SI init, `ipmi_hardcode_init` splits the `type` string in-place, then iterates over the four possible entries. Nonzero I/O ports generate `IPMI_IO_ADDR_SPACE` devices; nonzero memory addresses generate `IPMI_MEM_ADDR_SPACE` devices. Missing type defaults to KCS; invalid type logs a warning and skips that entry.

State and persistence behavior: Parameter arrays are static module state, some init-only. Created platform devices persist until `ipmi_si_hardcode_exit` removes all devices named `hardcode-ipmi-si`. There is no disk persistence.

Dependencies and integration points: It depends on module parameter parsing, `ipmi_plat_data` construction, `ipmi_platform_add`, and SI duplicate suppression in `ipmi_si_add_smi`, which gives hardcoded devices priority over firmware-specified devices at the same address.

Risks and edge cases: Arrays are independently counted, so partial parameter sets can leave default zero values for optional IRQ/register/slave fields. A single index can create both port and memory devices if both arrays contain entries. Type parsing mutates the initdata string. Duplicate hardcoded addresses are not filtered here; later SI add logic handles conflicts.

Test signals: Boot with KCS/BT/SMIC types, invalid type strings, port-only and memory-only entries, mixed register spacing/size/shift, IRQ and slave address propagation, hardcoded address matching, and cleanup removing only `hardcode-ipmi-si` platform devices.
