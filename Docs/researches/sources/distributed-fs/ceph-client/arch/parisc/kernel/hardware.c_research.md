# sources/distributed-fs/ceph-client/arch/parisc/kernel/hardware.c

## Purpose

`hardware.c` is a boot-time PA-RISC hardware identification database. It maps firmware hardware IDs to human-readable device names and maps CPU hversion model bits to PA-RISC CPU type enums and ISA version strings.

## Important APIs, Types, And Functions

`hp_hardware_list[] __initdata` is a large table of `struct hp_hardware` entries. Each row keys on `hw_type`, `hversion`, `sversion`, and hardware revision to name processors, bus adapters, direct I/O devices, DMA devices, FIO devices, memory controllers, management controllers, and miscellaneous platform devices.

`hp_cpu_type_mask_list[] __initdata` maps masked hversion model values to `enum cpu_type`. `cpu_name_version[][]` maps each `enum cpu_type` to a CPU marketing name and architecture version string.

`parisc_hardware_description()` searches `hp_hardware_list` for an exact hardware ID match and returns a fallback generic name for unknown processors, some direct devices, and memory. `parisc_get_cpu_type()` interprets the `PDC_MODEL_INFO` hversion by shifting to model bits, applying mask rows in order, and panicking if no CPU type is known.

## Control Flow

Device registration code calls `parisc_hardware_description()` during boot after firmware inventory has produced `struct parisc_device_id` values. The function performs a linear scan until the `HPHW_FAULTY` sentinel. If no exact row matches, it switches on `hw_type` for generic fallbacks and otherwise reports `unknown device`.

CPU setup calls `parisc_get_cpu_type()` with the hversion returned by firmware. The function linearly scans mask rows and returns the first matching CPU type. The table order matters for overlapping masks, as seen in the dense PCX/PCXU/PCXW ranges.

## State And Persistence Behavior

The hardware and CPU mask tables are `__initdata`, so they are intended to be discarded after initialization. The exported `cpu_name_version` table remains available for later CPU reporting. There is no persistent state or runtime mutation.

## Dependencies And Integration Points

The file depends on `asm/hardware.h` for `struct hp_hardware`, `struct parisc_device_id`, hardware type constants, and `enum cpu_type`. It is used by PA-RISC bus/device registration and CPU initialization paths to turn firmware identifiers into operator-readable descriptions and CPU feature classes.

## Risks

The table is manually curated and exact-match driven. Missing rows cause generic names, while wrong rows can mislabel hardware and confuse driver diagnostics. The CPU mask table affects CPU feature selection; a bad mask or wrong row order can select the wrong architecture class or panic on valid machines. Because the main database is `__initdata`, no late code should retain pointers into returned table strings unless the string storage remains valid for the caller's lifetime.

## Test Signals

Useful signals are boot logs showing accurate model and device descriptions, correct `/proc/cpuinfo` CPU family/version output, successful boot across representative PA1.1 and PA2.0 systems, and no panic from `parisc_get_cpu_type()` on supported hversions.
