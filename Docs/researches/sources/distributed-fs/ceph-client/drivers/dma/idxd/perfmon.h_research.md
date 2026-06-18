# sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.h

Purpose: provides the IDXD perfmon support definitions shared by the PMU implementation. It defines conversions from perf PMU objects back to IDXD objects, event/filter encodings, counter-control constants, and MMIO address macros for the perfmon register table.

Important APIs, types, and macros: inline helpers `event_to_pmu()`, `event_to_idxd()`, and `pmu_to_idxd()` recover `struct idxd_pmu` and `struct idxd_device` from perf core objects. `enum dsa_perf_events` documents high-level DSA categories, while `enum filter_enc` indexes filter register slots. Register helpers include `PERFMON_TABLE_OFFSET()`, `PERFMON_REG_OFFSET()`, `PERFCAP_REG()`, `PERFRST_REG()`, `OVFSTATUS_REG()`, `PERFFRZ_REG()`, `FLTCFG_REG()`, `CNTRCFG_REG()`, `CNTRDATA_REG()`, `CNTRCAP_REG()`, and `EVNTCAP_REG()`. `DEFINE_PERFMON_FORMAT_ATTR()` generates perf sysfs format attributes.

Control flow: this header has no runtime control flow beyond container conversions and macro-generated sysfs show functions. The address macros compose `idxd->reg_base`, `idxd->perfmon_offset`, fixed offsets from `registers.h`, counter index, and filter index. `perfmon.c` uses these helpers for capability probing, counter reset, filter programming, counter reads, overflow clearing, and PMU registration.

State and persistence: no independent state is stored here. The constants define persistent hardware bit meanings such as `CONFIG_RESET`, `CNTR_RESET`, `COUNTER_FREEZE`, `COUNTER_UNFREEZE`, `CNTRCFG_ENABLE`, and `CNTRCFG_IRQ_OVERFLOW`. The macro-generated attributes are static objects in the translation unit that includes the macro.

Dependencies and integration: depends on Linux perf, PCI, DMAengine, cdev, wait, UUID, sbitmap, and IDXD register definitions. It assumes `struct idxd_pmu` contains `struct pmu pmu` and `struct idxd_device *idxd`, as defined in `idxd.h`. It ties the perf PMU ABI strings to `perf_event_attr.config` and `config1` bit layouts consumed by `perfmon.c`.

Risks and test signals: the primary risks are ABI drift between format strings and `union event_cfg`/`union filter_cfg`, incorrect register offset arithmetic, and static attribute-name collisions if used outside its intended file. Test by checking `/sys/bus/event_source/devices/dsa*/format/*`, verifying perf encodes filters into expected registers, probing multiple devices, and validating counter data with known workloads.
