# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-plat.c

Purpose: Implements the generic Cadence CDNS3 platform core driver that binds named resources, powers PHYs, initializes the common DRD core, wires gadget initialization, and handles runtime/system PM.

Important APIs, types, and functions: `cdns3_plat_probe` allocates `struct cdns`, collects `host`, `peripheral`, and `otg` IRQ/memory resources, obtains optional wakeup IRQ and USB2/USB3 PHYs, powers PHYs, assigns `cdns->gadget_init = cdns3_gadget_init`, and calls `cdns_init`. `cdns3_plat_remove` tears this down. PM helpers `cdns3_controller_suspend/resume`, runtime callbacks, and system sleep callbacks coordinate PHY power, platform suspend hooks, core suspend/resume, wakeup IRQs, and low-power flags.

Control flow: Probe initializes resources and PHYs before entering common core initialization. Runtime suspend calls optional platform glue suspend, powers off PHYs, and marks `cdns->in_lpm`. Resume reinitializes PHYs if power was lost, powers PHYs back on, calls optional platform resume hook, resumes core state under lock, and re-enables wakeup IRQ if one was consumed.

State and persistence behavior: Runtime state is `struct cdns`, PHY states, runtime PM state, `in_lpm`, and wakeup flags. No persistent storage exists. PM state survives only across suspend cycles in memory and hardware registers.

Dependencies and integration points: Consumes platform resources from DT or PCI wrapper, optional `cdns3_platform_data` from SoC glue, Linux PHY APIs, runtime PM, `core.h`, `drd.h`, and `gadget-export.h`. Compatible is `cdns,usb3`.

Risks: Error paths must unwind PHY init/power in the right order. Runtime PM is forbidden unless platform quirks allow default runtime PM, which can surprise platforms expecting autosuspend. Resume after power loss depends on `cdns_power_is_lost` and PHY reinit correctness. Locking spans `cdns_resume` and wakeup flag updates.

Test signals: Probe error injection for missing named resources/IRQs/PHYs, host-only/gadget-only/dual-role operation, runtime autosuspend/resume, system suspend with wakeup IRQ, power-loss resume, PCI wrapper resources, and DT resource naming.
