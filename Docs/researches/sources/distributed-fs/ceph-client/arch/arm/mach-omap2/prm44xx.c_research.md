# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.c

## Purpose
Implements OMAP4/OMAP5/DRA7/AM43xx-style PRM support: PRM MMIO access, VP/VC access, chained PRCM IRQ support, IO wake chain control, reset-source mapping, context-loss helpers, powerdomain operations, AM43xx context save/restore, and PRM registration.

## APIs, Flow, And State
Exports `omap4_prm_vcvp_read/write/rmw()` and `omap44xx_prm_init()`. Static state includes `omap4_prcm_irq_setup`, `omap_prm_context`, and `prm_init_data`. IRQ flow reads each IRQENABLE/IRQSTATUS pair, saves and clears masks during suspend, restores them on resume, and uses IO event priority. IO-chain reconfiguration toggles `WUCLK_CTRL` and waits for `WUCLK_STATUS` assertion/deassertion. Reset-source flow reads the device PRM reset status and maps bits to standard IDs. Powerdomain operations use partitioned `omap4_prminst_*` accessors for next/current/previous power state, logic/memory retention, low-power state changes, transition polling, and context save/restore. AM43xx can save PRM IRQ enable and IO PMCTRL around CPU cluster PM when off mode is enabled.

## Dependencies And Integration
Depends on CPU PM, device-tree IRQ lookup, SoC detection, VP/voltage, PRM instance access, OMAP4/AM43xx register bits, `powerdomain`, and `pm.h` off-mode state. Registers `omap44xx_prm_ll_data` and late-registers the chained IO wake IRQ when `PRM_HAS_IO_WAKEUP` is present.

## Risks And Test Signals
This code adapts multiple SoC families; AM43xx changes IRQ register count and offsets at init time. `prm_restore_context()` mixes OMAP4 and AM43xx instance constants, so context save/restore is tightly coupled to compatible selection. Test signals are OMAP4/5/DRA/AM43xx boot, IO wake interrupts, VP TXDONE handling, powerdomain context restore, AM43xx RTC-DDR/off-mode resume, and reset-source reporting.
