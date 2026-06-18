# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.h

## Purpose
`ice_dpll.h` declares the driver-private DPLL data model and public DPLL initialization hooks for the Intel ice driver. It defines CGU/SynCE register bitfields, software pin indexing, per-pin state containers, per-DPLL device containers, and the aggregate `struct ice_dplls` stored on the PF.

## Important APIs, Types, and Functions
- `ICE_DPLL_RCLK_NUM_MAX` bounds recovered clock parent state arrays to four entries.
- `ICE_CGU_R10`, `ICE_CGU_R11`, and related masks describe SynCE recovered clock selection/divider/reset fields used by the E825C path in `ice_dpll.c`.
- `ICE_CGU_BYPASS_MUX_OFFSET_E825C` maps E825C port numbers into bypass mux selector values.
- `enum ice_dpll_pin_sw` defines the two software-controlled logical pin slots shared by SMA and U.FL arrays.
- `struct ice_dpll_pin_work` carries DPLL pin create/delete notifier work into the single-thread workqueue.
- `struct ice_dpll_pin` stores the Linux `dpll_pin`, PF back pointer, reference tracker, fwnode/notifier fields, hardware index, parent map, cached flags/state/frequency/phase data, logical software-pin backing input/output pointers, direction, status, ref-sync mapping, and visibility flags.
- `struct ice_dpll` stores one DPLL device instance, including Linux `dpll_device`, PF back pointer, reference tracker, hardware DPLL index, active input indices, cached lock mode/status, priorities, phase offset monitor period, active/previous input pins, and registered ops pointer.
- `struct ice_dplls` aggregates the DPLL subsystem state on a PF: kthread worker, delayed work, software workqueue, mutex, initialization completion, EEC/PPS DPLLs, input/output/SMA/U.FL/rclk pins, counts, CGU metadata, phase limits, periodic counter, and generic pin layout flag.
- Public functions `ice_dpll_init()` and `ice_dpll_deinit()` are real declarations when `CONFIG_PTP_1588_CLOCK` is enabled and inline no-ops otherwise.

## Control Flow
The header itself has no executable control flow beyond the `CONFIG_PTP_1588_CLOCK` compile-time gate. Runtime control flow is defined by consumers in `ice_dpll.c`, which allocate and fill the structures declared here during PF initialization, expose them through DPLL netlink callbacks, and free them during PF teardown.

## State and Persistence Behavior
All structures define in-memory PF lifetime state. Cached values mirror hardware CGU state and DPLL subsystem registrations but are not persisted to disk. Register masks describe persistent hardware registers, while the struct fields track current driver ownership and cached observations until deinit or reset.

## Dependencies and Integration Points
The header includes `ice.h` and depends on kernel DPLL types such as `struct dpll_pin`, `struct dpll_device`, `dpll_tracker`, `struct dpll_pin_properties`, `enum dpll_pin_direction`, `enum dpll_lock_status`, and `enum dpll_mode`. It also depends on kernel workqueue, completion, mutex, fwnode, and notifier types through included driver/kernel headers. It is consumed by the ice PF initialization/teardown path and DPLL implementation.

## Risks and Edge Cases
- Fixed-size arrays such as `parent_idx`, `flags`, and `state` must remain consistent with hardware parent counts; callers must validate counts before indexing.
- `struct ice_dpll_pin` has multiple ownership modes: direct DPLL pin, hidden backing pin, logical software pin, and fwnode parent pin. Misinterpreting those fields can lead to double unregisters or missed reference drops.
- Inline no-op behavior when PTP clock support is disabled means callers must not assume DPLL side effects exist in all builds.
- The `generic` flag in `struct ice_dplls` affects whether software pins and output pin resources are registered; future code must preserve that distinction.

## Test Signals
- Compile both with and without `CONFIG_PTP_1588_CLOCK` to verify call sites tolerate real and no-op DPLL hooks.
- Static analysis should focus on array bounds for `ICE_DPLL_RCLK_NUM_MAX`, `num_parents`, and DPLL index-based `state[]` access.
- Probe/remove tests should verify every tracked `dpll_tracker` and fwnode reference is balanced.
