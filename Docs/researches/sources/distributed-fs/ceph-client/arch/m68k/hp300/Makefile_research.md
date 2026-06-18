# sources/distributed-fs/ceph-client/arch/m68k/hp300/Makefile

Purpose: declares the HP300 platform objects built into the m68k kernel subtree.

Important APIs/types/functions: `obj-y := config.o time.o reboot.o` includes HP300 machine setup, timer/clocksource code, and reset stub in the built-in object list.

Control flow: build-system only. Kbuild descends into the directory and links the listed objects when HP300 support is selected by the surrounding architecture configuration.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrates with Linux Kbuild and the HP300 source files in the same directory. Any source added to HP300 machine support must be reflected here to participate in the build.

Risks: omitting an object would produce missing machine hooks or link failures; adding the wrong object could pull platform code into incompatible builds.

Test signals: HP300 kernel configuration builds, link includes `config.o`, `time.o`, and `reboot.o`, and machine boot reaches `config_hp300` and `hp300_sched_init`.
