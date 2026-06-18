# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.h

## Purpose

`intel_hfi.h` declares the HFI hooks used by the x86 thermal interrupt/hotplug code and provides no-op stubs when HFI thermal support is not enabled.

## Important APIs, Types, and Functions

The API surface is `intel_hfi_init()`, `intel_hfi_online()`, `intel_hfi_offline()`, and `intel_hfi_process_event()`. Under `CONFIG_INTEL_HFI_THERMAL` these are external declarations; otherwise static inline stubs compile away callers.

## Control Flow

The header contains no runtime flow beyond configuration-conditional no-op behavior. It allows `therm_throt.c` to call HFI hooks unconditionally.

## State and Persistence Behavior

No state is defined in the header. Runtime HFI state lives in `intel_hfi.c` when compiled.

## Dependencies and Integration Points

It integrates x86 thermal interrupt code with optional HFI support without forcing every build to include the HFI implementation.

## Risks and Test Signals

Risks are build-configuration drift and missing declarations if HFI call sites change. Test signals include builds with and without `CONFIG_INTEL_HFI_THERMAL`, CPU hotplug paths compiling with stubs, and HFI interrupt calls compiling under both configurations.
