# sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.h

## Purpose

`longhaul.h` is the VIA-specific data contract used by `longhaul.c`. It defines the MSR bitfield layouts for LongHaul/BCR2 control and provides static multiplier, EBLCR decode, and voltage ID lookup tables for multiple VIA C3 generations and VRM schemes.

## Important APIs, types, and functions

- `union msr_bcr2` describes the BCR2 software bus-frequency fields used by LongHaul v1, especially `ESOFTBF` and `CLOCKMUL`.
- `union msr_longhaul` describes LongHaul/PowerSaver MSR fields for revision key, soft bus ratio, soft VID, FSB select, max/min ratio, and voltage limits.
- `samuel1_mults`, `samuel1_eblcr`, `samuel2_eblcr`, `ezra_mults`, `ezra_eblcr`, `ezrat_mults`, `ezrat_eblcr`, `nehemiah_mults`, and `nehemiah_eblcr` map 4-bit or 5-bit hardware encodings to multipliers expressed as ratio times 10.
- `struct mV_pos`, `vrm85_mV`, `mV_vrm85`, `mobilevrm_mV`, and `mV_mobilevrm` map voltage IDs to millivolts and reverse VID encodings.

## Control flow and integration

The header has no runtime control flow. `longhaul_cpu_init()` copies the appropriate multiplier and EBLCR arrays into mutable driver arrays after identifying CPU model and stepping. `longhaul_get_cpu_mult()` decodes the current EBLCR value through the copied `eblcr` table. `longhaul_get_ranges()` builds the cpufreq table from the copied `mults` table. `longhaul_setup_voltagescaling()` uses the VRM tables to convert CPU-reported VID fields into voltage steps and to embed VID values into cpufreq `driver_data`.

## State and persistence behavior

The arrays are static constant source data and do not mutate. Persistent runtime state lives in `longhaul.c`, which copies the selected arrays so it can use one transition path for all CPU variants. The union definitions mirror MSR persistence but do not own state themselves.

## Dependencies

The header depends on compiler bitfield layout matching the driver's intended x86 little-endian MSR interpretation and on `longhaul.c` selecting the correct table for CPU model/stepping. It is tightly coupled to VIA C3 hardware documentation and to cpufreq table construction in `longhaul.c`.

## Risks and edge cases

- Table values marked `-1` represent reserved encodings; missing checks in callers would allow invalid multiplier programming.
- Some table comments document hardware quirks and alternate meanings; changing one table can affect both decode and write paths differently.
- The MSR bitfield names include reserved fields and a spelling typo in `Reseved`; this is harmless but underscores that the layout must not be casually reordered.
- Voltage reverse maps must remain consistent with `struct mV_pos` entries or staged voltage scaling will write the wrong VID.

## Test signals

Static validation should compare all multiplier and VID tables against VIA datasheets. Runtime signals come from `longhaul.c`: correct table selection for each CPU stepping, no reserved current multiplier, sorted frequency table generation, and safe voltage logs showing expected VID per frequency.
