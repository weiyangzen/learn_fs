# sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h

### Purpose
`lsui.h` provides ARM64 Load/Store Unprivileged instruction helpers or feature gating for access patterns that need unprivileged load/store semantics.

### Important APIs, Types, And Functions
It is a small include-time contract defining LSUI-related macros and conditional assembly/compiler hooks.

### Control Flow
Consumers expand the macros inline where unprivileged memory access sequences are needed. Runtime behavior is selected by CPU feature and compiler/assembler support.

### State, Persistence, And Dependencies
There is no owned state. It depends on ARM64 instruction availability and low-level access helper infrastructure.

### Integration Points
Potential consumers include user access, exception-table protected memory access, or architecture-specific probing paths.

### Risks
Executing unsupported unprivileged load/store instructions or missing exception-table coverage can fault in sensitive contexts.

### Test Signals
Cross-build with relevant CPU feature configs; run usercopy and fault-injection tests that exercise unprivileged accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lsui.h -->
