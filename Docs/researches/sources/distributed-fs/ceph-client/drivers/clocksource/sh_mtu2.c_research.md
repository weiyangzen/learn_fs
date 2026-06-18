# sources/distributed-fs/ceph-client/drivers/clocksource/sh_mtu2.c

Purpose: supports the SuperH/Renesas MTU2 block as a periodic clockevent provider. Unlike CMT and TMU, this driver does not register a clocksource.

Important APIs, types, and functions: `struct sh_mtu2_device` stores platform device, mapped base, `fck`, shared-register lock, channels, and clockevent availability. `struct sh_mtu2_channel` stores channel base and embedded clockevent. Important paths are `sh_mtu2_read()/write()`, `sh_mtu2_start_stop_ch()`, `sh_mtu2_enable()`, `sh_mtu2_disable()`, `sh_mtu2_interrupt()`, clockevent state callbacks, `sh_mtu2_setup_channel()`, and `sh_mtu2_probe()`.

Control flow: probe handles early-platform retention, enables runtime PM, allocates the device, prepares the functional clock, maps registers, counts IRQs, allocates channel structures, and for each channel tries to find a named IRQ like `tgi0a`. Channels without declared interrupts are skipped. Enabling a channel gets runtime PM, marks the device as syscore, enables the clock, stops the channel, computes a periodic period at clock/64, programs TGRA compare-match clear mode, enables TGRA interrupts, and starts the channel. The ISR acknowledges TGFA and dispatches the clockevent handler.

State and persistence: state is in the device/channel structs, prepared clock, runtime PM/syscore state, shared TSTR bits, and channel registers. There is no persistent storage and no clocksource state.

Dependencies and integration points: uses platform/OF matching, named platform IRQs, common clock framework, runtime PM/genpd, early platform timer hooks on SuperH, and clockevent registration.

Risks: only periodic mode is implemented; callers expecting one-shot behavior need another timer. Named IRQ resources must match `tgi%ua`. The shared start/stop register is protected by a raw spinlock and must remain synchronized across channels. Test signals include periodic tick delivery, correct clock/64 period, clean skip of channels without IRQs, runtime PM transitions, and earlytimer retention.
