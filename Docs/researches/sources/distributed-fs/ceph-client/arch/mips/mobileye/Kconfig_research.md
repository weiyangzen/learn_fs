<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig

### Purpose
`mobileye/Kconfig` defines MIPS Mobileye EyeQ SoC selection and optional FIT image FDT inclusion for EyeQ5 development boards.

### Important APIs, Types, And Functions
The file is Kconfig data, not C code. Symbols are `MACH_EYEQ5`, `MACH_EYEQ6H`, `MACH_EYEQ6LPLUS`, and `FIT_IMAGE_FDT_EPM5`.

### Control Flow
When `EYEQ` is enabled, Kconfig presents a choice with EyeQ5 as default. `FIT_IMAGE_FDT_EPM5` is available only for `MACH_EYEQ5` and controls embedding the EPM5 FDT into the FIT kernel image.

### State, Persistence, And Dependencies
State is the generated kernel `.config`. Dependencies include the parent `EYEQ` platform symbol and downstream build rules that consume `FIT_IMAGE_FDT_EPM5`.

### Integration Points
The symbols feed Mobileye platform compilation and FIT image assembly in the MIPS boot path.

### Risks
Only EyeQ5 has a selectable embedded EPM5 FDT option here. A mismatched SoC choice can select wrong platform support. The help text assumes U-Boot FIT boot flow.

### Test Signals
Run Kconfig selection for each EyeQ SoC, verify default choice behavior, and build EyeQ5 with and without `FIT_IMAGE_FDT_EPM5`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig -->
