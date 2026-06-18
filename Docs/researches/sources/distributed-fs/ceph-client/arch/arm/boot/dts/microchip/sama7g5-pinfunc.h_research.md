# sources/distributed-fs/ceph-client/arch/arm/boot/dts/microchip/sama7g5-pinfunc.h

Purpose: SAMA7G5 pinmux binding header. It supplies DTS-readable pin/function constants for PA0 through PE7, around 136 pins, including the SAMA7G5 multimedia, networking, storage, serial, timer, and audio pin matrix.

Important APIs/types/functions: `PINMUX_PIN(no, func, ioset)` encodes pin, mux function, and IO set into one cell. Exported macros include `PIN_Pxx` base pin numbers and `PIN_Pxx__GPIO`/`PIN_Pxx__<function>` alternatives for SDMMC, FLEXCOM, CAN, PDMC, G0/G1 Ethernet, EBI/NAND, SPDIF, ISC, LCDC, I2SMCC, PWM, TCB timers, PCK, TWI, SPI, and IRQ functions.

Control flow: no runtime code exists. The C preprocessor expands named constants into numeric DTB cells; pinctrl core and the Microchip driver apply the hardware register programming later.

State and persistence: the header is stateless. Persistent behavior comes from board DTBs selecting these macros in pinctrl groups.

Dependencies and integration: used by SAMA7G5 `.dtsi` and board files, and interpreted according to Microchip pinctrl bindings. Its macro encoding must remain aligned with driver expectations. The file has no include guard, matching the DTS binding-header style used by neighboring Microchip pinfunc files.

Risks: the main risk is board misconfiguration through a plausible but wrong alternate function or IO set. Multimedia and Ethernet pins are especially sensitive because many functions share PE and PA banks. Since the values are plain constants, review must compare against the SoC pin table, not just rely on build success. Tests are DTB compilation, `dt_binding_check`, and hardware validation of boot storage, console, Ethernet, audio, display, camera, CAN, and any modified FLEXCOM instance.
