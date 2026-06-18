<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h

Purpose: This header defines Intel SoundWire platform integration: SHIM/ALH register maps, ACE2+ register definitions, ACPI/resource context, DSP callback glue, clock-stop quirks, hardware operation hooks, and public probe/startup/IRQ APIs.

Important APIs/types/functions: Register macros cover SHIM LCAP/LCTL/SYNC/IOCTL/WAKE/CTMCTL, ALH stream config, SHIM2 generic/vendor registers, stream channel maps, and mic privacy support. `sdw_intel_ops` exposes DSP/audio callbacks for stream params/free/trigger. `sdw_intel_ctx` tracks links, MMIO, masks, link list, shared SHIM lock/mask, and peripherals. `sdw_intel_res` supplies platform resources and clock-stop quirks. `sdw_intel_hw_ops` abstracts chip-specific debugfs, link count, DAI registration, power, bus start/stop, wake, bank-switch sync, SDI programming, and BPT operations.

Control flow: Intel initialization is intentionally phased: ACPI scan, allocation/probe, startup/hardware enable, then threaded IRQ handling. Power and clock-stop paths choose among normal start, reset start, clock-stop resume, or teardown based on quirks.

State and persistence: Persistent state lives in context/link objects and shared SHIM/ALH registers. `shim_lock`, `shim_mask`, link masks, and `clock_stop_quirks` protect shared multi-link behavior and wake/sync state.

Dependencies/integration: Depends on ACPI, HDaudio/extended link resources, SoundWire core, ASoC PCM/DAI types, IRQ threading, debugfs, and DSP parent drivers. External hardware op tables are declared for CNL and LNL.

Risks and test signals: Risks include shared-register races, wrong SHIM base for ACE generation, clock-stop quirk misuse that breaks wake-capable slaves, multi-link sync failures, and ALH stream mismatches. Test with ACPI link masks, startup/exit cycles, threaded IRQs, runtime/system suspend, wake events, multi-link bank switch, and DSP params/free/trigger callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_intel.h -->
