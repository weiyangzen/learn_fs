# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/crashlog.c

Purpose: implements the Intel PMT crashlog auxiliary driver. It decodes crashlog discovery headers, creates PMT class devices, exposes crashlog control/status sysfs attributes, and allows users to read crashlog buffers through the PMT class bin file.

Important APIs/types/functions: `struct crashlog_status`, `struct crashlog_control`, and `struct crashlog_info` describe version-specific status/control bits. `struct crashlog_entry` embeds `intel_pmt_entry` first and adds a control mutex and selected info. `pmt_crashlog_rmw()` masks trigger bits and writes control, while `pmt_crashlog_rc()` reads status. Sysfs handlers implement `clear`, `consumed`, `enable`, `error`, `rearm`, and `trigger`. `pmt_crashlog_header_decode()` validates type/version, decodes access/GUID/base/size, and attaches the correct attribute group. Probe/remove manage entries for each VSEC resource.

Control flow: auxiliary probe allocates a flexible private structure sized for all VSEC resources and calls `intel_pmt_dev_create()` for each. The namespace decoder skips unsupported crashlog headers by returning positive `1`; hard errors abort and unwind. For supported type 1 version 0 or 2, class creation exposes version-appropriate controls and the binary crashlog region. Remove destroys all created entries and mutexes.

State and persistence: per-entry mutex protects control register writes. Hardware status/control bits persist in the device discovery/control registers. The `crashlog_array` xarray persists namespace IDs until module exit, where it is destroyed.

Dependencies and integration points: depends on auxiliary bus, Intel VSEC, PMT class, PCI/MMIO, sysfs, mutex, and overflow-safe allocation. Imports `INTEL_PMT`. PMT class handles common mapping and bin read/mmap.

Risks: sysfs writes directly alter crashlog hardware state; guards prevent clearing false, consuming incomplete logs, triggering while disabled, and triggering when a log is already complete. Version 0 has combined status/control register while version 2 separates them, so bit masks must be exact. Returning positive `1` for unsupported devices is a convention with `pmt_crashlog_probe()` and class create callers.

Test signals: supported crashlog VSEC resources should create `crashlogN` devices with v0 or v2 attribute sets. Invalid writes should return `-EINVAL`, disabled trigger/consume should return `-EBUSY`, and duplicate trigger should return `-EEXIST`. Remove/reprobe should clean sysfs and xarray entries.
