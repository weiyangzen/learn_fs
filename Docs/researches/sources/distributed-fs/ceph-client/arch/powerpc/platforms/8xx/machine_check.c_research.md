# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c

### Purpose
MPC8xx machine-check exception handling.

### Important APIs, Types, And Functions
Defines `machine_check_8xx(struct pt_regs *regs)`. It inspects exception state, reports machine-check details, and decides recovery/fatal behavior according to PowerPC exception conventions.

### Control Flow
The PowerPC exception path calls this handler when an 8xx machine check occurs. It runs in exception context and returns a status to the core exception handling code.

### State, Persistence, And Dependencies
State is CPU exception register content in `pt_regs` and any diagnostic output. No durable persistence. Dependencies include PowerPC exception types and low-level register definitions.

### Integration Points
Wired through 8xx machine definitions or architecture exception tables to handle hardware faults.

### Risks
Exception-context code cannot sleep and must avoid unsafe operations. Returning the wrong recovery status can hide fatal hardware errors or unnecessarily panic.

### Test Signals
Inject or emulate machine-check conditions, verify diagnostics and expected panic/recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c -->
