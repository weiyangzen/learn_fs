<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c

### Purpose
`mips-mt.c` provides general MIPS MT configuration support. It parses boot options limiting VPEs/TCs, overriding 34K Config7 behavior, and mapping the Inter-Thread Communication block, then registers the MT sysfs class.

### Important APIs, Types, And Functions
Public globals are `vpelimit`, `tclimit`, and `mt_class`. Important functions are `mips_mt_set_cpuoptions()` and init parsers for `maxvpes=`, `maxtcs=`, `rpsctl=`, `nblsu=`, `config7=`, and `itcbase=`.

### Control Flow
Boot option parsers store requested limits or override values. `mips_mt_set_cpuoptions()` reads CP0 Config7, applies return prediction stack and ALU/LSU sync overrides, optionally forces the full Config7 value, writes it with `sync` and `ehb`, then optionally enables ITC register access through ErrCtl and programs ITC granularity/base using cache tag operations. `mips_mt_init()` registers the `mt` class at `subsys_initcall`.

### State, Persistence, And Dependencies
State includes boot-option globals, CP0 Config7, ErrCtl, DTagLo, ITC control state, and sysfs class registration. Dependencies include MIPS MT CP0 register access, cache ops, CPU feature setup, and Linux device class infrastructure.

### Integration Points
The code is used by MIPS MT CPU setup, VPE/TC management, board-specific MT initialization, and userspace-visible MT class devices.

### Risks
Config7 and ITC programming are hardware-specific and can destabilize CPUs if wrong values are forced. `itcbase=` assumes 34K-specific cache tag control paths. Boot options bypass conservative defaults, so they are powerful diagnostics but risky production knobs.

### Test Signals
Boot with each MT option, inspect Config7 logs, verify VPE/TC limits, validate ITC mapping on 34K-family hardware, check `/sys/class/mt`, and run SMP/SMVP scheduling and interrupt tests after overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c -->
