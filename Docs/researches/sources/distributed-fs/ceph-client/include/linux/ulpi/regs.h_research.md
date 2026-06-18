<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h

Purpose: provides ULPI 1.1 register offsets, set/clear register address helpers, and bit definitions for PHY function, interface, OTG, interrupt, debug, and carkit controls.

Important APIs and types: `ULPI_SET()`/`ULPI_CLR()` derive adjacent write-only set/clear offsets. Register macros cover vendor/product IDs, `ULPI_FUNC_CTRL`, `ULPI_IFC_CTRL`, `ULPI_OTG_CTRL`, USB interrupt enable/status/latch registers, scratch/debug, carkit optional registers, extended access, and vendor-specific ranges. Bit macros define transceiver speed, opmode, reset/suspend, serial/carkit modes, VBUS/ID/pulldown controls, interrupt events, and carkit pulse/control bits.

Control flow: PHY drivers and controller glue read ID registers, configure function/interface/OTG bits, use set/clear offsets to avoid read-modify-write races when supported by the PHY, and service interrupt/latch bits.

State and persistence: state is hardware register state in the ULPI PHY. The header only names fields.

Dependencies and integration points: relies on `BIT()` being available to includers. It integrates with ULPI read/write users in USB PHY and controller drivers.

Risks and test signals: risks include using `ULPI_SET/CLR` on unsupported registers, wrong speed/opmode combinations, failing to preserve reserved bits, and carkit/OTG bit drift from the spec. Test PHY identification, reset/suspend/resume, OTG VBUS/ID behavior, interrupt latch handling, and hardware-specific register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/regs.h -->
