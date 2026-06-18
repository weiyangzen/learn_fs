# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-ich.c

Purpose: provides the Intel SpeedStep CPUFreq driver for mobile Intel processors controlled through ICH2-M/ICH3-M/ICH4-M southbridge power-management registers. It exposes two states, `SPEEDSTEP_HIGH` and `SPEEDSTEP_LOW`, through a CPUFreq table.

Important APIs and functions: `speedstep_detect_processor()` and `speedstep_get_freqs()` come from `speedstep-lib`. Local setup finds the ICH LPC/PM PCI device in `speedstep_detect_chipset()`, enables SpeedStep registers in PCI config offset `0xa0`, reads PMBASE from config offset `0x40`, and uses `speedstep_set_state()` to toggle bit 0 at `pmbase + 0x50` while temporarily disabling bus-master arbitration at `pmbase + 0x20`. `speedstep_cpu_init()` discovers low/high rates by executing the transition callback on a policy CPU; `speedstep_target()` uses `smp_call_function_single()` to run transitions on an online sibling.

Control flow and state: global state includes the retained PCI device pointer, detected processor enum, PMBASE, and the two-entry frequency table. SMP policy masks are narrowed to topology siblings. Frequency reads are executed on the target CPU through `get_freq_data()` because MSR-derived speed detection is CPU-local.

Dependencies and integration points: depends on Intel PCI IDs, raw port I/O, x86 CPU matching, the shared SpeedStep library, and CPUFreq generic table verification. Module init registers only after CPU, chipset, activation, and PMBASE discovery succeed; exit releases the PCI reference and unregisters CPUFreq.

Risks and test signals: risks include dangerous raw chipset programming, missing `pci_dev_put()` on the `speedstep_find_register()` failure path after chipset detection, fixed offsets for legacy southbridges, Dell Inspiron host-bridge exclusion fragility, and no transition error propagation from the asynchronous target wrapper. Test signals include PMBASE logging, successful low/high frequency discovery with measured latency, no lockups on excluded 82815 revisions, correct sibling policy masks, and pmbase state bit matching the requested CPUFreq index after transitions.
