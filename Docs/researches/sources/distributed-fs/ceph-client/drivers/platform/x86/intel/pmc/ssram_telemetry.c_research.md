# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.c

Purpose: PCI driver that discovers PMC SSRAM telemetry headers, records PMC device IDs and PWRM bases for the PMC core driver, and registers PMT telemetry DVSEC regions with Intel VSEC.

Important APIs/types/functions: `pmc_ssram_telemetry_add_pmt()` reads a DVSEC header from SSRAM and calls `intel_vsec_register()` with telemetry capability. `get_base()` reads aligned 64-bit base fields and masks low attribute bits. `pmc_ssram_telemetry_get_pmc()` maps SSRAM headers for main/IOE/PCH PMCs, extracts PWRM base and device ID, stores them in `pmc_ssram_telems`, and registers PMT telemetry. Exported `pmc_ssram_telemetry_get_pmc_info()` returns cached info to `core.c`.

Control flow: PCI probe allocates the telemetry array, enables the device, discovers the main PMC, then best-effort discovers IOE and PCH PMCs from offsets in the main SSRAM header. At probe finish it publishes `device_probed=true` with a write barrier. Consumers calling before probe finishes receive `-EAGAIN`, which `generic_core_init()` converts to probe defer.

State and persistence: static `pmc_ssram_telems` points to devm-managed per-PMC info and static `device_probed` gates reads. The array persists for the PCI device lifetime. Registered VSEC telemetry devices become integration points for PMT telemetry consumers.

Dependencies and integration points: depends on PCI, `linux/intel_vsec.h`, SSRAM offsets, PMC device IDs from `core.h`, and `INTEL_VSEC` namespace. `core.c` consumes this through `pmc_ssram_telemetry_get_pmc_info()` for multi-PMC mapping.

Risks: `device_probed` is global and there is no remove callback resetting it, so this assumes one relevant device lifetime. Secondary PMC discovery errors are ignored by probe, so missing IOE/PCH may be silent. DVSEC parsing from firmware/hardware-provided SSRAM must be correct or PMT telemetry registration will be wrong. Memory barriers protect publication but not broader multi-device scenarios.

Test signals: on supported MTL/ARL/LNL/PTL/WCL PCI IDs, probe should enable the device, expose PMT telemetry through VSEC, and allow `intel_pmc_core` SSRAM init without `-EPROBE_DEFER`. Missing secondary PMCs should not fail probe. Invalid early consumer ordering should result in deferred PMC core probe.
