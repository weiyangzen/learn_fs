# sources/distributed-fs/ceph-client/arch/sparc/power/Makefile

Purpose: adds SPARC hibernation objects to the build.

Important APIs/targets: when `CONFIG_HIBERNATION` is enabled, builds `hibernate.o` and `hibernate_asm.o`.

Control flow: kbuild conditionally includes the C state hooks and assembly suspend/resume paths.

State and persistence: no runtime state; affects build composition.

Dependencies and integration points: integrates SPARC64 hibernation support with the generic suspend/hibernate subsystem.

Risks: missing either object leaves unresolved architecture hibernation symbols or incomplete resume support.

Test signals: sparc64 builds with and without `CONFIG_HIBERNATION`, plus link checks for `swsusp_arch_suspend` and `swsusp_arch_resume`.
