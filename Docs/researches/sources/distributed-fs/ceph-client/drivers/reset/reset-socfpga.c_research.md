# sources/distributed-fs/ceph-client/drivers/reset/reset-socfpga.c

Purpose: early Intel/Altera SoCFPGA reset-manager registration using `reset_simple_ops`, plus a dummy platform driver to satisfy device-link probing.

Important APIs/types/functions: `a10_reset_init()` manually allocates `reset_simple_data`, maps the reset manager from OF, applies optional `altr,modrst-offset`, and registers 8 banks of resets with active-low status. `socfpga_reset_init()` scans early `altr,rst-mgr` nodes. The later `reset_socfpga_driver` has a no-op probe.

Control flow: early init registers reset control before normal driver model availability. Later the platform driver binds to the same compatible only to attach a driver to the device node.

State and persistence: early allocations and ioremap are not device-managed and remain for system lifetime. Hardware reset registers retain state.

Dependencies and integration: uses OF address translation, manual memory-region reservation, `reset_simple_ops`, `linux/reset/socfpga.h`, and built-in platform driver registration.

Risks and test signals: if `reset_controller_register()` fails, mapped memory is not unwound. Mismatched early and platform bindings can affect device links. Test early boot reset consumers, missing offset property fallback, duplicate reservation failure, and normal platform-device binding.
