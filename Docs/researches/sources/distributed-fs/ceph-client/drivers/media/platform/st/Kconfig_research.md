# sources/distributed-fs/ceph-client/drivers/media/platform/st/Kconfig

Purpose: introduces the STMicroelectronics media platform driver submenu and sources the ST platform Kconfig fragments.

Important APIs and symbols: emits a Kconfig `comment` and sources `drivers/media/platform/st/sti/Kconfig` plus `drivers/media/platform/st/stm32/Kconfig`.

Control flow: when the media platform Kconfig tree is evaluated, this file delegates actual driver symbols to the STI and STM32 subtrees.

State and persistence: no runtime state. Selected symbols persist only in kernel configuration.

Dependencies and integration points: integrates the ST platform directory with the wider Linux media Kconfig hierarchy.

Risks: incorrect source paths would hide all ST platform driver options. The file itself defines no guards or dependencies, so subtrees must own symbol constraints.

Test signals: `menuconfig` visibility under media platform drivers and allmodconfig/allnoconfig parse coverage.
