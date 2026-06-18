# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/Makefile

Purpose: selects the x86 MTRR implementation objects built into the kernel.

Important APIs/types/functions: builds `mtrr.o`, `if.o`, `generic.o`, and `cleanup.o` unconditionally for this directory. Adds `amd.o`, `cyrix.o`, `centaur.o`, and `legacy.o` only when `CONFIG_X86_32` is enabled.

Control flow: no runtime control flow. Kbuild evaluates `obj-y` and `obj-$(CONFIG_X86_32)` to decide which objects are linked.

State and persistence: no runtime state. The only persistent effect is build output selection.

Dependencies and integration points: integrates with Kbuild and the MTRR source files in the same directory. The 32-bit-only objects implement legacy CPU-specific MTRR-like interfaces and suspend/resume handling for non-generic CPUs.

Risks: moving an object between unconditional and `CONFIG_X86_32` changes symbol availability. Generic MTRR code must remain available for 64-bit, while legacy AMD K6/Cyrix/Centaur code must not be linked where its CPU access mechanisms are invalid.

Test signals: build 32-bit and 64-bit x86 configurations, with and without generic MTRR support, and confirm expected object inclusion through build logs or `nm`.
