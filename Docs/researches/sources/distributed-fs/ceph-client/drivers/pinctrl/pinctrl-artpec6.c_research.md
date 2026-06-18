# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-artpec6.c

Purpose: Implements the Axis ARTPEC-6 pin controller. It provides static pin/group/function tables, mux selection for peripheral groups, and generic pinconf support for bias and drive strength.

Important APIs and functions: `artpec6_pmx_reg_offset()` maps pin numbers across register holes. Pinctrl callbacks expose groups. Pinmux callbacks are `artpec6_pmx_get_functions_count()`, `artpec6_pmx_get_fname()`, `artpec6_pmx_get_fgroups()`, `artpec6_pmx_set()`, and `artpec6_pmx_request_gpio()`. Pinconf callbacks are `artpec6_pconf_get()`, `artpec6_pconf_set()`, and `artpec6_pconf_group_set()`. Probe/reset paths are `artpec6_pmx_reset()`, `artpec6_pmx_probe()`, and `artpec6_pmx_remove()`.

Control flow: Probe maps MMIO, resets every pin drive field to 8 mA, fills driver data from static tables, and registers the pinctrl descriptor. DT mapping is delegated to `pinconf_generic_dt_node_to_map_all()`. Setting a mux iterates the selected group's pins, skips pins above `ARTPEC6_MAX_MUXABLE` because they lack a select field, computes config 0 for GPIO or the group's configured alternate value, updates the `SEL` field, and leaves nonmuxable pins unchanged. Pinconf get/set reads the per-pin register and manipulates `UDC0/UDC1` for pull-up/down/disable and `DRV` for 4/6/8/9 mA.

State and persistence: Runtime state is `struct artpec6_pmx`, holding device, pinctrl device, MMIO base, and static table pointers/counts. Hardware state is held in per-pin registers and persists until reset or later pinctrl operations. There is no explicit PM save/restore path.

Dependencies and integration points: Integrates with OF compatible `axis,artpec6-pinctrl`, pinctrl core, pinmux, generic pinconf DT parsing, and pinctrl utility map freeing. The driver is registered with `arch_initcall()`.

Risks: `artpec6_pconf_get()` checks `pin >= pmx->num_pins` but then logs `pmx->pins[pin].name`, which would be out of bounds on invalid input. Several function group arrays mention names not present in `artpec6_pin_groups` (`uart4grp1`) or use unusual naming (`uart5nocts`), so table consistency matters. There is no locking around MMIO read-modify-write operations.

Test signals: Probe on matching DT, mux selection for GPIO and each peripheral group, pinconf bias disable/pull-up/pull-down, drive strength 4/6/8/9 mA and invalid values, nonmuxable pin handling, and debugfs generic pinconf output are useful validation points.
