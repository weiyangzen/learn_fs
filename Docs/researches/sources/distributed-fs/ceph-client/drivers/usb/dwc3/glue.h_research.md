# sources/distributed-fs/ceph-client/drivers/usb/dwc3/glue.h

Purpose: defines the public interface used by platform glue drivers to probe, remove, suspend/resume, and optionally sequence DWC3 core, host, gadget, PHY suspend, and port-capability setup themselves.

Important APIs/types/functions: `struct dwc3_properties` carries software-managed core properties such as `gsbuscfg0_reqinfo` and `needs_full_reinit`; `DWC3_DEFAULT_PROPERTIES` supplies defaults. `struct dwc3_probe_data` packages a DWC3 context, MMIO resource, clock/reset ignore flags, `skip_core_init_mode`, and properties for `dwc3_core_probe`. The header declares `dwc3_core_probe/remove`, runtime/system PM callbacks, `dwc3_core_init/exit`, `dwc3_host_init/exit`, `dwc3_gadget_init/exit`, `dwc3_enable_susphy`, and `dwc3_set_prtcap`.

Control flow: normal glue drivers call `dwc3_core_probe` and let the core initialize the selected role. Glue drivers using `skip_core_init_mode` must explicitly call `dwc3_core_init`, select a port capability with `dwc3_set_prtcap`, initialize exactly one role with host or gadget init, then unwind in reverse order.

State and persistence: the header does not own state, but its structs control persistent core initialization choices and role-transition state stored in `struct dwc3`, including current role and low-power PHY settings.

Dependencies and integration: includes `core.h` and Linux types. It is consumed by platform-specific DWC3 wrappers that manage clocks, resets, power domains, USB role switches, and SoC-specific mode sequencing outside generic core code.

Risks: misuse of `skip_core_init_mode` can initialize host/gadget before the core is ready, initialize both roles simultaneously, or leave SUSPHY/PRTCAP inconsistent during role switches. The comment says "finial" but the semantics are clear. Glue drivers that ignore clocks/resets must fully own those resources.

Test signals: platform probe/remove tests, runtime PM cycling, system suspend/resume, role-switch transitions, and wakeup-capable platforms validate this contract. Failures show as missing xHCI/gadget registration, bad role mode, PHY suspend problems, or resource leaks on remove.
