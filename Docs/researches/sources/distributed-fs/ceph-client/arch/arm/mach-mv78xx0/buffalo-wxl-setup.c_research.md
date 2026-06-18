# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/buffalo-wxl-setup.c

Purpose: Board setup for Buffalo WXL NAS systems based on MV78xx0.

Important APIs/types/functions: Defines board init data for MPP pins, Ethernet, SATA, NAND/flash, buttons/LEDs, PCIe, and `MACHINE_START` style board registration.

Control flow: Board init configures MPP, registers platform devices, initializes PCIe/SATA/ethernet/flash/GPIO resources, and wires board-specific peripherals.

State and persistence: Persistent hardware state includes pin mux, registered platform devices/resources, MAC/flash/SATA setup, and GPIO defaults.

Dependencies and integration points: Depends on MV78xx0 common init, MPP, PCIe, legacy platform device APIs, and board bootloader machine ID.

Risks: Hard-coded resources and GPIOs are board-specific; applying to a variant can break storage/network/LEDs. Legacy board files lack DT validation.

Test signals: Boot Buffalo WXL, verify Ethernet, SATA disks, flash, LEDs/buttons, and PCIe.
