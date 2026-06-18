<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h

## Purpose
Small header declaring Intel ASoC ACPI SDCA quirk helpers used by SoundWire machine-match tables.

## APIs, Types, and Functions
Declares `bool snd_soc_acpi_intel_sdca_is_device_rt712_vb(void *arg);` and provides an include guard.

## Control Flow, State, and Persistence
No runtime state or logic exists in the header. It defines the compile-time contract for match tables that want to gate entries on RT712-VB SDCA quirk detection.

## Dependencies and Integration
Included by MTL/LNL/PTL match files and implemented by `soc-acpi-intel-sdca-quirks.c`. The declaration intentionally uses `void *` to match the generic machine-check callback shape.

## Risks and Test Signals
Risks include declaration/implementation drift, users forgetting the providing object/namespace, and the opaque argument hiding the required `sdw_intel_ctx` type. Test signals are successful builds of all users and correct runtime selection of SDCA-quirked SoundWire entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h -->
