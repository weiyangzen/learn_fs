# sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h

Source read summary: 231 lines, 9161 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h` enumerates AST2500, AST2600, and AST2700 watchdog reset-mask bits for peripherals and SoC domains controlled by Aspeed watchdog hardware.

Important APIs, types, and functions: The file exports 208 visible constants or packing macros; representative names are `AST2500_WDT_RESET_CPU`, `AST2500_WDT_RESET_COPROC`, `AST2500_WDT_RESET_SDRAM`, `AST2500_WDT_RESET_AHB`, `AST2500_WDT_RESET_I2C`, `AST2500_WDT_RESET_MAC0`, `AST2500_WDT_RESET_MAC1`, `AST2500_WDT_RESET_GRAPHICS`, `AST2500_WDT_RESET_USB2_HOST_HUB`, `AST2500_WDT_RESET_USB_HOST`, `AST2500_WDT_RESET_HID_EHCI`, `AST2500_WDT_RESET_VIDEO`, `AST2500_WDT_RESET_HAC`, `AST2500_WDT_RESET_LPC`, `AST2500_WDT_RESET_SDIO`, `AST2500_WDT_RESET_MIC` and 192 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Aspeed watchdog device-tree nodes reference these masks to select which blocks are reset on timeout; the watchdog driver writes corresponding hardware reset-mask registers.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The constants are SoC-generation specific. Reusing an AST2500 bit on AST2600/AST2700 hardware, or combining incompatible reset targets, can leave a peripheral out of reset or reset more of the SoC than intended.

Test signals: Compile representative DTS files, compare masks with the SoC datasheet, and exercise watchdog timeout paths on boards where reset scope can be observed.
