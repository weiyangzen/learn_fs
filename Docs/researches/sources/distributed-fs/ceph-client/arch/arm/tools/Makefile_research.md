## sources/distributed-fs/ceph-client/arch/arm/tools/Makefile

### Purpose
Generates ARM architecture headers and syscall assembly tables used by kernel and UAPI builds.

### Important APIs, Types, And Functions
Build targets include generated `calls-oabi.S`, `calls-eabi.S`, `unistd-nr.h`, `mach-types.h`, `unistd-oabi.h`, and `unistd-eabi.h`. Commands wrap `gen-mach-types`, `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, and `syscallnr.sh`.

### Control Flow
`kapi` depends on generated kernel headers and syscall tables; `uapi` depends on generated user ABI headers. Kbuild creates output directories, then invokes AWK or shell scripts through `if_changed` rules so outputs regenerate when inputs or commands change.

### State, Persistence, And Dependencies
State is generated files under `arch/$(ARCH)/include/generated`. Inputs are `mach-types`, `syscall.tbl`, generic syscall scripts, and Kbuild variables such as `ARCH`, `src`, `srctree`, and `CONFIG_SHELL`.

### Integration Points
Feeds ARM syscall numbering, OABI/EABI entry tables, and machine-type helpers into the rest of the ARM build.

### Risks
Generated UAPI header drift is ABI-sensitive. Missing directory creation or stale `if_changed` dependencies can leave obsolete syscall counts or machine IDs in builds.

### Test Signals
Run `make ARCH=arm archprepare`, inspect generated headers, and compare syscall table output after syscall additions.
