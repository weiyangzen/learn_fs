## sources/distributed-fs/ceph-client/drivers/acpi/riscv/cpuidle.c

### Purpose
`riscv/cpuidle.c` provides RISC-V ACPI FFH LPI validation and entry hooks for the generic ACPI processor idle driver.

### Important APIs, Types, And Functions
The public hooks are `acpi_processor_ffh_lpi_probe()` and `acpi_processor_ffh_lpi_enter()`. `acpi_cpu_init_idle()` validates all nonzero LPI states for a CPU.

### Control Flow
Probe retrieves the per-CPU ACPI processor, requires `_LPI` state data, requires SBI HSM support, requires more than the baseline state, then validates each state address against the RISC-V FFH encoding: type bits must indicate SBI, reserved bits must be zero, and the low 32-bit SBI power state must be valid. Entry chooses retention or non-retention CPU PM wrappers based on `SBI_HSM_SUSP_NON_RET_BIT` and calls `riscv_sbi_hart_suspend()`.

### State, Persistence, And Dependencies
There is no retained state. Dependencies include ACPI processor LPI data, SBI HSM suspend support, CPU PM idle wrappers, and RISC-V suspend helpers.

### Integration Points
`processor_idle.c` calls these functions from LPI discovery and idle entry when ACPI `_LPI` states use fixed hardware methods on RISC-V.

### Risks
Any invalid LPI address disables the ACPI LPI path for that CPU. The address is a 64-bit ACPI field but the SBI state is truncated to 32 bits after validation. Entry assumes the generic idle layer selected an already-validated LPI state.

### Test Signals
Test absent processor data, no SBI HSM, single-state `_LPI`, invalid type bits, nonzero reserved bits, invalid SBI power states, retention and non-retention entry, and interaction with suspend-to-idle.
