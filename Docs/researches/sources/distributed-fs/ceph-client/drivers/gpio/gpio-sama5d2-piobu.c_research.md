# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sama5d2-piobu.c

## Purpose
This driver exposes the SAMA5D2 SECUMOD PIOBU pins as an eight-line GPIO controller. It uses a syscon regmap for secure-module registers and disables tamper/wakeup detection so pins can be used as ordinary GPIOs.

## Important APIs, Types, and Functions
`struct sama5d2_piobu` contains the gpio chip and syscon regmap. `sama5d2_piobu_setup_pin()` clears the pin's tamper detection bits in backup and normal mode protection registers and clears wakeup participation. `sama5d2_piobu_write_value()` and `sama5d2_piobu_read_value()` access per-pin PIOBU registers. Direction and get/set callbacks translate gpiolib semantics to PIOBU direction, SOD, and PDS bits.

## Control Flow
Probe allocates state, fills an eight-line gpio chip, obtains the regmap from the device node, registers the chip, and then calls setup for every PIOBU line. Direction output writes direction and output state together; get reads PDS for inputs and SOD for outputs.

## State and Persistence
All state is stored in SECUMOD registers through regmap. The driver performs no suspend/resume handling. Initial setup mutates tamper and wakeup configuration persistently for all eight pins.

## Dependencies and Integration Points
The file depends on syscon, regmap, platform DT matching with `atmel,sama5d2-secumod`, and gpiolib. It exposes only GPIO behavior, not IRQ handling.

## Risks
Register setup deliberately disables security/tamper functionality for these pins, so firmware/DT must only bind the driver when GPIO ownership is intended. The chip is registered before per-pin setup; a setup failure returns probe failure but the devm chip registration will unwind. `can_sleep` is set to 0 even though regmap access characteristics depend on the syscon backend.

## Test Signals
Test syscon regmap lookup, all eight per-pin register offsets, input versus output reads, output high/low programming, tamper/wakeup bit clearing, and probe unwind on regmap/setup failures.
