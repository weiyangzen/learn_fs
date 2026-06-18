## sources/distributed-fs/ceph-client/drivers/acpi/processor_pdc.c

### Purpose
`processor_pdc.c` performs the ACPI `_PDC` processor-driver-capabilities handshake so firmware can expose modern processor power and performance features.

### Important APIs, Types, And Functions
The main public functions are `acpi_processor_set_pdc()` and early boot `acpi_early_processor_set_pdc()`. Internals are `acpi_set_pdc_bits()`, `acpi_processor_alloc_pdc()`, `acpi_processor_eval_pdc()`, and the namespace walker callback `early_init_pdc()`.

### Control Flow
The early init path runs `acpi_proc_quirk_mwait_check()`, walks legacy `Processor` objects and processor device HID objects, skips objects not physically present, allocates a one-element ACPI object list containing a 12-byte buffer, sets revision/count/capability bits, lets the architecture fill capability bits, evaluates `_PDC`, and frees all temporary allocations.

### State, Persistence, And Dependencies
There is no retained state in this file. The persistent effect is firmware state changed by `_PDC`. Dependencies are ACPI namespace walks, object evaluation, processor presence checks, and architecture hooks `arch_has_acpi_pdc()` and `arch_acpi_set_proc_cap_bits()`.

### Integration Points
The handshake happens early enough to affect later processor `_CST`, `_PSS`, `_PCT`, CPPC, and idle/performance feature exposure. It is shared by all architectures that implement the arch capability hooks.

### Risks
Allocation failure silently skips the handshake after logging. `_PDC` failure falls back to legacy performance control. Incorrect architecture capability bits can cause firmware to expose unsupported paths or hide needed ones. The early walker covers both processor object models and must avoid absent hotplug targets.

### Test Signals
Check systems with and without `_PDC`, architecture hook disabled, allocation-failure injection, physically absent processor namespace objects, duplicate Processor/HID coverage, and firmware behavior changes in subsequent C/P-state methods after `_PDC`.
