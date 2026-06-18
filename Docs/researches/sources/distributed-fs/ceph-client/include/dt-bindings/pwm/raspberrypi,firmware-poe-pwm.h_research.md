# sources/distributed-fs/ceph-client/include/dt-bindings/pwm/raspberrypi,firmware-poe-pwm.h

Purpose: `raspberrypi,firmware-poe-pwm.h` is a Devicetree binding header for a PWM provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering PWM polarity, channel, or
firmware control constants. The main macro families are RASPBERRYPI (2). Representative constants
are `RASPBERRYPI_FIRMWARE_PWM_POE`, `RASPBERRYPI_FIRMWARE_PWM_NUM`, `RASPBERRYPI_FIRMWARE_PWM_POE`,
`RASPBERRYPI_FIRMWARE_PWM_NUM`. Function-like helpers are none. Value shape: literal numeric range
0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RASPBERRYPI_FIRMWARE_PWM_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RASPBERRYPI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are PWM providers, fan/backlight nodes, and
firmware PWM consumers.

Local source signals: The file is 13 lines long. Notable source comments include none. Example value clusters are
RASPBERRYPI: `RASPBERRYPI_FIRMWARE_PWM_POE=0`, `RASPBERRYPI_FIRMWARE_PWM_NUM=1`.

Risks and test signals: Primary risks are polarity or channel constant drift can invert outputs or address the wrong
firmware PWM endpoint. Pay special attention to exported symbols such as
`RASPBERRYPI_FIRMWARE_PWM_POE`, `RASPBERRYPI_FIRMWARE_PWM_NUM`. Test signals include DTS compile
checks, PWM sysfs/debugfs inspection, fan/backlight behavior, and polarity regression tests.
