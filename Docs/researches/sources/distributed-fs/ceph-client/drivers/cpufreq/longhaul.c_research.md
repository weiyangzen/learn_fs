# sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.c

## Purpose

`longhaul.c` implements the VIA/Centaur C3 LongHaul and PowerSaver cpufreq driver for legacy x86 family 6 processors. It supports LongHaul v1 through `MSR_VIA_BCR2`, LongHaul v2 through `MSR_VIA_LONGHAUL`, and PowerSaver through the same LongHaul MSR with optional voltage scaling. The driver is deliberately opt-in through the `enable` module parameter because unsafe motherboard/interrupt/APIC combinations can freeze the machine.

## Important APIs, types, and functions

- `longhaul_get_cpu_mult()`, `calc_speed()`, and `guess_fsb()` translate hardware multiplier encodings and guessed FSB values into kHz.
- `do_longhaul1()` programs BCR2 software clock multiplier changes and invokes halt.
- `do_powersaver()` programs bus ratio and optional VID changes through `MSR_VIA_LONGHAUL`, using either halt or ACPI C3 I/O reads to trigger transitions.
- `longhaul_setstate()` is the core transition path. It masks PIC interrupts, waits for PCI bus master idle, disables bus arbitration through ACPI or VIA northbridge support, performs the MSR transition, restores arbitration/interrupt masks, verifies the multiplier, and retries with errata fallbacks.
- `longhaul_get_ranges()` builds the cpufreq table from model-specific multiplier tables.
- `longhaul_setup_voltagescaling()` reads VID bounds, selects VRM 8.5 or Mobile VRM tables, annotates table rows with VID data, and enables staged voltage scaling.
- `longhaul_cpu_init()` detects CPU model/stepping, selects multiplier tables from `longhaul.h`, discovers ACPI C3/northbridge support, builds the table, and installs policy data.

## Control flow

`late_initcall(longhaul_init)` first requires a Centaur family 6 CPU, the `enable` parameter, UP operation, and no APIC configuration known to be broken. CPU init maps model and stepping to Samuel, Samuel2, Ezra, Ezra-T, or Nehemiah behavior, copies the right multiplier/EBLCR tables, validates LongHaul v2 availability, initializes southbridge and ACPI data, and refuses systems without a safe bus-master/arbitration mechanism.

On target changes, the cpufreq core passes a table index. If voltage scaling is disabled, the driver calls `longhaul_setstate()` once. If voltage scaling is enabled, it walks intermediate table entries one VID step at a time with sleeps between steps, because large voltage jumps were observed to power off boards. `longhaul_setstate()` decides whether voltage must rise before frequency, performs low-level transition, then verifies the actual multiplier. If verification fails, it may enable the revision-key erratum workaround, disable ACPI C3, or downgrade v2 to v1 before retrying.

## State and persistence behavior

Global state tracks CPU model, LongHaul version, FSB, speed bounds, current table index, voltage-scaling tables, ACPI processor/C3 data, ACPI register address, and safety flags. `longhaul_table` is dynamically allocated during CPU init and freed on module exit. Exit attempts to return to the maximum multiplier before unregistering. Hardware state persists in LongHaul/BCR2 MSRs, chipset arbitration registers, and possibly voltage regulator state.

## Dependencies

The driver depends on x86 MSR access, ACPI processor C-state and bus-master control, PCI discovery of VIA northbridge/southbridge IDs, legacy PIC I/O ports, VIA-specific FADT timer behavior, and multiplier/VID tables from `longhaul.h`. It also depends on accurate boot `cpu_khz` for FSB guessing and on running on a single CPU without IO-APIC.

## Risks and edge cases

- The driver can hang hardware, which is why `enable` is required and SMP/APIC are rejected.
- FSB detection is heuristic for most models; wrong guesses produce invalid frequency tables or unsafe target speeds.
- `bm_timeout` is initialized once before the retry loop, so repeated retry paths inherit decremented timeout state.
- ACPI C3 may claim to work but fail to trigger frequency changes; the driver has fallback retries, but transition failure can still leave hardware at an unexpected rate.
- Voltage scaling relies on VID tables and CPU-reported min/max values; bogus values disable it, but incorrect-but-plausible firmware data remains risky.
- Transition code manipulates PIC masks, ACPI arbiter bits, and northbridge ports directly; interrupts and bus masters are highly sensitive here.

## Test signals

Useful signals are mostly hardware-based: module load should require `enable=1`, build a sorted table with more than one entry, and log selected ACPI/northbridge safety method. Repeated transitions across all table entries should verify actual multiplier after each change, avoid PCI bus timeout warnings, and survive module exit returning to max multiplier. Voltage-scaling validation needs board power stability and temperature/power observation across stepped VID transitions.
