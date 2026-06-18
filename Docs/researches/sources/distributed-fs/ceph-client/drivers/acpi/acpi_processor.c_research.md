# sources/distributed-fs/ceph-client/drivers/acpi/acpi_processor.c

## Purpose
`acpi_processor.c` handles ACPI processor enumeration and early processor control negotiation. It maps ACPI processor objects/devices to Linux CPU devices, detects duplicate processor IDs, handles CPU hot-add/remove hooks, exposes per-CPU ACPI handles, initializes cpufreq platform devices, processes old PIIX4 errata, and evaluates `_CST` idle-state packages when configured.

## Important APIs, Types, And Functions
It defines per-CPU `processors`, exported `errata`, and helpers such as `acpi_get_processor_handle()`, `acpi_duplicate_processor_id()`, `acpi_processor_init()`, `acpi_processor_claim_cst_control()`, and `acpi_processor_evaluate_cst()`. Key internal functions include `acpi_processor_errata_piix4()`, `acpi_processor_errata()`, `cpufreq_add_device()`, `acpi_pcc_cpufreq_init()`, `acpi_processor_set_per_cpu()`, `acpi_processor_hotadd_init()`, `acpi_processor_get_info()`, `acpi_processor_add()`, `acpi_processor_post_eject()`, `processor_physically_present()`, `_OSC`/`_PDC` setup helpers, duplicate-ID namespace walkers, and processor/container scan handlers.

## Control Flow
Init first walks processor namespace entries and processor device HIDs to record duplicate ACPI IDs, registers the processor scan handler with hotplug support, registers processor container handling, and creates `pcc-cpufreq` if `\_SB.PCCH` exists on x86. Attach allocates `struct acpi_processor`, allocates throttling cpumask storage, reads processor ID from a `Processor` object or device `_UID`, rejects duplicate IDs, maps ACPI/physical IDs to a logical CPU, handles CPU0 fallback for UP systems without MADT entries, creates `acpi-cpufreq` if `_PCT` is present on the first processor, hot-adds a CPU if needed, stores per-CPU mappings, renames the ACPI BID to `CPU%X`, records PBLK throttling data, applies `_SUN` package ID hints, binds the ACPI device to the CPU device, and triggers CPU device driver probe. Hot-eject detaches the CPU driver, unbinds ACPI, unregisters and unmaps the CPU, clears per-CPU state, and tries to offline the NUMA node. `_CST` evaluation parses and validates package contents, maps FFH or system-I/O C-state entry methods, and populates the caller's power-state array.

## State And Persistence
Runtime state is per-CPU ACPI processor pointers, the duplicate-ID arrays, PIIX4 errata flags, processor-device companion bindings, per-processor throttling state, and cpufreq platform devices. Firmware negotiation through `_OSC`, `_PDC`, and `_CST` influences processor idle/performance behavior for the boot.

## Dependencies And Integration Points
It depends on ACPI scan and table helpers, CPU hotplug and device model APIs, architecture CPU mapping/unmapping, PCI for PIIX4 errata, cpufreq platform drivers (`acpi-cpufreq`, `pcc-cpufreq`), processor idle/throttling/performance subdrivers, Xen Dom0 processor presence handling, and namespace-specific exports for `ACPI_PROCESSOR_IDLE`.

## Risks
Processor ID mapping is firmware-sensitive; duplicate or wrong `_UID`/ProcessorID values can reject CPUs or bind the wrong ACPI companion. Hotplug paths must coordinate CPU map locks and ACPI removal locks. `processor_device_array` is intentionally not cleared on some errors for BIOS diagnostics, which can surprise cleanup reasoning. `_CST` parsing must guard malformed packages and hardware-unsupported FFH states. Legacy PBLK and PIIX4 errata behavior is architecture- and hardware-specific.

## Test Signals
Tests should cover Processor object and Device+`_UID` declarations, duplicate IDs including `0xff`, missing MADT UP fallback, `_PCT`/`PCCH` cpufreq device creation, PBLK length handling, `_SUN` package ID update, CPU hot-add and hot-remove, Xen Dom0 presence checks, `_OSC` fallback to `_PDC`, `_CST` malformed packages, FFH and system-I/O C-states, and C-state control claiming.
