# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.c

## Purpose

`hw_factory_dce110.c` builds the DCE11.0 GPIO hardware factory. It defines HPD and DDC register tables, shift/mask tables, pin register binding callbacks, and factory function pointers/pin counts.

## Important APIs, Types, And Functions

Important elements are HPD register arrays from `HPD_REG_LIST`, DDC data/clock register arrays, `hpd_shift`, `hpd_mask`, `ddc_shift`, `ddc_mask`, `define_ddc_registers`, `define_hpd_registers`, the `hw_factory_funcs` table, and `dal_hw_factory_dce110_init`.

## Control Flow

Initialization fills `factory->number_of_pins` for DDC data/clock, generic, HPD, GPIO pad, VIP pad, sync, and GSL, then assigns factory funcs. DDC binding switches on `pin->id` to select data or clock register arrays by encoder index and sets base GPIO register pointers. HPD binding sets HPD register/shifts/masks and base GPIO regs.

## State, Dependencies, Risks, And Test Signals

State is written into the caller-provided `struct hw_factory` and individual `hw_gpio_pin`/`hw_ddc`/`hw_hpd` objects. Hardware registers are not programmed here; this file only binds metadata. It depends on DCE11 generated register headers, `reg_helper`, shared GPIO factory/pin classes, and HPD/DDC register macro headers. Risks include array index assumptions for eight DDC pins and six HPD pins, missing generic pin init despite nonzero generic count, and critical assertion on unsupported DDC pin IDs. Tests should create DDC data/clock and HPD pins for all valid indices and verify register pointers and pin counts.
