<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c

## Purpose
Placeholder Coffee Lake ACPI match definitions for Intel ASoC/SOF machine selection.

## APIs, Types, and Functions
Exports empty sentinel-only arrays `snd_soc_acpi_intel_cfl_machines[]` and `snd_soc_acpi_intel_cfl_sdw_machines[]`.

## Control Flow, State, and Persistence
No runtime control flow or persistent state exists. The empty arrays allow generation-specific lookup code to reference Coffee Lake tables even when no board-specific matches are listed.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the Intel match aggregate. Platform code can iterate these arrays and simply terminate on the first zero entry.

## Risks and Test Signals
Risks are mainly omission risks: Coffee Lake boards requiring non-HDA/non-generic matches will not bind through these arrays. Test signals are build/export success and fallback to other generic/HDA machine selection where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c -->
