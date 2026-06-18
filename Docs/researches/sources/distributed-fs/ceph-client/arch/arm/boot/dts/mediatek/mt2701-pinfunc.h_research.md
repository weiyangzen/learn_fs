# sources/distributed-fs/ceph-client/arch/arm/boot/dts/mediatek/mt2701-pinfunc.h

Purpose: defines the MediaTek MT2701 pin-function constants consumed by DTS pinctrl nodes. It is a binding header, not executable C code. DTS files include it so `pinmux` cells can name pads and alternate functions instead of embedding raw mux numbers.

Important APIs/types/functions: the exported surface is a large macro set named `MT2701_PIN_<n>_<pad>__FUNC_<function>`. Each value combines `MTK_PIN_NO(n)` from `<dt-bindings/pinctrl/mt65xx.h>` with a mux selector using bitwise OR. Function selector 0 is generally GPIO, while selectors 1 and higher name peripheral functions such as PWRAP SPI, SPI, UART, PCM, I2S, PWM, MSDC, USB, Ethernet, antenna select, debug monitor, and PCIe reset functions. The file has the include guard `__DTS_MT2701_PINFUNC_H`.

Control flow: there is no runtime control flow. The C preprocessor expands these macros while building device trees, and the resulting integer cells are interpreted by the MediaTek pinctrl binding and driver.

State and persistence: no mutable state or persistence exists. The only persisted behavior is the compiled DTB pinmux data emitted from DTS sources that use these constants.

Dependencies and integration: depends on the generic MediaTek `MTK_PIN_NO()` encoding and on DTS pinctrl consumers under the MT2701 SoC tree. Integration points are board `.dts`/`.dtsi` pin groups and the Linux MediaTek pinctrl driver that decodes the encoded pin number and mux mode.

Risks: mistakes are hardware-visible. A wrong alternate function can disconnect boot storage, UART console, clock, interrupt, Ethernet, or reset wiring. The dense hand-maintained macro list also has risk of duplicate or missing pad/function definitions, especially where debug and antenna functions use high mux selectors. Tests should compile all relevant DTBs with `make dtbs`, run `dt_binding_check` for pinctrl users, and boot or smoke-test affected boards with console, storage, networking, and interrupt lines verified.
