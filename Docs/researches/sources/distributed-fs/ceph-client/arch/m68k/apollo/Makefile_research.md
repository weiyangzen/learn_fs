# sources/distributed-fs/ceph-client/arch/m68k/apollo/Makefile

Purpose: Apollo platform object selection.

It builds `config.o` and `dn_ints.o` for the Apollo machine directory. These provide machine setup, timer/RTC/reset/model hooks, and PIC interrupt control.

Control flow is Kbuild-only and depends on the top-level m68k Kbuild including `apollo/` when `CONFIG_APOLLO` is enabled.

State/persistence: no runtime state; object selection determines linked Apollo support.

Risks and test signals: omitting either object leaves unresolved `config_apollo()` dependencies or no IRQ controller. Validate a `CONFIG_APOLLO` build and boot far enough to initialize model setup and IRQs.
