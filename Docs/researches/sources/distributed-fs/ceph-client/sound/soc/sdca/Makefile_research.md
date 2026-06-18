# sources/distributed-fs/ceph-client/sound/soc/sdca/Makefile

## Purpose
Build recipe for the SDCA ASoC library, class SoundWire driver, and auxiliary class function driver.

## APIs, Types, and Functions
Defines `snd-soc-sdca-y` with common parser/device/function-device/regmap/ASoC/UMP objects, conditionally adds HID, interrupt/jack, and FDL objects, then builds `snd-soc-sdca.o`. Defines separate `snd-soc-sdca-class.o` from `sdca_class.o` and `snd-soc-sdca-class-function.o` from `sdca_class_function.o`.

## Control Flow, State, and Persistence
No runtime state. Build-time object composition determines which exported `SND_SOC_SDCA` namespace helpers are available to class and external drivers.

## Dependencies and Integration
Follows the Kconfig symbols in the same folder. It integrates shared library objects with class driver modules that import the SDCA namespace.

## Risks and Test Signals
Risks are missing object inclusion for feature symbols, namespace/link errors when optional pieces are selected, and unused object builds if Kconfig dependencies drift. Test signals are module link tests for `SND_SOC_SDCA`, `SND_SOC_SDCA_CLASS`, and `SND_SOC_SDCA_CLASS_FUNCTION` combinations.
