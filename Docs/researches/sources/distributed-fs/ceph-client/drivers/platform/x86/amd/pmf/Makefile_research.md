# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Makefile

Purpose: this Makefile builds the AMD PMF composite object.

Important APIs, types, and functions: `amd-pmf-y` contains `core.o`, `acpi.o`, `sps.o`, `auto-mode.o`, `cnqf.o`, `tee-if.o`, and `spc.o`.

Control flow: kbuild links all PMF feature layers into one module/object when `CONFIG_AMD_PMF` is enabled.

State and persistence: build-only state.

Dependencies and integration points: the object list reflects PMF layering: core lifecycle/SMU, ACPI method interface, static slider, auto mode, CnQF dynamic slider, TEE policy engine, and Smart PC input collection.

Risks: all layers are linked together, so Kconfig dependencies must satisfy every source file even if a platform uses only a subset of PMF features.

Test signals: successful composite build and expected `MODULE_SOFTDEP("pre: amdtee")` behavior from the core module.
