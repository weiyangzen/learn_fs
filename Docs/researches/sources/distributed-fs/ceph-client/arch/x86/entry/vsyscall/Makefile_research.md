## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/Makefile

Purpose: Kbuild rules for legacy x86-64 vsyscall support.

Important build object: `obj-$(CONFIG_X86_VSYSCALL_EMULATION) += vsyscall_64.o vsyscall_emu_64.o`.

Control flow: builds the C emulator and assembly emulation page only when legacy vsyscall emulation support is configured.

State/persistence: produces kernel objects that map/emulate the fixed vsyscall ABI page.

Integration points: x86 entry page-fault/general-protection handling, fixed mappings, legacy userspace ABI, and Kconfig selection.

Risks: omitting either object breaks configured emulation. Test signals include builds with vsyscall enabled/disabled and runtime `vsyscall=` boot mode tests.
