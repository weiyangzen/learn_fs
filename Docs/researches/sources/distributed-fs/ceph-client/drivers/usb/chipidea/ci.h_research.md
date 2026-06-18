# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci.h

Purpose: defines the common ChipIdea controller model, register map indices, role-driver interface, endpoint representation, MMIO helpers, role conversion helpers, and internal function prototypes.

Important APIs/types/functions: key types are `struct ci_hw_ep`, `enum ci_role`, `enum ci_revision`, `struct ci_role_driver`, `struct hw_bank`, and `struct ci_hdrc`. Important helpers include `ci_role`, `ci_role_start`, `ci_role_stop`, `ci_role_to_usb_role`, `usb_role_to_ci_role`, `hw_read_id_reg`, `hw_write_id_reg`, `hw_read`, `hw_write`, `hw_test_and_clear`, `hw_test_and_write`, and `ci_otg_is_fsm_mode`.

Control flow: inline role start validates role availability, invokes role callback, records `ci->role`, and signals legacy USB PHY events. Role stop marks `CI_ROLE_END`, invokes stop, and clears PHY events. MMIO helpers apply read-modify-write masks and optionally use the i.MX28 SWP write workaround.

State and persistence: `struct ci_hdrc` persists all controller state: locks, mapped register bank, IRQ, role table/current role, OTG FSM timers/workqueue, DMA pools, gadget endpoints and control transfer state, platform data, PHYs, HCD, extcon event flags, quirks, runtime PM flags, low-power flags, revision, and mutex.

Dependencies and integration: shared by core, host, gadget, OTG, debug, trace, and SoC glue code; bridges Linux gadget, host, OTG FSM, role-switch, ULPI, PHY, and platform data APIs.

Risks: `ci_role()` uses `BUG_ON` for invalid role state, so callers must guard role transitions carefully. Register helper masks use `~mask` semantics that assume nonzero masks. Shared state is protected by a mix of spinlock and mutex depending on IRQ versus role-switch context.

Test signals: compile all role combinations; exercise role transitions, register helpers on i.MX28 and normal MMIO paths, OTG FSM enablement, and PM paths touching `in_lpm` and wakeup flags.
