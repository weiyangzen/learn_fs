# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzt2h.c

## Purpose

`pinctrl-rzt2h.c` is the pinctrl, GPIO, pinconf, and optional GPIO IRQ driver for Renesas RZ/T2H and RZ/N2H-family SoCs. It is based on the RZ/G2L driver but adapted for a different register layout, 64-bit PFC/DRCTL registers, optional safety-region ports, and a fixed GPIO-to-parent-IRQ mapping table. It supports compatibles `renesas,r9a09g077-pinctrl` and `renesas,r9a09g087-pinctrl`.

## Important APIs, Types, And Functions

`struct rzt2h_pinctrl_data` supplies the number of pins, per-port valid-pin bitmasks, and port count. `struct rzt2h_pinctrl` owns pinctrl and GPIO descriptors, two optional MMIO bases (`base0` normal/security and `base1` safety), a bitmap of used parent IRQs, register lock, DT group/function mutex, safety-port flag, and wakeup-path counter.

The register helpers `RZT2H_GET_BASE()` and generated `rzt2h_pinctrl_read/write{b,w,q}()` route accesses to the correct MMIO base based on port number. `rzt2h_validate_pin()` rejects out-of-range pins, disabled safety ports, and pins absent from the SoC bitmask. `rzt2h_pinctrl_set_pfc_mode()` performs safe mux switching by forcing Hi-Z, enabling GPIO temporarily through `PMC`, writing the 8-bit function field in `PFC`, and returning the pin to peripheral mode.

Pinconf support uses the `DRCTL` register. `rzt2h_pinctrl_pinconf_get()` and `_set()` support slew-rate, bias-disable/pull-up/pull-down, Schmitt input, and drive-strength-uA using the fixed table `{2500, 5000, 9000, 11800}`. GPIO callbacks implement request/free, direction, value get/set, and mode switching. IRQ support is provided by `rzt2h_gpio_irq_map`, `rzt2h_gpio_child_to_parent_hwirq()`, `rzt2h_gpio_irq_domain_free()`, and parent-forwarding irqchip callbacks.

## Control Flow

Probe allocates state, loads match data, maps the required `nsr` region, optionally maps the `srs` region, selects safety region `0x812c0xxx` by clearing `RSELP` for safety ports when `srs` is present, initializes locks, and registers pinctrl plus GPIO. Registration builds one pin descriptor per possible GPIO name, registers/enables pinctrl, then registers a GPIO chip after validating `gpio-ranges`.

DT mapping is similar to the RZ/G2L pattern: a node contains either `pinmux` cells or a `pins` string list. `pinmux` cells encode a pin ID and an 8-bit function. The parser dynamically creates one generic group and one generic function per mux node and optionally adds a config map. `pins` nodes are config-only and require at least one generic pinconf property.

Mux set validates every requested pin and writes the PFC sequence. GPIO request also validates and switches the line to GPIO mode. Direction writes update two-bit `PM` fields; output writes update `P`; input reads come from `PIN`, output reads from `P`. `get_direction()` has special handling for interrupt function mode because an IRQ line is not in GPIO mode but must still report as input to gpiolib.

IRQ translation is optional and enabled only if the DT node has `interrupt-controller`. Child lines index into `rzt2h_gpio_irq_map`; invalid entries and parent IRQs below `RZT2H_INTERRUPTS_START` are rejected. A parent IRQ can be used by only one child at a time through `used_irqs`. The child is muxed to `PFC_FUNC_INTERRUPT`, parent type is inherited from the child request, and wake enable increments `wakeup_path`. Domain free clears the used bit and disables GPIO mode for the pin.

## State And Persistence

The driver persists no state across reboot and has minimal system PM handling. Hardware state lives in `P`, `PM`, `PMC`, `PFC`, `PIN`, `DRCTL`, and `RSELP`. Runtime state includes the generated pinctrl structures, `used_irqs`, `safety_port_enabled`, and `wakeup_path`. `rzt2h_pinctrl_suspend_noirq()` only marks the device as a wakeup path when needed; unlike RZ/G2L it does not cache and restore registers.

## Dependencies And Integration Points

The driver depends on pinctrl, gpiolib, hierarchical IRQ domain helpers, OF matching, platform resources named `nsr` and optional `srs`, and `dt-bindings/pinctrl/renesas,r9a09g077-pinctrl.h`. It expects a correct `gpio-ranges` tuple and a parent interrupt domain when IRQ support is enabled. It registers at `core_initcall` and suppresses bind attributes.

## Risks

The optional safety-region split means the same logical port can be invalid if `srs` is absent; board DT must match available hardware. `rzt2h_gpio_irq_domain_free()` computes the used IRQ bit from the child hwirq, while allocation sets it from the parent IRQ number; this deserves close review because child offsets and parent IRQ IDs are different namespaces. The fixed IRQ map has many zero entries and shared parent IRQs, making off-by-one or reuse bugs high impact. Lack of full suspend/resume restore means firmware or low-power states that reset PFC/GPIO registers may lose pin state.

## Test Signals

Exercise probe with and without `srs`, mux states on safety and non-safety ports, config-only `pins` nodes, invalid sparse pins for `r9a09g087`, GPIO direction/value operations, IRQ allocation conflicts for shared parent IRQs, IRQ free/reallocate, wake-enabled IRQ suspend, and DT validation failures for mismatched `gpio-ranges`.
