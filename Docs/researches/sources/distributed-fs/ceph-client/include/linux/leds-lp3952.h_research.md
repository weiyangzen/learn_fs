# sources/distributed-fs/ceph-client/include/linux/leds-lp3952.h

Purpose: declares register constants and driver-private structures for the TI LP3952 RGB LED controller and pattern generator.

Important APIs and types: register constants cover LED control, blink timing/cycles, enables, pattern generator, current control, command memory, and reset. Bit masks enable pattern loop/generator, boost loader, active mode, and all LEDs. Enums describe transition time, command execution time, max current, and six LED channels plus all-channel sentinel. `struct lp3952_ctrl_hdl` embeds `led_classdev`; `struct ptrn_gen_cmd` packs pattern-generator command bitfields; `struct lp3952_led_array` carries regmap, I2C client, enable GPIO, and channel handlers.

Control flow: the driver maps LED class operations to regmap writes, programs packed pattern commands, toggles enable GPIO, and addresses per-channel handlers through the array.

State and persistence: state is runtime driver state mirrored to LP3952 registers; no durable persistence is defined.

Dependencies and integration points: depends on LED class, regmap, I2C, and GPIO descriptors in the implementation. It integrates the LP3952 chip with LED sysfs/triggers.

Risks and test signals: risks include packed bitfield endianness, register limit drift, channel ordering errors, and enable/reset sequencing. Test per-channel brightness, pattern generation, reset, regmap ranges, and probe/remove cleanup.
