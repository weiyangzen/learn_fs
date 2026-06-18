# sources/distributed-fs/ceph-client/arch/sparc/math-emu/Makefile

Purpose: builds the SPARC floating-point emulation object for the selected word size.

Important APIs/functions: `ccflags-y := -w` suppresses warnings for the emulation source, and `obj-y := math_$(BITS).o` selects `math_32.o` or `math_64.o` according to the architecture build variable.

Control flow: Kbuild includes exactly one object based on `BITS`; there is no conditional list beyond that.

State and persistence: no runtime state. Build-time state is limited to compiler flags and object selection.

Dependencies/integration: depends on architecture Kbuild defining `BITS`. Integrates the math emulator into the SPARC kernel image when this directory is built.

Risks: global warning suppression can hide real regressions in the emulation code. Wrong `BITS` propagation would build the incompatible dispatcher and register layout.

Test signals: build both sparc32 and sparc64 configurations and verify the expected object appears in link maps. A warning-enabled local build is useful for catching latent type issues despite `-w`.
