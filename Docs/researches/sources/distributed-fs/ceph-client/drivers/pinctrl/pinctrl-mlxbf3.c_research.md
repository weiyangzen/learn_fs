# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mlxbf3.c

## Purpose
Implements NVIDIA BlueField-3 pinctrl for 56 GPIO-capable pins. It switches pins between firmware/hardware control and software GPIO control by writing set/clear firmware-control registers and exposes ACPI-described GPIO ranges.

## Important APIs, Types, and Functions
Key state is `struct mlxbf3_pinctrl`, which stores four MMIO windows for set/clear control of two GPIO banks. Static data includes `mlxbf3_pinctrl_gpio_ranges`, `mlxbf3_pins`, one-pin group names, and two functions `hwfunc` and `gpiofunc`. Runtime callbacks are `mlxbf3_get_groups_count`, `mlxbf3_get_group_name`, `mlxbf3_get_group_pins`, `mlxbf3_pmx_get_funcs_count`, `mlxbf3_pmx_get_func_name`, `mlxbf3_pmx_get_groups`, `mlxbf3_pmx_set`, and `mlxbf3_gpio_request_enable`.

## Control Flow and State
Probe maps four resources, registers and enables pinctrl, then adds two GPIO ranges mapping pin 0-31 to GPIO base 480 and pin 32-55 to GPIO base 456. Mux setting writes a bit to a clear register for hardware mode or to a set register for software GPIO mode, choosing bank 0 or bank 1 by pin number. GPIO requests force the requested pin into software-controlled mode. Persistent state lives in firmware-control hardware registers; there is no software cache or readback path.

## Dependencies and Integration Points
Depends on ACPI match ID `MLNXBF34`, platform MMIO resources, pinctrl core registration with explicit `pinctrl_enable`, and gpiolib range association. This driver is a pinmux companion to the BlueField GPIO controller rather than a full GPIO provider itself.

## Risks and Test Signals
Risks include unusual function/group metadata where functions advertise one group array but return all pins as group count, incorrect GPIO base mapping for the two ranges, no selector validation beyond two known enum values, and write-only control with no state verification. Test signals include ACPI probe, pinctrl debugfs group/function enumeration, GPIO request forcing software mode, MMIO trace/readback from adjacent firmware registers if available, and exercising pins on both sides of the 32-pin bank boundary.
