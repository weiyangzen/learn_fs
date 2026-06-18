# sources/distributed-fs/ceph-client/arch/m68k/atari/atari.h

Purpose: local Atari machine support prototypes.

It declares `atari_init_IRQ()`, `atari_microwire_cmd()`, `atari_mksound()`, `atari_sched_init()`, `atari_mste_hwclk()`, and `atari_tt_hwclk()`. It forward-declares `struct rtc_time`.

State/persistence: none in the header. The functions it declares mutate IRQ controller, sound, timer, and RTC hardware state.

Dependencies and integration: used by Atari `config.c`, `ataints.c`, `atasound.c`, and `time.c` to avoid broader architecture header coupling.

Risks and test signals: prototype drift is caught by compilation. Runtime coverage comes from Atari boot with IRQ, beep, and RTC paths enabled.
