## sources/distributed-fs/ceph-client/drivers/acpi/riscv/cppc.c

### Purpose
`riscv/cppc.c` implements RISC-V CPPC fixed-hardware accessors used by the generic ACPI CPPC library. It supports FFH register encodings backed by SBI CPPC calls and a limited CSR path.

### Important APIs, Types, And Functions
The exported architecture hooks are `cpc_ffh_supported()`, `cpc_read_ffh()`, and `cpc_write_ffh()`. Internal helpers include `sbi_cppc_init()`, `sbi_cppc_read()`, `sbi_cppc_write()`, `cppc_ffh_csr_read()`, and `cppc_ffh_csr_write()`. `struct sbi_cppc_data` carries the register, value, and SBI return.

### Control Flow
At device init, the file probes SBI version and the CPPC extension. Reads and writes reject IRQ-disabled callers, decode the FFH type from the ACPI CPPC register address, and execute the operation on the target CPU using `smp_call_function_single()`. SBI reads/writes call `sbi_ecall()` and map SBI errors to Linux errno. CSR reads currently support only `CSR_TIME`; CSR writes always fail with `-EINVAL`.

### State, Persistence, And Dependencies
The retained state is `cppc_ext_present`. Dependencies include ACPI CPPC register definitions, RISC-V SBI probing/ecalls, CSR accessors, SMP cross-calls, and Linux errno mapping.

### Integration Points
Generic `drivers/acpi/cppc_acpi.c` calls these hooks when CPPC register descriptors use fixed hardware space on RISC-V. `processor_driver.c` indirectly depends on this through `acpi_cppc_processor_probe()`.

### Risks
Calls require interrupts enabled because they send synchronous IPIs. SBI CPPC support is only available with SBI spec 2.0 or later plus extension presence. CSR support is intentionally narrow. Data is stack-local but passed synchronously to the target CPU, so the blocking cross-call is required.

### Test Signals
Test SBI-present and absent systems, reads/writes to SBI-encoded CPPC registers, CSR TIME reads, unsupported CSR writes, unknown FFH type, IRQ-disabled warnings, target CPU offline behavior, and SBI error mapping.
