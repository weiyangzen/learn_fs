# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_class_function.c

## Purpose
Auxiliary-bus driver for individual class-compliant SDCA functions. It parses each function, creates function-specific MBQ regmaps, initializes/reset/downloads firmware, exposes the ASoC component and DAIs, manages function IRQs, and connects SoundWire streams to SDCA dataports.

## APIs, Types, and Functions
Registers an auxiliary driver named `sdca_function` with IDs for smart amp, smart mic, UAJ, HID, and RJ functions. Private state is `struct class_function_drv`. Key functions include regmap access callbacks, `class_function_startup()`, `class_function_sdw_add_peripheral()`, `class_function_sdw_remove_peripheral()`, `class_function_sdw_set_stream()`, component probe/remove, `class_function_set_jack()`, `class_function_init_device()`, `class_function_boot()`, `class_function_probe()`, and PM callbacks for runtime and system sleep.

## Control Flow, State, and Persistence
Probe locates the matching short function descriptor by function type, parses full function metadata, builds regmap defaults from DisCo constants/resets, creates a SoundWire MBQ regmap with busy-delay-adjusted retry/timeout values, installs jack support for UAJ/RJ, populates ASoC component/DAI definitions, enables runtime PM, runs the boot sequence, then registers the component. Boot is serialized by the core `init_lock`: it reads function status, resets or writes initialization table if status bits require it, registers early FDL IRQs, runs FDL sync, writes defaults, and clears function status. Stream `hw_params` converts ALSA params into SoundWire stream/port config, resolves the SDCA port, adds the slave to the SoundWire stream, then writes SDCA cluster/clock/usage controls. Runtime suspend sets function regmap cache-only; runtime resume clears cache-only, optionally reinitializes after system suspend, re-enables early/full IRQs, reruns FDL, clears status, and syncs cache. System suspend marks `suspended`, resumes the device to disable IRQs, then force-suspends runtime PM.

## Dependencies and Integration
Depends on auxiliary bus, SoundWire stream helpers, ASoC component/DAI APIs, SoundWire MBQ regmap, SDCA parser/regmap/ASoC/FDL/IRQ/jack helpers, and shared core state from `sdca_class.h`. It imports `SND_SOC_SDCA`.

## Risks and Test Signals
Risks include matching only by function type when multiple same-type functions exist, single-port limitation for DAIs, boot failures leaving runtime PM references, duplicated IRQ cleanup in component remove and auxiliary remove paths requiring idempotence, regcache ordering after FDL/default writes, and resume paths depending on `suspended` state. Test signals are auxiliary probes for each supported function type, component/DAI registration from parsed DisCo, FDL-triggered firmware download, stream add/remove with valid SoundWire ports, jack registration for UAJ/RJ, runtime suspend/resume cache sync, and system suspend/resume with IRQ/FDL reinitialization.
