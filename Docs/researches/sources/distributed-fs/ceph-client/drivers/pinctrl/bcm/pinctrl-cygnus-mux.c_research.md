<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c

## Purpose
This file implements the Broadcom Cygnus group-based IOMUX driver. It exposes a large static pin/group/function matrix, programs group mux fields, and supports per-pin GPIO override for pins whose GPIO function is controlled through a second register block.

## Important APIs, Types, And Functions
`struct cygnus_pinctrl` stores the pinctrl device, two MMIO bases, group/function tables, a `mux_log`, and a spinlock. `struct cygnus_pin_group` ties a group to pins and a mux field described by `struct cygnus_mux`. `struct cygnus_mux_log` records whether an IOMUX field was configured and with which alternate value. `cygnus_pinmux_set()` detects conflicting double configuration and writes group mux bits. `cygnus_gpio_request_enable()` and `cygnus_gpio_disable_free()` set or clear per-pin GPIO override bits in `base1`.

## Control Flow
The arch initcall registers the platform driver early. Probe maps two resources, initializes the mux log for 8 registers times 8 mux fields, allocates pin descriptors with each pin's GPIO override metadata in `drv_data`, assigns static groups/functions, and registers pinctrl. Applying a state calls `cygnus_pinmux_set_mux()`, which logs and writes the group mux. GPIO requests call the GPIO override path if the pin supports it.

## State And Persistence
The key software state is `mux_log`, which prevents two groups from programming the same IOMUX field to different alternate values. Hardware mux state persists in `base0` group mux registers and `base1` GPIO override registers. The driver does not restore state across suspend/resume itself; it relies on normal pinctrl reapplication if needed.

## Dependencies And Integration Points
Depends on Linux pinctrl, pinmux, pinconf-generic group DT mapping, pinctrl-utils, platform MMIO resources, and any ASIU GPIO controller that requests GPIO override through pinctrl GPIO ranges. It binds to `brcm,cygnus-pinmux`.

## Risks
The conflict detection only tracks IOMUX field reuse after this driver starts; it does not read initial hardware state. `CYGNUS_NUM_IOMUX` must cover every static mux field. GPIO override supports only selected pins and returns `-ENOTSUPP` otherwise. `cygnus_gpio_disable_free()` logs with `dev_err`, which may be noisy for normal free paths.

## Test Signals
Apply DT states for shared mux fields with same and conflicting alternates to verify conflict handling. Test major groups: SPI, UART, SDIO, NAND, LCD, camera, smartcard, PWM, key, CAN, USB overcurrent, and GPIO override-capable pins. Confirm two MMIO resources are present and pinctrl registers at arch init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-cygnus-mux.c -->
