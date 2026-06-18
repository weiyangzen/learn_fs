# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdf2xxx.c

## Purpose
This is an ACPI-only Qualcomm QDF2xxx TLMM client for server-style systems where firmware owns pin muxing. It deliberately exposes only GPIO and GPIO interrupt behavior through the shared MSM pinctrl core, avoiding a static SoC mux table because UEFI is expected to configure pin control. The driver dynamically builds pin and group descriptors from ACPI device properties.

## Important APIs, Types, And Functions
`qdf2xxx_pinctrl_probe()` is the core function. It reads `num-gpios` and a `gpios` byte array from device properties, validates them against `MAX_GPIOS` (256), allocates `struct msm_pinctrl_soc_data`, `struct pinctrl_pin_desc`, `struct msm_pingroup`, and persistent GPIO names with device-managed memory, then calls `msm_pinctrl_probe()`. The generated groups use the same register bit layout as classic MSM TLMM GPIOs: 0x10000-byte GPIO register stride, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and interrupt detection/polarity/target fields.

## Control Flow
At `arch_initcall()` the `qdf2xxx-pinctrl` platform driver is registered. ACPI matching uses the `QCOM8002` ID. Probe first requires a sane total GPIO count, then requires a non-empty approved GPIO list no larger than the total. It initializes all pin numbers and group pin pointers so the array indices remain valid for the MSM core, but only GPIOs named in the `gpios` property receive names, `npins = 1`, register offsets, and GPIO/IRQ bit metadata. Finally it passes the generated SoC data to `msm_pinctrl_probe()`.

## State And Persistence
Unlike the other files in this work item, the SoC data is allocated at probe time and is owned by devres. Names are allocated once because pinctrl/gpiolib store pointers to them. There is no persistent on-disk state and no custom remove path. Hardware state is whatever firmware and later GPIO/IRQ requests program into TLMM registers; the driver does not expose mux functions or pin configuration states beyond GPIO semantics.

## Dependencies And Integration Points
The file depends on ACPI/device-property APIs, platform driver registration, pinctrl descriptors, and `pinctrl-msm.h`. It integrates with firmware through `num-gpios` and `gpios` properties, with gpiolib through the MSM core, and with ACPI enumeration through `QCOM8002`. It intentionally does not use OF matching and does not define static `struct pinfunction` arrays.

## Risks And Test Signals
The main risk is property correctness. If firmware reports too many GPIOs, omits the approved list, or includes GPIO numbers outside the allocated range, probe can fail or write out of bounds; the code validates counts but trusts each `gpios[i]` value to be less than `num_gpios`. Another subtle risk is sparse GPIO exposure: unnamed/unavailable GPIOs still occupy array slots, so consumers must request only approved GPIO numbers. Test signals include ACPI enumeration, missing/invalid property failure messages, successful `gpiochip` registration with the expected sparse lines, GPIO direction/value operations, IRQ configuration from approved GPIOs, and confirmation that no pin mux states are required for boot because firmware already configured them.
