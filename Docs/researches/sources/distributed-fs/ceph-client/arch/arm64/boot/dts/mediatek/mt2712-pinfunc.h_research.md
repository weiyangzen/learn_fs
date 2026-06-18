## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt2712-pinfunc.h

### Purpose
This header is the MediaTek MT2712 pin-function binding catalog. It maps each physical pin and alternate function to the packed value format consumed by MediaTek pinctrl bindings.

### Important APIs, Types, And Functions
There are no functions or local types. The exported API is 902 `MT2712_PIN_*__FUNC_*` macros. Each macro uses `MTK_PIN_NO(n) | function_index`, so the pin number and mux function are encoded in one integer. The file includes `<dt-bindings/pinctrl/mt65xx.h>` for `MTK_PIN_NO`. It covers 210 pins, including EINT, PWM, USB ID/VBUS, keypad, camera clocks, NAND/MSDC/NOR, Ethernet, UART, I2C, SPI, JTAG/debug monitor, PCIe sideband, I2S/TDM/PCM audio, display, and GPIO functions.

### Control Flow
The header has no executable control flow. DTS pinctrl nodes reference these macros; the C preprocessor emits packed pin/function integers; the MediaTek pinctrl driver decodes them and programs mux registers when applying pin states.

### State, Persistence, And Dependencies
The file stores no state. Its packed values persist inside compiled DTBs. Dependencies are the MT65xx pinctrl binding format, the MT2712 pin numbering scheme, the mux function indexes for each pin, and the MediaTek pinctrl driver that interprets `MTK_PIN_NO`.

### Integration Points
Integration points include MT2712 SoC and board DTS files, the MediaTek pinctrl driver, GPIO/EINT infrastructure, and peripheral drivers for MMC, Ethernet, USB, display, camera, serial buses, and audio. Board pinctrl states depend on these names to select the correct mux.

### Risks
The packed format makes both parts of the value important: a wrong pin number or function index can silently mux the wrong signal. Function indexes are sparse on some pins, so assuming all alternate functions are contiguous is unsafe. Debug monitor and boot/storage pins can interfere with bring-up or board recovery if selected accidentally.

### Test Signals
Useful signals include `dtbs_check`, MediaTek pinctrl probe logs, GPIO/EINT interrupt tests, bus-level validation for MMC/NAND/NOR/Ethernet/USB/UART/I2C/SPI/audio/display/camera, and comparison with the MT2712 datasheet mux table. Source reading signal: 1123 lines; 902 `#define` entries; one include; no functions.
