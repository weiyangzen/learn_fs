# sources/distributed-fs/ceph-client/arch/m68k/amiga/config.c

Purpose: central Amiga machine setup: bootinfo parsing, hardware detection, machine hook registration, timer/clocksource setup, reset, debug console, heartbeat, and `/proc` hardware reporting.

Important APIs are `amiga_parse_bootinfo()`, `config_amiga()`, private `amiga_identify()`, `amiga_sched_init()`, `amiga_read_clk()`, `amiga_reset()`, `amiga_get_model()`, and `amiga_get_hardware_list()`. It exports key platform state such as `amiga_eclock`, `amiga_colorclock`, `amiga_chipset`, `amiga_vblank`, and `amiga_hw_present`.

Control flow parses bootinfo records for model, clocks, chipset, Chip RAM, vblank, power-supply frequency, and Zorro autoconfig devices, including a Warp 1260 interrupt-storm workaround. `amiga_identify()` derives hardware presence bits from model, chipset registers, and custom chip IDs. `config_amiga()` registers motherboard resources, machine hooks, DMA master state, filters Zorro II memory on Zorro III systems, registers RAM resources, initializes Chip RAM, sound, and magic rekick state.

Timer flow programs CIAB Timer A using `amiga_eclock/HZ`, requests `IRQ_AMIGA_CIAB_TA`, starts the timer, and registers a continuous clocksource. `amiga_read_clk()` carefully reads CIAB timer high/low bytes and accounts for pending interrupts through `cia_set_irq()`.

State includes model name, hardware presence bitmap, resource trees, clock accumulators, savekmsg buffer, debug console write callback, and hardware registers. Reset disables MMU/translation as needed and jumps through Kickstart ROM reset vectors.

Dependencies include bootinfo formats, Amiga custom/CIA/Zorro headers, `chipram.c`, `amisound.c`, `amiints.c`, `cia.c`, generic machdep hooks, and optional heartbeat/input/debug features.

Risks and test signals: hardware probing and model inference are legacy and register-sensitive; timer code depends on CIA semantics; debug memory console steals Chip RAM early. Test with multiple Amiga models, Zorro devices, `debug=mem`/`debug=ser`, `/proc/hardware`, clocksource monotonicity, reboot, and audio/Chip RAM initialization.
