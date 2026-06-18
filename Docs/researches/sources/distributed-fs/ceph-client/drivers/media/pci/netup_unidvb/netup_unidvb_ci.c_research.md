# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_ci.c

Purpose: Implements EN50221 common-interface/CAM support for the NetUP Universal Dual DVB-CI PCIe card. It maps two CAM slots into BAR1 windows, exposes the DVB CA callbacks needed by `dvb_ca_en50221`, and acknowledges CI-related interrupts from the bridge.

Important APIs, types, and functions: `netup_ci_interrupt()` clears CI interrupt status with `CAM_CTRLSTAT_CLR`. `netup_unidvb_ci_register()` initializes one `struct netup_ci_state`, fills `struct dvb_ca_en50221` callbacks, points attribute and I/O windows at slot-specific BAR1 offsets, calls `dvb_ca_en50221_init()`, and enables `NETUP_UNIDVB_IRQ_CI`. `netup_unidvb_ci_unregister()` releases the CA state. Callback functions include `netup_unidvb_ci_read_attribute_mem()`, `netup_unidvb_ci_write_attribute_mem()`, `netup_unidvb_ci_read_cam_ctl()`, `netup_unidvb_ci_write_cam_ctl()`, `netup_unidvb_ci_slot_reset()`, `netup_unidvb_ci_slot_ts_ctl()`, and `netup_unidvb_poll_ci_slot_status()`.

Control flow: Registration is per slot and is called by the core after DVB adapters are registered. Runtime DVB CA operations are direct MMIO byte accesses into the configured slot windows. Slot reset asserts `BIT_CAM_RESET`, waits up to five seconds for `BIT_CAM_READY`, and retries three times before returning success regardless of final readiness. Status polling reads `CAM_CTRLSTAT_READ_SET` and reports present/ready flags to the DVB CA layer. TS enable clears the CAM bypass bit so transport stream data is routed through the CAM.

State and persistence: Software state is held in `dev->ci[num]`: slot number, device pointer, BAR1 config and I/O bases, cached status, and the CA callback object. Hardware CAM state lives in bridge control registers and CAM memory windows and persists only while the card remains powered/configured.

Dependencies and integration points: Depends on `netup_unidvb.h` definitions, the core driver's BAR mappings and frontend adapters, Linux MMIO helpers, and the DVB CA EN50221 framework. Interrupt dispatch is owned by `netup_unidvb_core.c`, which calls `netup_ci_interrupt()` when `NETUP_UNIDVB_IRQ_CI` is reported.

Risks: Reset timeout does not return an error if the CAM never becomes ready, so upper layers can see a successful reset with a nonready slot. Attribute/control memory accesses do not validate `slot` or `addr` beyond the CA framework's expectations. Interrupt clearing uses a fixed `0x101` mask and assumes both slots/bridge bits match that value. There is no locking around CAM window accesses in this file.

Test signals: Useful validation includes probing both CI slots, polling with absent, present, and ready CAM states, reset timeout behavior, TS bypass bit transitions for slot 0 and slot 1 shift handling, unregister/re-register cleanup, and interrupt acknowledgment observed through `REG_ISR`/`CAM_CTRLSTAT` traces.
