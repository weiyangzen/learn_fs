# sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-processor.c

## Purpose
`xen-acpi-processor.c` uploads ACPI processor power-management data from dom0 to the Xen hypervisor. It sends C-state and P-state information so Xen can manage physical CPU idle and frequency behavior.

## Important APIs, types, and functions
Key functions are `push_cxx_to_hypervisor`, `push_pxx_to_hypervisor`, `xen_copy_pss_data`, `xen_copy_psd_data`, `xen_copy_pct_data`, `upload_pm_data`, `get_max_acpi_id`, `read_acpi_id`, `check_acpi_ids`, `xen_upload_processor_pm_data`, resume work, and module init/exit. Important state includes `nr_acpi_bits`, `acpi_ids_done`, `acpi_id_present`, `acpi_id_cst_present`, `acpi_psd`, and per-CPU `acpi_perf_data`.

## Control flow
Initialization runs only in the Xen initial domain. It sizes bitmaps from Xen physical CPU info, allocates ACPI performance storage, asks ACPI core to preregister performance data, loads per-processor performance info, uploads C/P state data for possible CPUs, walks ACPI namespace to catch physical CPUs not visible as dom0 vCPUs, and registers a syscore resume hook. Resume defers re-upload to a work item because syscore resume context is atomic.

## State and persistence
The driver stores runtime bitmaps of processed and present ACPI IDs, cached PSD packages, and per-CPU performance structures. Uploaded PM state resides in Xen until refreshed or rebooted. The `off` module parameter inhibits hypercalls for testing or disabling upload behavior.

## Dependencies and integration points
It depends on ACPI processor/cpufreq internals, Xen `XENPF_set_processor_pminfo` and `XENPF_get_cpuinfo` platform ops, syscore resume, CPU masks, per-CPU allocations, and dom0 physical CPU enumeration. It intentionally initializes before cpufreq scaling drivers.

## Risks and test signals
Risks include ACPI ID bitmap sizing, virtual CPU vs physical CPU mismatches, malformed ACPI tables, missing P-state components, copy/layout assumptions between ACPI and Xen structures, resume re-upload ordering, and partial allocation cleanup. Test signals include dom0 with limited `xen_max_vcpus`, CPU hotplug-capable ACPI tables, systems with PBLK but no `_CST`, P-state dependency domains, `off=1` dry runs, suspend/resume, and hypercall error handling for invalid ACPI IDs.
